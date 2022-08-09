from xml.dom import ValidationErr
from drf_spectacular.utils import extend_schema

from rest_framework import generics, status, permissions
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from device_mngr_auth.common.validate import check_form_password_user
from device_mngr_auth.auth_user.models import DMAUser, UserProfile
from device_mngr_auth.common.paginators import CustomPagination
from device_mngr_auth.common.exceptions import UserNotFoundException
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
    )


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


#@extend_schema(request=, responses=None, methods=['POST'])
@api_view(["POST"])
@permission_classes([permissions.AllowAny,])
def soft_delete_user(request):
    uid = request.data['id']
    user = DMAUser.objects.get(pk=uid)
    return Response(user)


class ListCreateUserAPIView(generics.ListCreateAPIView):

    #permission_classes = (permissions.IsAuthenticated, IsAdminUser,)
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    
    def get(self, request):
        user = DMAUser.objects.filter(deleted_at=None)
        serializer = self.serializer_class(user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'code': 201, 'message': 'succes', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    
    
class ListDetailUserAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer
    
    def get_object(self, pk):
        try:
            return DMAUser.objects.get(pk=pk,deleted_at=None)
        except DMAUser.DoesNotExist:
            raise UserNotFoundException()
        
    def get(self, request, pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    def put(self, request, pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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
        return Response({'code': 200, 'message': 'succes', 'data': serializer.data}, status=status.HTTP_200_OK)


class AuthAdminAPIView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        # print(request.META.get("HTTP_AUTHORIZATION"))
        user = request.user
        if user.role == 1:
            serializer = self.serializer_class(user)
            return Response({'code': 200, 'message': 'succes', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'code': 401, 'message': 'You do not have permission to use this action !'})

class UserProfileDetail(RetrieveAPIView):
    """
    Read profile user
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

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
            serializer.save()
            return Response({'status': status.HTTP_200_OK, 'message': 'uppdate user success', 'data': serializer.data})
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
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            url_reset_password = 'http://localhost:3000/api/v1/auth/reset-password?uid=' + \
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
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise ValidationErr('Token is not Valid or Expired')
            new_password = request.data.get("new_password")
            user.set_password(new_password)
            user.save()
            response = {
                'status': status.HTTP_200_OK,
                'message': 'Password reset successfully',
            }
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
