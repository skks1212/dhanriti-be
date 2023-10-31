from rest_framework import status
from rest_framework.test import APITestCase

from dhanriti.models import AssignedBadge, Badge, User


class BadgeTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin", password="adminpassword"
        )
        self.badge_data = {
            "name": "Pirate",
            "description": "Read 100 stories",
        }

    def test_create_badge(self):
        # Test as Admin
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post("/v4/badges", self.badge_data, format="json")
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test as Client
        self.client.force_authenticate(user=None)
        response = self.client.post("/v4/badges", self.badge_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_badges(self):
        url = "/v4/badges"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertTrue("results" in json)

    def test_retrieve_badge(self):
        created_badge = Badge.objects.create(**self.badge_data)
        response = self.client.get(f"/v4/badges/{created_badge.external_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertTrue("name" in json)

    def test_update_badge(self):
        # Test as Admin
        self.client.force_authenticate(user=self.admin_user)
        created_badge = Badge.objects.create(**self.badge_data)
        updated_data = {
            "name": "Pirate Pro",
            "description": "Read 200 stories",
        }
        response = self.client.patch(
            f"/v4/badges/{created_badge.external_id}", updated_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(json["name"], updated_data["name"])
        self.assertEqual(json["description"], updated_data["description"])

        # Test as Client
        self.client.force_authenticate(user=None)
        response = self.client.patch(
            f"/v4/badges/{created_badge.external_id}", updated_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_badge(self):
        # Test as Admin
        self.client.force_authenticate(user=self.admin_user)
        created_badge = Badge.objects.create(**self.badge_data)
        response = self.client.delete(f"/v4/badges/{created_badge.external_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Test as Client
        self.client.force_authenticate(user=None)
        response = self.client.delete(f"/v4/badges/{created_badge.external_id}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AssignedBadgeViewSetTestCase(APITestCase):
    authentication_classes = []

    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.badge = Badge.objects.create(name="Test Badge")
        self.assigned_badge = AssignedBadge.objects.create(
            user=self.user, badge=self.badge
        )

    def test_user_badges(self):
        url = "/v4/users/testuser/badges"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["badge"]["name"], self.badge.name)
