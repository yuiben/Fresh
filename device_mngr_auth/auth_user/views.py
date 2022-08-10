from drf_spectacular.utils import extend_schema

from rest_framework import generics, status, permissions
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from device_mngr_auth.common.validate import check_form_password_user
from device_mngr_auth.auth_user.models import DMAUser
from device_mngr_auth.common.paginators import CustomPagination
from device_mngr_auth.common.exceptions import UserNotFoundException
from .permissions import IsAdminUser



from device_mngr_auth.auth_user.serializers import (
    AuthLoginSerializer,
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

    permission_classes = (permissions.IsAuthenticated, IsAdminUser,)
    serializer_class = UserSerializer
    # queryset = DMAUser.objects.all()
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
