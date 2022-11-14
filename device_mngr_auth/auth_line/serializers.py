from rest_framework import serializers


class AuthLoginSerializer(serializers.Serializer):
    code = serializers.CharField()
    state = serializers.CharField()
    redirect_url = serializers.CharField()

