from rest_framework import status
from rest_framework.test import APITestCase

from dhanriti.models import Follow, User


class MeTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="testuser1", email="testuser1@example.com", full_name="testuser1"
        )

    def test_get_me(self):
        # Test as anonymous user
        response = self.client.get("/v4/users/me")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/v4/users/me")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(json["username"], self.user.username)

    def test_update_me(self):
        # Test as anonymous user
        updated_data = {"full_name": "Test User"}
        response = self.client.patch("/v4/users/me", updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user)
        updated_data = {"full_name": "Test User"}
        response = self.client.patch("/v4/users/me", updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(json["full_name"], updated_data["full_name"])


class FollowTestCase(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create(
            username="testuser1", email="testuser1@example.com"
        )
        self.user_b = User.objects.create(
            username="testuser2", email="testuser2@example.com"
        )
        self.user_c = User.objects.create(
            username="testuser3", email="testuser3@example.com"
        )

    def test_follow(self):
        print("SUPP")
        # Test as anonymous user
        response = self.client.post(f"/v4/users/{self.user_a.username}/follow")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user_b)

        # Follow:
        response = self.client.post(f"/v4/users/{self.user_a.username}/follow")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user_a.followers.count(), 1)

        # Unfollow:
        response = self.client.post(f"/v4/users/{self.user_a.username}/unfollow")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user_a.followers.count(), 0)

        # Follow self:
        response = self.client.post(f"/v4/users/{self.user_b.username}/follow")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_followers_following(self):
        Follow.objects.create(follower=self.user_a, followed=self.user_b)
        Follow.objects.create(follower=self.user_c, followed=self.user_b)
        Follow.objects.create(follower=self.user_b, followed=self.user_a)

        response = self.client.get(f"/v4/users/{self.user_b.username}/followers")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(json["count"], 2)

        response = self.client.get(f"/v4/users/{self.user_b.username}/following")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(json["count"], 1)
