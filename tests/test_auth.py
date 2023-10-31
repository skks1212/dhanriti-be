from rest_framework.test import APITestCase


class LoginTestCase(APITestCase):
    token = None
    # commented out as they fail if authentication Method is Vishnu
    """
    def setUp(self):
        self.client = APIClient()
        User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass",
        )

    def test_login(self):
        response = self.client.post(
            "/v4/auth/login",
            {
                "email": "test@test.com",
                "password": "testpass",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertTrue("token" in json)

        self.token = response.json()["token"]

    def test_wrong_password(self):
        response = self.client.post(
            "/v4/auth/login",
            {
                "email": "test@test.com",
                "password": "wrongpass",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue("non_field_errors" in response.json())

    def test_wrong_email(self):
        response = self.client.post(
            "/v4/auth/login",
            {
                "email": "test@test.in",
                "password": "testpass",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue("non_field_errors" in response.json())

    def test_logout(self):
        # get token
        self.test_login()
        token = f"Token {self.token}"

        # check if token is valid
        response = self.client.get(
            "/v4/users/me",
            {},
            format="json",
            HTTP_AUTHORIZATION=token,
        )

        self.assertEqual(response.status_code, 200)

        # logout
        response = self.client.delete(
            "/v4/auth/logout",
            {},
            format="json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, 204)

        # check if token is invalid
        response = self.client.get(
            "/v4/users/me",
            {},
            format="json",
            HTTP_AUTHORIZATION=token,
        )

        self.assertEqual(response.status_code, 401)
    """
