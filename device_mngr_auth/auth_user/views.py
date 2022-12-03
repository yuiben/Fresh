import codecs
import csv
import os

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.forms.models import model_to_dict
from django.utils.encoding import smart_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from linebot import LineBotApi, WebhookHandler
from rest_framework import generics, status, permissions
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.decorators import parser_classes
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveAPIView
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from device_mngr_auth.auth_user.serializers import (
    AuthLoginSerializer,
    SendPasswordResetEmailSerializer,
    UserChangePasswordSerializer,
    UserResetPasswordSerializer,
    UserProfileSerializer,
    LoginSerializer,
    UserSerializer,
    SoftDeleteUserSerializer,
    UserCreateSerializer,
    UserProfileCreateSerializer,
)
from device_mngr_auth.common.exceptions import CheckTokenException, InvalidPasswordException, UserNotFoundException
from device_mngr_auth.common.paginators import CustomPagination
from device_mngr_auth.common.sendmail import send_email_to_user
from device_mngr_auth.common.validate import validate_date_of_birth, validate_password, validate_phone_number
from .permissions import IsAdminUser
from ..core.models.borrow import Borrow
from ..core.models.users import UserProfile, DMAUser

FE_URL = os.environ.get('FE_URL')

line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))


@extend_schema(responses={200: {}}, methods=['GET'], )
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny, ])
@csrf_exempt
def callback(request):
    print(request.GET)
    # status_friend = request.GET['friendship_status_changed']

    # if status_friend:
    #     r = requests.get('https://1569-2405-4802-7006-2c40-cd42-bc3c-1ee6-9764.ap.ngrok.io/api/v1/list-user/')
    # else:
    #     r = requests.get('https://1569-2405-4802-7006-2c40-cd42-bc3c-1ee6-9764.ap.ngrok.io/api/v1/add-tracking-line/')
    # return Response('Could not save data')
    # send_json = json.loads(request.body)
    # reply_token = send_json['events'][0]['replyToken']
    # user_id = send_json['events'][0]['source']['userId']
    # # line_bot_api.reply_message(reply_token, TextSendMessage(text='Hello World!'))
    # try:
    #     profile = line_bot_api.get_profile(user_id='U0fb11ef46062a25ed4e78cd9665ecef5')
    # except LineBotApiError as e:
    #     return Response(e.message)
    return Response(request.GET)


@extend_schema(request=AuthLoginSerializer, responses={200: {}}, methods=['POST'], )
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def auth_login_view(request):
    auth_serializer = AuthLoginSerializer(data=request.data)
    auth_serializer.is_valid()
    token = auth_serializer.authenticate()
    return Response(token, 200)


@extend_schema(request=None, responses={200: {}}, methods=['POST'], )
@api_view(["POST"])
def auth_verify_token_view(request):
    return Response(request.user, 200)


@extend_schema(request=SoftDeleteUserSerializer, responses=None, methods=['POST'])
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated, IsAdminUser, ])
def soft_delete_user(request):
    serializer = SoftDeleteUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.delete(serializer.data)
    return Response({
        'status': 200,
        'message': 'Soft delete success'}, status=status.HTTP_200_OK)


@extend_schema(request=SoftDeleteUserSerializer, responses=None, methods=['PUT'])
@api_view(["PUT"])
@permission_classes([permissions.IsAuthenticated, IsAdminUser, ])
def restore_user(request):
    serializer = SoftDeleteUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.update(serializer.data)
    return Response({
        'status': 200,
        'message': 'Restore delete success'}, status=status.HTTP_200_OK)


fs = FileSystemStorage(location='tmp/')


@extend_schema(responses=None, methods=['POST'])
@api_view(["POST"])
@parser_classes([MultiPartParser])
@permission_classes([permissions.IsAuthenticated, IsAdminUser, ])
def upload_data(request, format=None):
    file = request.FILES["file"]
    content = file.read()
    file_content = ContentFile(content)
    file_name = fs.save(
        "_tmp.csv", file_content
    )
    tmp_file = fs.path(file_name)
    reader = csv.DictReader(codecs.iterdecode(file, "utf-8"), delimiter=',')
    data = list(reader)
    print(data)

    user_list = []
    profile_list = []
    for row in data:
        user_list.append(
            DMAUser(
                email=row['email'],
                name=row['name'],
                role=row['role']
            )
        )
        profile_list.append(
            UserProfile(
                first_name=row['first_name'],
                last_name=row['last_name'],
                phone_number=row['phone_number'],
                date_of_birth=row['date_of_birth'],
                position_id=row['position']
            )
        )

    for index, value in enumerate(user_list):
        user = DMAUser.objects.create(email=value.email, name=value.name, role=value.role)
        profile_list[index].user = user
        a = model_to_dict(profile_list[index])
        print(a)
        UserProfile.objects.create(**a)

    return Response("Success")


@api_view(['POST'])
@parser_classes([JSONParser])
def example_view(request, format=None):
    """
    A view that can accept POST requests with JSON content.
    """
    return Response({'received data': request.data})


class ListCreateUserAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = UserCreateSerializer

    def get(self, request):
        paginator = CustomPagination()
        user = DMAUser.objects.all()

        for key, value in self.request.query_params.items():
            if key == 'name':
                user = user.filter(name__icontains=value)
                break

            if key == 'deleted_at':
                if value == "1" or value == "0":
                    user = user.filter(deleted_at__isnull=bool(int(value)))
                    continue
                return Response({
                    'status': 400,
                    'message': 'Deleted_at param Error'}, status=status.HTTP_400_BAD_REQUEST)

            if key == 'position':
                try:
                    profile = UserProfile.objects.filter(position=value)
                    user = user.filter(id__in=profile)
                    continue
                except ValueError:
                    return Response({
                        'status': 400,
                        'message': 'Position param Error'}, status=status.HTTP_400_BAD_REQUEST)

        result_page = paginator.paginate_queryset(user, request)

        pserializer = UserSerializer(result_page, many=True)

        return paginator.get_paginated_response(pserializer.data)

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'status': 201,
            'message': 'success',
            'data': serializer.data}, status=status.HTTP_201_CREATED)


class UserDetailAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsAdminUser,)
    serializer_class = UserCreateSerializer

    def get_object(self, pk):
        try:
            return DMAUser.objects.get(pk=pk)
        except DMAUser.DoesNotExist:
            raise UserNotFoundException()

    def get(self, request, pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user)
        return Response({
            'status': 200,
            'message': 'success',
            'data': serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        user = self.get_object(pk)
        profile_data = request.data.pop('profile')

        serializer = self.serializer_class(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        profile = UserProfile.objects.get(pk=pk)
        serializer_profile = UserProfileCreateSerializer(profile, data=profile_data)
        serializer_profile.is_valid(raise_exception=True)

        serializer.save()
        serializer_profile.save()
        return Response({
            'status': 200,
            'message': 'Update User Succes'}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        user_borrow = Borrow.objects.filter(user_id=pk, deleted_at=None)
        if len(user_borrow) != 0:
            raise UserNotFoundException({
                'status': 400,
                'message': f'Can\'t continue because user borrow id {pk} is borrowing the product'},
                status=status.HTTP_400_BAD_REQUEST)
        user = self.get_object(pk)
        user.delete()
        return Response({
            'status': 204,
            'message': 'Delete User Succes'}, status=status.HTTP_204_NO_CONTENT)


class LoginAPIView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class AuthUserAPIView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response({
            'status': 200,
            'message': 'success',
            'data': serializer.data}, status=status.HTTP_200_OK)


class AuthAdminAPIView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        user = request.user
        if user.role == 1:
            serializer = self.serializer_class(user)
            return Response({
                'status': 200,
                'message': 'success',
                'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 403,
                'message': 'You do not have permission to use this action !'}, status=status.HTTP_403_FORBIDDEN)


class UserProfileDetail(RetrieveAPIView):
    """
    Read profile user
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer
    parser_classes = (MultiPartParser, JSONParser,
                      FormParser, FileUploadParser)

    def get_object(self, request):
        profile = UserProfile.objects.get(user=request.user)
        if profile is None:
            return Response({
                'status': 404,
                'message': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return profile

    def get(self, request):
        user_profile = self.get_object(request)
        serializer = self.serializer_class(user_profile)
        response = {
            'status': 200,
            'message': 'success',
            'data': {
                'user_id': request.user.id,
                'name': request.user.name,
                'email': request.user.email,
                'code': request.user.code,
                'profile': serializer.data
            },
        }
        return Response(response, status=status.HTTP_200_OK)

    def put(self, request):
        user_profile = self.get_object(request)
        serializer = UserProfileSerializer(user_profile, data=request.data)
        if serializer.is_valid(raise_exception=True):
            date_of_birth = request.data.get("date_of_birth")
            validate_date_of_birth(date_of_birth)
            phone_number = request.data.get("phone_number")
            validate_phone_number(phone_number)
            serializer.save()
            response = {
                'status': 200,
                'message': 'Update profile success',
                'data': {
                    'user_id': request.user.id,
                    'name': request.user.name,
                    'email': request.user.email,
                    'code': request.user.code,
                    'profile': serializer.data
                },
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response({
            'status': 400,
            'message': serializer.errors}, status.HTTP_400_BAD_REQUEST)


class UserChangePasswordView(generics.GenericAPIView):
    """
    Change password
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserChangePasswordSerializer
    model = DMAUser

    def post(self, request):
        self.object = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not self.object.check_password(serializer.data.get("old_password")):
            response = {
                "status": 400,
                "message": "Wrong password",
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")
        validate_password(new_password)
        validate_password(confirm_password)
        self.object.set_password(confirm_password)
        self.object.save()
        response = {
            'status': 200,
            'message': 'Change password successfully',
            'data': {
                'user_id': self.request.user.id
            }
        }
        return Response(response, status=status.HTTP_200_OK)


class SendPasswordResetEmailView(APIView):
    """
    Forgot password
    """
    permission_classes = (AllowAny,)
    serializer_class = SendPasswordResetEmailSerializer

    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = DMAUser.objects.get(email=request.data.get('email'))
            if user.deleted_at != None:
                raise NotFound('The account no longer exists!!')
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            url_reset_password = f'{FE_URL}/new-password?uid=' + \
                                 uid + '&token=' + token
            # send mail
            send_email_to_user(to_email=user.email, user_data=dict(
                user=user, code=token, url_reset_password=f'{url_reset_password}'))
            response = {
                'status': 200,
                'message': 'Email sent. Please check your email',
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordResetView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = UserResetPasswordSerializer

    def post(self, request, uid, token, format=None):
        serializer = UserResetPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            id = smart_str(urlsafe_base64_decode(uid))
            user = DMAUser.objects.get(id=id)
            CheckTokenException().check_token(user, token)
            new_password = request.data.get("new_password")
            try:
                validate_password(new_password)
            except InvalidPasswordException:
                return Response({"status": 400, "message": "Validate Password Wrong"},
                                status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            user.save()
            response = {
                'status': 200,
                'message': 'Password reset successfully',
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
