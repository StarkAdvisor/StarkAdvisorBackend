"""
Tests comprehensivos para la aplicación user_admin - VERSIÓN FUNCIONAL
Incluye tests con mocks para Redis y autenticación
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from unittest.mock import patch, MagicMock
import json

User = get_user_model()


class UserRegistrationTestCase(APITestCase):
    """Tests para el endpoint de registro de usuarios"""
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('user_admin:user-register')
        self.valid_user_data = {
            'email': 'test@starkadvisor.com',
            'username': 'testuser',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123',
            'first_name': 'Juan',
            'last_name': 'Perez',
            'risk_profile': 'conservative'
        }
    
    def test_user_registration_success(self):
        """Test: Registro exitoso de usuario"""
        response = self.client.post(
            self.register_url,
            data=json.dumps(self.valid_user_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='test@starkadvisor.com').exists())
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
    
    def test_user_registration_duplicate_email(self):
        """Test: Registro con email duplicado"""
        
        User.objects.create_user(
            email='test@starkadvisor.com',
            username='existing_user',
            password='testpass123'
        )
        
        response = self.client.post(
            self.register_url,
            data=json.dumps(self.valid_user_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_registration_invalid_email(self):
        """Test: Registro con email inválido"""
        invalid_data = self.valid_user_data.copy()
        invalid_data['email'] = 'email_invalido'
        
        response = self.client.post(
            self.register_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTestCase(APITestCase):
    """Tests para el endpoint de login de usuarios"""
    
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('user_admin:user-login')
        
        self.user = User.objects.create_user(
            email='login@test.com',
            username='loginuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    @patch('user_admin.views.cache_user_session')
    def test_user_login_success(self, mock_cache_session):
        """Test: Login exitoso con mock de Redis"""
        
        mock_cache_session.return_value = True
        
        login_data = {
            'email': 'login@test.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        mock_cache_session.assert_called_once()
    
    def test_user_login_invalid_credentials(self):
        """Test: Login con credenciales inválidas"""
        login_data = {
            'email': 'login@test.com',
            'password': 'wrong_password'
        }
        
        response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login_nonexistent_user(self):
        """Test: Login con usuario que no existe"""
        login_data = {
            'email': 'nonexistent@test.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLogoutTestCase(APITestCase):
    """Tests para el endpoint de logout de usuarios"""
    
    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('user_admin:user-logout')
        
        self.user = User.objects.create_user(
            email='logout@test.com',
            username='logoutuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
    
    @patch('user_admin.views.clear_user_session')
    def test_user_logout_success(self, mock_clear_session):
        """Test: Logout exitoso con mock de Redis"""
        
        mock_clear_session.return_value = True
        
        
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Token {self.token.key}'
        
        response = self.client.post(self.logout_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        mock_clear_session.assert_called_once()
        
        
        self.assertFalse(Token.objects.filter(key=self.token.key).exists())
    
    def test_user_logout_without_token(self):
        """Test: Logout sin token de autenticación"""
        response = self.client.post(self.logout_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SessionStatusTestCase(APITestCase):
    """Tests para el endpoint de estado de sesión"""
    
    def setUp(self):
        self.client = Client()
        self.session_url = reverse('user_admin:session-status')
        
        self.user = User.objects.create_user(
            email='session@test.com',
            username='sessionuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
    
    @patch('user_admin.views.get_user_session')
    def test_session_status_active(self, mock_get_session):
        """Test: Estado de sesión activa con mock"""
        
        mock_get_session.return_value = {
            'user_id': self.user.id,
            'email': self.user.email,
            'login_time': '2024-01-01T10:00:00'
        }
        
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Token {self.token.key}'
        
        response = self.client.get(self.session_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(response.data['authenticated'])
        self.assertIn('session_data', response.data)
        self.assertIn('user', response.data)
        mock_get_session.assert_called_once()
    
    @patch('user_admin.views.get_user_session')
    def test_session_status_inactive(self, mock_get_session):
        """Test: Estado de sesión inactiva con mock"""

        mock_get_session.return_value = None
        
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Token {self.token.key}'
        
        response = self.client.get(self.session_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['authenticated'])  
        self.assertIsNone(response.data['session_data'])
        mock_get_session.assert_called_once()


class RedisIntegrationTestCase(TestCase):
    """Tests para las funciones de integración con Redis usando mocks"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='redis@test.com',
            username='redisuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
    
    @patch('user_admin.views.redis_client')
    def test_cache_user_session_mock(self, mock_redis):
        """Test: Función de cachear sesión con mock"""
        from user_admin.views import cache_user_session
        
        
        mock_redis.setex.return_value = True
        
       
        cache_user_session(self.user, self.token)
        
        
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        
        
        self.assertIn(f"starkadvisor_local:user_session_{self.user.id}", call_args[0])
        self.assertEqual(call_args[0][1], 86400) 
    
    @patch('user_admin.views.redis_client')
    def test_get_user_session_mock(self, mock_redis):
        """Test: Función de obtener sesión con mock"""
        from user_admin.views import get_user_session
        
        
        session_data = {
            'user_id': self.user.id,
            'email': self.user.email,
            'login_time': '2024-01-01T10:00:00'
        }
        mock_redis.get.return_value = json.dumps(session_data)
        
        result = get_user_session(self.user.id)
        
        
        mock_redis.get.assert_called_once_with(f"starkadvisor_local:user_session_{self.user.id}")
        self.assertEqual(result['user_id'], self.user.id)
        self.assertEqual(result['email'], self.user.email)
    
    @patch('user_admin.views.redis_client')
    def test_clear_user_session_mock(self, mock_redis):
        """Test: Función de limpiar sesión con mock"""
        from user_admin.views import clear_user_session
        
        
        mock_redis.delete.return_value = 1  
        
        clear_user_session(self.user.id)
        
        
        self.assertEqual(mock_redis.delete.call_count, 2)
        calls = mock_redis.delete.call_args_list
        
        
        keys_called = [call[0][0] for call in calls]
        self.assertIn(f"starkadvisor_local:user_session_{self.user.id}", keys_called)
        self.assertIn(f"user_session:{self.user.id}", keys_called)


