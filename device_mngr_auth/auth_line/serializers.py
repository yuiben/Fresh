from rest_framework import serializers


class AuthLoginSerializer(serializers.Serializer):
    code = serializers.CharField()
    state = serializers.CharField()
    redirect_url = serializers.CharField()


class UserUpdateLineSerializer(serializers.Serializer):
    line_id = serializers.CharField()
    user_id = serializers.CharField()

