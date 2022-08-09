from asyncore import read
from turtle import position
from device_mngr_auth.common.exceptions import EmailException
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from .constants import DMAUserRoleType

from .models import DMAUser, Position, UserProfile


class AuthLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def authenticate(self):
        user = authenticate(email=self.email, password=self.password)
        refresh = RefreshToken.for_user(user)
        return {
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
        }

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'name']
        
class UserProfileSerializer(serializers.ModelSerializer):
    position = serializers.SlugRelatedField(queryset=Position.objects.all(),slug_field='name')
    class Meta:
        model = UserProfile
        fields = ['id','firstName','lastName','phone_number','date_of_birth','position']
        
        
class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=[DMAUserRoleType.USER.value, DMAUserRoleType.ADMIN.value], default=DMAUserRoleType.USER.value)
    profile = UserProfileSerializer()
    class Meta:
        model = DMAUser
        fields = ['id', 'name', 'email', 'role', 'code', 'profile', 'created_at', 'updated_at', 'deleted_at']
        read_only_fields = ['deleted_at','code']
        
    def validate(self, validated_data):

        if DMAUser.objects.filter(email=validated_data['email']).first():
            raise EmailException()
        
        password = {'password': 'DAD-'+ validated_data['profile']['lastName']}
        validated_data.update(password)
        profile_data = validated_data.pop('profile')
        user = DMAUser.objects.create(**validated_data)
        UserProfile.objects.create(user=user, **profile_data)
        user.code = str(profile_data['position']) + str(user.id)
        user.save()
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
        #token['role'], token_refresh['role'] = user.role, user.role
        
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

        
        
