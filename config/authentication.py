"""
Autenticador personalizado para API Keys de rest_framework_api_key.
Permite que requests HTTP reales (no solo test client) sean autenticadas con API Key.
"""
import logging
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_api_key.models import APIKey

logger = logging.getLogger(__name__)


class APIKeyAuthentication(BaseAuthentication):
    """
    Autenticación basada en API Key enviada en el header Authorization.
    Formato: Authorization: Api-Key <key>
    """
    
    def authenticate(self, request):
        # Obtener el header Authorization
        auth_header_value = request.META.get('HTTP_AUTHORIZATION', '')
        logger.info(f'[APIKeyAuthentication] AUTH HEADER: {auth_header_value[:50] if auth_header_value else "NO HEADER"}')
        
        auth_header = auth_header_value.split()
        
        if len(auth_header) != 2:
            # Sin header o formato incorrecto - dejar que otro autenticador lo intente
            logger.info(f'[APIKeyAuthentication] Invalid format or no header')
            return None
        
        auth_type, key = auth_header
        logger.info(f'[APIKeyAuthentication] AUTH TYPE: {auth_type}, KEY: {key[:10]}...')
        
        # Verificar que el tipo es "Api-Key"
        if auth_type.lower() != 'api-key':
            # Otro tipo de autenticación - dejar que otro autenticador lo intente
            logger.info(f'[APIKeyAuthentication] Wrong auth type')
            return None
        
        # Verificar si la API Key es válida
        is_valid = APIKey.objects.is_valid(key)
        logger.info(f'[APIKeyAuthentication] is_valid({key[:10]}...): {is_valid}')
        
        if not is_valid:
            raise AuthenticationFailed('API Key inválida.')
        
        # Obtener el objeto APIKey para pasarlo como request.auth
        try:
            api_key_obj = APIKey.objects.get_from_key(key)
            logger.info(f'[APIKeyAuthentication] Got APIKey object: {api_key_obj.name}')
        except APIKey.DoesNotExist:
            # Aunque is_valid retornó True, algo salió mal
            logger.error(f'[APIKeyAuthentication] get_from_key failed but is_valid was True')
            raise AuthenticationFailed('API Key no encontrada.')
        
        # Retorna (user, auth) — None como user, objeto APIKey como auth
        logger.info(f'[APIKeyAuthentication] SUCCESS: Returning APIKey object')
        return (None, api_key_obj)
