"""
Aceptación — ÉPICA 1: Autenticación.
HU-01 Iniciar sesión (JWT) · HU-02 Cerrar sesión (blacklist del refresh token).

La app no tenía tests; se agregan ejerciendo los endpoints reales de JWT.
"""
from apps.acceptance_base import AcceptanceBase


class AutenticacionTests(AcceptanceBase):

    def _login(self, password='clave12345'):
        self.as_anon()
        return self.client.post('/api/v1/auth/token/', {
            'username': 'admin_test', 'password': password,
        }, format='json')

    # ---------------- HU-01 — Iniciar sesión ----------------
    def test_hu01_login_correcto_devuelve_tokens(self):
        r = self._login()
        self.assertEqual(r.status_code, 200)
        self.assertIn('access', r.data)
        self.assertIn('refresh', r.data)

    def test_hu01_login_credenciales_incorrectas_rechazado(self):
        r = self._login(password='CLAVE-MALA')
        self.assertEqual(r.status_code, 401)

    def test_hu01_ruta_protegida_sin_token_bloquea(self):
        self.as_anon()
        r = self.client.get('/api/v1/dashboard/kpis/')
        self.assertIn(r.status_code, (401, 403))

    # ---------------- HU-02 — Cerrar sesión ----------------
    def test_hu02_logout_invalida_refresh_token(self):
        tokens = self._login().data
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        r = self.client.post('/api/v1/auth/logout/',
                             {'refresh': tokens['refresh']}, format='json')
        self.assertEqual(r.status_code, 200)

        # Tras el logout, el refresh token ya NO debe poder renovar sesión.
        self.client.credentials()
        r2 = self.client.post('/api/v1/auth/token/refresh/',
                              {'refresh': tokens['refresh']}, format='json')
        self.assertEqual(r2.status_code, 401)