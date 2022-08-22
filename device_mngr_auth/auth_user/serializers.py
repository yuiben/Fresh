import os
import base64
import uuid
from datetime import datetime
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate
from django.db import transaction

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, NotFound, ValidationError

from .constants import DMAUserRoleType
from .models import DMAUser, Position, UserProfile
from device_mngr_auth.borrow.models import Borrow
from device_mngr_auth.common.exceptions import InvalidEmailException, UserNotFoundException
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

ENV_FILE = os.getenv("USE_ENV_FILE", ".env")


class AuthLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def authenticate(self):
        user = authenticate(
            email=self.data['email'], password=self.data['password'])
        refresh = RefreshToken.for_user(user)
        return {
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
        }


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'name']


class UserProfileCreateSerializer(serializers.ModelSerializer):
    position = serializers.PrimaryKeyRelatedField(queryset=Position.objects.all())
    date_of_birth = serializers.DateField(format="%d-%m-%Y", input_formats=['%d-%m-%Y'])
    image = serializers.ImageField(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'last_name', 'image',
                  'phone_number', 'date_of_birth', 'position']
    
    def validate_phone_number(self, value):
        try:
            int(value)
            if value.startswith("0"):
                return value
            raise ValidationError()
        except:
            raise ValidationError("Phone number must be numberic and start with 0")
    

class UserProfileViewSerializer(UserProfileCreateSerializer):
    position = serializers.SlugRelatedField(
        queryset=Position.objects.all(), slug_field='name')
    
    class Meta:
        model = UserProfileCreateSerializer.Meta.model
        fields = UserProfileCreateSerializer.Meta.fields


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileViewSerializer()

    class Meta:
        model = DMAUser
        exclude = ['password']


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(min_length=3, max_length=255,
        validators=[
            UniqueValidator(
                queryset=DMAUser.objects.all(),
                message="Email already exists.!!"
            )]
        )
    role = serializers.ChoiceField(
        choices=[DMAUserRoleType.USER.value, DMAUserRoleType.ADMIN.value],
        default=DMAUserRoleType.USER.value)
    profile = UserProfileCreateSerializer()
    
    class Meta:
        model = DMAUser
        exclude =  ['password']
        read_only_fields = ['deleted_at', 'code']
        
    def create(self, validated_data):
        password = {'password': os.getenv("USER_DEFAULT_PASSWORD")}
        validated_data.update(password)
        profile_data = validated_data.pop('profile')
        user = DMAUser.objects.create(**validated_data)
        UserProfile.objects.create(user=user, **profile_data)
        user.code = str(profile_data['position']) + str(user.id)
        user.save()
        return user
    

class SoftDeleteUserSerializer(serializers.Serializer):
    id = serializers.ListField(
        child=serializers.IntegerField())

    @transaction.atomic
    def delete(self, validated_data):
        with transaction.atomic():
            for value in validated_data['id']:
                user_borrow = Borrow.objects.filter(
                    user_id=value, deleted_at=None)
                if len(user_borrow) != 0:
                    raise UserNotFoundException({
                        'status': 400, 
                        'message': f'Can\'t continue because user borrow id {value} is borrowing the product'})
                try:
                    user = DMAUser.objects.get(pk=value, deleted_at=None)
                    user.deleted_at = datetime.now()
                    user.save()

                    profile = UserProfile.objects.get(
                        user=value, deleted_at=None)
                    profile.deleted_at = datetime.now()
                    profile.save()
                except DMAUser.DoesNotExist:
                    raise UserNotFoundException({
                        'status': 400, 
                        'message': f'Can\'t continue because user id {value} can\'t be found'})
        return user




class UserProfileSerializer(serializers.ModelSerializer):
    position = serializers.SlugRelatedField(read_only=True, slug_field='name')
    date_of_birth = serializers.DateField(
        format="%d-%m-%Y", input_formats=['%d-%m-%Y', 'iso-8601'])
    image = serializers.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'last_name',
                  'phone_number', 'date_of_birth', 'image', 'position']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=255, min_length=6, write_only=True)

    class Meta:
        model = DMAUser
        fields = ['email', 'password']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        try:
            user = DMAUser.objects.get(email=email, deleted_at = None)
            user = authenticate(email=email, password=password)
            if not user:
                raise AuthenticationFailed({
                    'status': 401, 'message': 'Wrong Password'})
        except DMAUser.DoesNotExist:
                    raise NotFound('Email does not exist!!')
                    
        serializer = UserProfileSerializer(user.profile)
        refresh = RefreshToken.for_user(user)
        token = refresh.access_token
        return {
            'status': 200,
            'message': 'succes',
            'data': {
                'user_id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role,
                'code': user.code,
                'profile': serializer.data,
                'refresh_token': str(refresh),
                'access_token': str(token),
            }
        }

class UserChangePasswordSerializer(serializers.Serializer):
    """
    Change password:
        - input old_password, new_password, confirm_password
        - validate: new_password==confirm_password
    """
    old_password = serializers.CharField(max_length=255, required=True)
    new_password = serializers.CharField(
        max_length=255, write_only=True, required=True)
    confirm_password = serializers.CharField(
        max_length=255, write_only=True, required=True)

    class Meta:
        fields = ['old_password', 'new_password', 'confirm_password']

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        if new_password != confirm_password:
            raise serializers.ValidationError(
                "Password and Confirm Password doesn't match")
        return attrs


class SendPasswordResetEmailSerializer(serializers.Serializer):
    """
    Forgot password:
      - Send mail
      - Reset password
    """
    email = serializers.EmailField(max_length=255, required=True)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if not DMAUser.objects.filter(email=email).first():
            raise InvalidEmailException()
        return attrs


class UserResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=255, required=True)
    confirm_password = serializers.CharField(max_length=255, required=True)

    class Meta:
        fields = ['new_password', 'confirm_password']

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        if new_password != confirm_password:
            raise serializers.ValidationError(
                "Password and Confirm Password doesn't match")
        return attrs

