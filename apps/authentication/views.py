from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse 
from drf_spectacular.openapi import OpenApiTypes

from .serializers import LoginSerializer, UserSerializer
# Create your views here.

class LoginView(APIView):

    """
        POST /api/admin/auth/login/
    
        Recibe: { username, password }
        Retorna: { access, refresh, user }
    
        El token 'access' dura 1 hora → se usa en cada request
        El token 'refresh' dura 7 días → se usa para renovar el access
    """
    
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Auth'],
        summary='Iniciar sesión',
        description='Retorna tokens JWT de acceso y refresco. Solo usuarios staff pueden acceder.',
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description='Login exitoso, retorna access y refresh tokens'),
            400: OpenApiResponse(description='Credenciales inválidas o usuario no autorizado'),
        }
    )

    def post(self,request):
        serializer = LoginSerializer(
            data=request.data,
            context={'request':request}
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        return Response({
            'access':str(refresh.access_token),
            'refresh':str(refresh),
            'user':UserSerializer(user).data
            },status=status.HTTP_200_OK)
    

class LogoutView(APIView):
    """
    POST /api/admin/auth/logout/
    
    Invalida el refresh token para cerrar sesión.
    El access token sigue válido hasta que expire (1 hora),
    pero el frontend debe eliminarlo localmente.
    """
    permission_classes=[IsAuthenticated]

    @extend_schema(
        tags=['Auth'],
        summary='Cerrar sesión',
        description='Invalida el refresh token. El frontend debe eliminar el access token localmente.',
        request=None,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        }
    )
    def post(self,request):

        try:

            refresh_token = request.data.get('refresh')

            if not refresh_token:
                return Response(
                    {'error':'Se requiere el refresh token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {'message': 'Sesion cerrada correctamente'},
                status=status.HTTP_200_OK
            )
        

        except Exception:
            return Response(
                {'error': 'Token inválido o ya expirado.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class UserProfileView(APIView):

    """
    GET /api/admin/auth/me/
    
    Retorna los datos del usuario actualmente autenticado.
    El frontend usa esto para saber qué usuario está logueado
    y mostrar su nombre en el panel.
    
    Requiere: Authorization: Bearer {access_token}
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Auth'],
        summary='Perfil del usuario actual',
        description='Retorna los datos del usuario autenticado.',
        responses={200: UserSerializer}
    )

    def get(self,request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)