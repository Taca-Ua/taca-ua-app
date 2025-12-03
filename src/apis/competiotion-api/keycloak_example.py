"""
Example Keycloak authentication implementation for Django REST Framework.
This is a reference implementation that shows how to integrate Keycloak with Django.

For the actual implementation, add to your Django settings and views.
"""

# settings.py additions
"""
INSTALLED_APPS = [
    # ... other apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ... other middleware
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

from datetime import timedelta

SIMPLE_JWT = {
    'ALGORITHM': 'RS256',
    'SIGNING_KEY': None,
    'VERIFYING_KEY': None,  # Will be fetched from Keycloak JWKS
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'sub',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

KEYCLOAK_CONFIG = {
    'KEYCLOAK_SERVER_URL': os.getenv('KEYCLOAK_URL', 'http://keycloak:8080'),
    'KEYCLOAK_REALM': os.getenv('KEYCLOAK_REALM', 'taca-ua'),
    'KEYCLOAK_JWKS_URL': f\"{os.getenv('KEYCLOAK_URL', 'http://keycloak:8080')}/realms/{os.getenv('KEYCLOAK_REALM', 'taca-ua')}/protocol/openid-connect/certs\",
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:3001',
]
"""

# Example views.py implementation
"""
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_competitions(request):
    # User from JWT token is automatically available as request.user
    user = request.user
    return Response({
        'competitions': [],
        'user': user.username,
        'email': user.email
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_competition(request):
    # Verify admin role
    token = request.auth  # JWT token
    roles = token.get('realm_access', {}).get('roles', [])
    
    if 'admin' not in roles:
        return Response(
            {'error': 'Admin role required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Create competition logic here
    return Response({'created': True})
"""

# For custom Keycloak integration using python-keycloak
"""
from keycloak import KeycloakOpenID
from django.conf import settings

keycloak_openid = KeycloakOpenID(
    server_url=settings.KEYCLOAK_CONFIG['KEYCLOAK_SERVER_URL'],
    client_id=settings.KEYCLOAK_CONFIG['KEYCLOAK_CLIENT_ID'],
    realm_name=settings.KEYCLOAK_CONFIG['KEYCLOAK_REALM'],
    client_secret_key=settings.KEYCLOAK_CONFIG['KEYCLOAK_CLIENT_SECRET'],
)

# Get token
token = keycloak_openid.token(username='user', password='pass')
access_token = token['access_token']

# Verify token
decoded_token = keycloak_openid.decode_token(access_token)
"""

print("Django Keycloak integration reference - see comments above")
