from device_mngr_auth.common.exceptions import EmailException, UserNotFoundException
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, NotFound
from .constants import DMAUserRoleType, DefaultPasswordUser

from .models import DMAUser, Position, UserProfile
from datetime import date
from device_mngr_auth.borrow.models import Borrow
from django.db import transaction


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

    class Meta:
        model = UserProfile
        fields = ['id','first_name','last_name','phone_number','date_of_birth','position']

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
        
        
    def create(self, validated_data):
        if DMAUser.objects.filter(email=validated_data['email']).first():
            raise EmailException()
        password = {'password': DefaultPasswordUser.PASSWORD}
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
    def create(self, validated_data):

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

                    profile = UserProfile.objects.get(user=value, deleted_at=None)
                    profile.deleted_at = date.today()
                    profile.save()
                except DMAUser.DoesNotExist:
                    raise UserNotFoundException(
                        {'code': 400, 'message': f'Can\'t continue because user id {value} can\'t be found'})
        return user

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=255, min_length=6, write_only=True)
    
    class Meta:
        model = DMAUser
        fields = ['email', 'password']
        

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        user = authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed({'code':401,'message':'Account Invalid, Try Again'})
        refresh = RefreshToken.for_user(user)
        token = refresh.access_token
        return {
            'refresh_token':str(refresh),
            'access_token':str(token),
            'data': {
                'user_id':user.id,
                'email': user.email,
                'name' : user.name,
                'phone_number' : user.profile.phone_number,
                'role' : user.role
            }
        }

        
        
class UserProfileSerializer(serializers.ModelSerializer):
    position = serializers.SlugRelatedField(read_only=True, slug_field='name')

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
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']
    
    def validate(self, attrs):
        email = attrs.get('email')
        if not DMAUser.objects.filter(email=email).first():
            raise serializers.ValidationError(
                "User not found"
            )
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
