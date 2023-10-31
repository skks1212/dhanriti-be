from rest_framework import status
from rest_framework.test import APITestCase

from dhanriti.models import Follow, Leaf, LeafRead, User


class LeafTestCase(APITestCase):
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

        Follow.objects.create(follower=self.user_c, followed=self.user_b)

        self.leaf_data_a = {
            "img_url": "https://cdn.dhanriti.net/media/1689260857.jpg",
            "text": "Test Leaf 1",
            "caption": "Caption of Test Leaf 1",
            "visibility": 3,
            "author": self.user_b,
        }
        self.leaf_data_b = {
            "img_url": "https://cdn.dhanriti.net/media/1689260857.jpg",
            "text": "Test Leaf 2",
            "caption": "Caption of Test Leaf 2",
            "visibility": 3,
            "author": self.user_a,
        }
        self.leaf_data_c = {
            "img_url": "https://cdn.dhanriti.net/media/1689260857.jpg",
            "text": "Test Leaf 3",
            "caption": "Caption of Test Leaf 3",
            "visibility": 3,
        }

        self.leaf_a = Leaf.objects.create(**self.leaf_data_a)
        self.leaf_b = Leaf.objects.create(**self.leaf_data_b)

    def test_filter_by_author(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f"/v4/leaves?author={self.user_a.username}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(json["count"], 1)

    def test_filter_by_followed(self):
        self.client.force_authenticate(user=self.user_c)
        response = self.client.get("/v4/leaves?following=True")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(json["count"], 1)

    def test_filter_by_unread(self):
        self.client.force_authenticate(user=self.user_c)
        LeafRead.objects.create(leaf=self.leaf_a, reader=self.user_c)
        response = self.client.get("/v4/leaves?unread=True")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(json["count"], 1)

    def test_retrieve_leaf(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f"/v4/leaves/{self.leaf_a.url}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(json["text"], self.leaf_a.text)
