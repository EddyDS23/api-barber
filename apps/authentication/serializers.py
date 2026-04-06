
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class LoginSerializer(serializers.Serializer):

    '''
        Validar las credenciales del login
    '''

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self,attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError(
                'Debe proporcionar usuario y contraseña',
                code='authorization'
            )
        

        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password
        )

        if not user:
            raise serializers.ValidationError(
                'Credenciales invalidas. Verifique denuevo',
                code='authorization'
            )
        
        if not user.is_staff:
            raise serializers.ValidationError(
                'No tiene permisos para entrar al panel',
                code='authorization'
            )
        

        attrs['user'] = user
        return attrs
    

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model=User
        fields = ['id','username','email','first_name','last_name','is_staff']
        read_only_fields = ['id','is_staff']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
