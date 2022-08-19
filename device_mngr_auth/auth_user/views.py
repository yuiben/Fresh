from datetime import datetime, date
from xml.dom import ValidationErr
import os
from drf_spectacular.utils import extend_schema

from rest_framework import generics, status, permissions
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser, FileUploadParser
from rest_framework.exceptions import NotFound

from device_mngr_auth.common.validate import validate_date_of_birth, validate_password, validate_phone_number
from device_mngr_auth.auth_user.models import DMAUser, UserProfile
from device_mngr_auth.borrow.models import Borrow
from device_mngr_auth.common.paginators import CustomPagination
from device_mngr_auth.common.exceptions import CheckTokenException, InvalidPasswordException, UserNotFoundException
from .permissions import IsAdminUser

from django.utils.encoding import smart_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from device_mngr_auth.common.sendmail import send_email_to_user

from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

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
)

FE_URL = os.environ.get('FE_URL')


@extend_schema(request=AuthLoginSerializer, responses={200: {}}, methods=['POST'],)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def auth_login_view(request):
    auth_serializer = AuthLoginSerializer(data=request.data)
    auth_serializer.is_valid()
    token = auth_serializer.authenticate()
    return Response(token, 200)


@extend_schema(request=None, responses={200: {}}, methods=['POST'],)
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
    return Response({'status': 200, 'message': 'Soft delete success'})


class ListCreateUserAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsAdminUser, )
    serializer_class = UserSerializer

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
                return Response({'status': 400, 'message': 'Deleted_at param Error'})

            if key == 'position':
                try:
                    profile = UserProfile.objects.filter(position=value)
                    user = user.filter(id__in=profile)
                    continue
                except ValueError:
                    return Response({'status': 400, 'message': 'Position param Error'})

        result_page = paginator.paginate_queryset(user, request)

        pserializer = self.serializer_class(result_page, many=True)

        return paginator.get_paginated_response(pserializer.data)

    @extend_schema(request=UserCreateSerializer, responses=None, methods=['POST'])
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'status': 201, 'message': 'succes', 'data': serializer.data},
            status=status.HTTP_201_CREATED)


class UserDetailAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsAdminUser,)
    serializer_class = UserSerializer

    def get_object(self, pk):
        try:
            return DMAUser.objects.get(pk=pk)
        except DMAUser.DoesNotExist:
            raise UserNotFoundException()

    def get(self, request, pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        user = self.get_object(pk)
        serializer = UserCreateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 204, 'message': 'Update User Succes'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user_borrow = Borrow.objects.filter(user_id=pk, deleted_at=None)
        if len(user_borrow) != 0:
            raise UserNotFoundException(
                {'status': 400, 'message': f'Can\'t continue because user borrow id {pk} is borrowing the product'})
        user = self.get_object(pk)
        user.delete()
        return Response({'status': 204, 'message': 'Delete User Succes'})


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
        return Response({'status': 200, 'message': 'succes', 'data': serializer.data}, status=status.HTTP_200_OK)


class AuthAdminAPIView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        user = request.user
        if user.role == 1:
            serializer = self.serializer_class(user)
            return Response({'status': 200, 'message': 'succes', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 401, 'message': 'You do not have permission to use this action !'})


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
            return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'User profile not found'})
        else:
            return profile

    def get(self, request):
        user_profile = self.get_object(request)
        serializer = self.serializer_class(user_profile)
        response = {
            'status': status.HTTP_200_OK,
            'message': 'success',
            'data': {
                'user_id': request.user.id,
                'name': request.user.name,
                'email': request.user.email,
                'code': request.user.code,
                'profile': serializer.data
            },
        }
        return Response(response)

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
                'status': status.HTTP_200_OK,
                'message': 'Update profile success',
                'data': {
                    'user_id': request.user.id,
                    'name': request.user.name,
                    'email': request.user.email,
                    'code': request.user.code,
                    'profile': serializer.data
                },
            }
            return Response(response)
        return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': serializer.errors})


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
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Wrong password",
            }
            return Response(response)
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")
        validate_password(new_password)
        validate_password(confirm_password)
        self.object.set_password(confirm_password)
        self.object.save()
        response = {
            'status': status.HTTP_200_OK,
            'message': 'Change password successfully',
            'data': {
                'user_id': self.request.user.id
            }
        }
        return Response(response)


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
                raise NotFound(
                    {'status': 404, 'message': 'The account no longer exists!!'})
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            url_reset_password = f'{FE_URL}/new-password?uid=' + \
                uid+'&token='+token
            # send mail
            send_email_to_user(to_email=user.email, user_data=dict(
                user=user, code=token, url_reset_password=f'{url_reset_password}'))
            response = {
                'status': status.HTTP_200_OK,
                'message': 'Email sent. Please check your email',
            }
            return Response(response)
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
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Validate Password Wrong"})
            user.set_password(new_password)
            user.save()
            response = {
                'status': status.HTTP_200_OK,
                'message': 'Password reset successfully',
            }
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
