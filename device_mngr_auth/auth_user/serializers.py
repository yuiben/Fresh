import base64
import os
import base64
import uuid
from datetime import date
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate
from django.db import transaction

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, NotFound

from .constants import DMAUserRoleType
from .models import DMAUser, Position, UserProfile
from device_mngr_auth.borrow.models import Borrow
from device_mngr_auth.common.exceptions import InvalidEmailException, UserNotFoundException

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
    position = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all())
    phone_number = serializers.CharField(min_length=10, max_length=10)

    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'last_name', 'image',
                  'phone_number', 'date_of_birth', 'position']


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
        fields = [
            'id', 'name', 'email', 'role', 'code', 'profile', 'created_at', 'updated_at', 'deleted_at'
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        choices=[DMAUserRoleType.USER.value, DMAUserRoleType.ADMIN.value],
        default=DMAUserRoleType.USER.value)
    profile = UserProfileCreateSerializer()

    class Meta:
        model = DMAUser
        fields = [
            'id', 'name', 'email', 'role', 'code', 'profile', 'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['deleted_at', 'code']

    def validate(self, data):
        phone_number = data['profile']['phone_number']
        if UserProfile.objects.filter(phone_number=phone_number).first():
            raise serializers.ValidationError(
                {"phone_number": "Phone number is Exists"})
        try:
            int(phone_number)
        except:
            raise serializers.ValidationError(
                {"phone_number": "Phone number must be numeric characters"})

        if phone_number.startswith("0") == False:
            raise serializers.ValidationError(
                {"phone_number": "Phone number must start with 0"})

        return data

    def create(self, validated_data):
        password = {'password': os.getenv("USER_DEFAULT_PASSWORD")}
        validated_data.update(password)
        profile_data = validated_data.pop('profile')
        user = DMAUser.objects.create(**validated_data)
        UserProfile.objects.create(user=user, **profile_data)
        user.code = str(profile_data['position']) + str(user.id)
        user.save()
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        profile = instance.profile

        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.role = validated_data.get('role', instance.role)
        instance.save()

        profile.first_name = profile_data.get('first_name', profile.first_name)
        profile.last_name = profile_data.get('first_name', profile.last_name)
        profile.phone_number = profile_data.get(
            'phone_number', profile.phone_number)
        profile.date_of_birth = profile_data.get(
            'date_of_birth', profile.date_of_birth)
        profile.position = profile_data.get('position', profile.position)
        profile.save()
        return instance


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
                    raise UserNotFoundException(
                        {'code': 400, 'message': f'Can\'t continue because user borrow id {value} is borrowing the product'})
                try:
                    user = DMAUser.objects.get(pk=value, deleted_at=None)
                    user.deleted_at = date.today()
                    user.save()

                    profile = UserProfile.objects.get(
                        user=value, deleted_at=None)
                    profile.deleted_at = date.today()
                    profile.save()
                except DMAUser.DoesNotExist:
                    raise UserNotFoundException(
                        {'code': 400, 'message': f'Can\'t continue because user id {value} can\'t be found'})
        return user


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
            DMAUser.objects.get(email=email)
        except:
            raise NotFound(
                {'code': 404, 'message': 'The Email no exists!!'})

        user = authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed(
                {'code': 401, 'message': 'Wrong Password'})

        if user.deleted_at != None:
            raise NotFound(
                {'code': 404, 'message': 'The account no longer exists!!'})
        refresh = RefreshToken.for_user(user)
        token = refresh.access_token
        return {
            'code': 200,
            'message': 'succes',
            'data': {
                'user_id': user.id,
                'email': user.email,
                'name': user.name,
                'phone_number': user.profile.phone_number,
                'role': user.role,
                'code': user.code,
                'date_of_birth': user.profile.date_of_birth,
                'position': user.profile.position.name,
                'refresh_token': str(refresh),
                'access_token': str(token),
            }
        }


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            # base64 encoded image - decode
            format, imgstr = data.split(';base64,')  # format ~= data:image/X,
            ext = format.split('/')[-1]  # guess file extension
            id = uuid.uuid4()
            data = ContentFile(base64.b64decode(imgstr),
                               name=id.urn[9:] + '.' + ext)
        return super(Base64ImageField, self).to_internal_value(data)


class UserProfileSerializer(serializers.ModelSerializer):
    position = serializers.SlugRelatedField(read_only=True, slug_field='name')
    date_of_birth = serializers.DateField(
        format="%d-%m-%Y", input_formats=['%d-%m-%Y', 'iso-8601'])
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'last_name',
                  'phone_number', 'date_of_birth', 'image', 'position']


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

