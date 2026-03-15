from rest_framework import permissions

class AllowAny(permissions.AllowAny):
    '''
        Accesso a todo el publico
    '''

    def has_permission(self, request, view):
        return True;


class IsAdmin(permissions.BasePermission):
    '''
        Accesso solo a Administradores
    '''

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.is_staff
        )
    

class IsAdminOrReadOnly(permissions.BasePermission):
    '''
        Admin: Leer y Escribir
        Otros: Leer
    '''

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.is_staff
        )