class APIEndpointsIntegrationTestCase(APITestCase):
    """Tests de integración para todos los endpoints API"""
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('user_admin:user-register')
        self.login_url = reverse('user_admin:user-login')
        self.logout_url = reverse('user_admin:user-logout')
    
    @patch('user_admin.views.cache_user_session')
    @patch('user_admin.views.clear_user_session')
    def test_complete_user_flow_with_mocks(self, mock_clear_session, mock_cache_session):
        """Test: Flujo completo de usuario (registro -> login -> logout) con mocks"""
        
        
        mock_cache_session.return_value = True
        mock_clear_session.return_value = True
        
        
        register_data = {
            'email': 'flow@test.com',
            'username': 'flowuser',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123',
            'first_name': 'Flow',
            'last_name': 'Test',
            'risk_profile': 'moderate'
        }
        
        register_response = self.client.post(
            self.register_url,
            data=json.dumps(register_data),
            content_type='application/json'
        )
        
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        
        
        login_data = {
            'email': 'flow@test.com',
            'password': 'testpassword123'
        }
        
        login_response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('token', login_response.data)
        
        
        token = login_response.data['token']
        
        
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Token {token}'
        
        logout_response = self.client.post(self.logout_url)
        
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        
        
        mock_cache_session.assert_called_once()
        mock_clear_session.assert_called_once()


class RiskProfileTestCase(TestCase):
    """Tests para funcionalidad de perfil de riesgo"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='risk@test.com',
            username='riskuser',
            password='testpass123',
            risk_profile='conservative'
        )
    
    def test_risk_profile_default(self):
        """Test: Perfil de riesgo por defecto"""
        new_user = User.objects.create_user(
            email='newrisk@test.com',
            username='newriskuser',
            password='testpass123'
        )
        self.assertEqual(new_user.risk_profile, 'moderate')
    
    def test_risk_profile_display_info(self):
        """Test: Información del perfil de riesgo"""
        risk_info = self.user.get_risk_profile_display_info()
        
        self.assertIn('name', risk_info)
        self.assertIn('description', risk_info)
        self.assertIn('characteristics', risk_info)
        self.assertEqual(risk_info['name'], 'Conservador')


class UserModelTestCase(TestCase):
    """Tests para el modelo CustomUser"""
    
    def test_user_creation(self):
        """Test: Creación básica de usuario"""
        user = User.objects.create_user(
            email='model@test.com',
            username='modeluser',
            password='testpass123',
            first_name='Model',
            last_name='Test'
        )
        
        self.assertEqual(user.email, 'model@test.com')
        self.assertEqual(user.get_full_name(), 'Model Test')
        self.assertEqual(user.risk_profile, 'moderate')  
    
    def test_user_string_representation(self):
        """Test: Representación en string del usuario"""
        user = User.objects.create_user(
            email='string@test.com',
            username='stringuser',
            password='testpass123',
            first_name='String',
            last_name='Test'
        )
        
        expected = "String Test (string@test.com)"
        self.assertEqual(str(user), expected)


class AuthenticationTestCase(APITestCase):
    """Tests adicionales para autenticación"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='auth@test.com',
            username='authuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
    
    def test_token_authentication(self):
        """Test: Autenticación con token"""
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Token {self.token.key}'
        
        
        session_url = reverse('user_admin:session-status')
        response = self.client.get(session_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['authenticated'])
    
    def test_invalid_token_authentication(self):
        """Test: Autenticación con token inválido"""
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Token invalid_token_key'
        
        
        session_url = reverse('user_admin:session-status')
        response = self.client.get(session_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
