from rest_framework import status
from rest_framework.test import APITestCase

from dhanriti.models import Leaf, Shelf, Story, User


class ShelfTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            username="testuser1", email="testuser1@example.com"
        )
        self.user2 = User.objects.create(
            username="testuser2", email="testuser2@example.com"
        )
        self.shelf_data = {
            "name": "Test Shelf",
            "description": "Description of Test Shelf",
            "visibility": 3,
        }

        self.shelf_data2 = {
            "name": "Test Shelf 2",
            "description": "Description of Test Shelf 2",
            "visibility": 3,
        }

        self.private_shelf_data = {
            "name": "Private Shelf",
            "description": "Description of Private Shelf",
            "visibility": 1,
        }

        self.shelf2 = Shelf.objects.create(**self.shelf_data2, user_id=self.user1.id)
        self.private_shelf = Shelf.objects.create(
            **self.private_shelf_data, user_id=self.user1.id
        )

    def test_create_shelf(self):
        # Test as anonymous user
        response = self.client.post(
            f"/v4/users/{self.user1.username}/shelves", self.shelf_data
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as different user
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(
            f"/v4/users/{self.user1.username}/shelves", self.shelf_data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            f"/v4/users/{self.user1.username}/shelves", self.shelf_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_shelf(self):
        # Test as anonymous user
        # public shelf
        response = self.client.get(
            f"/v4/users/{self.user1.username}/shelves/{self.shelf2.external_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # private shelf
        response = self.client.get(
            f"/v4/users/{self.user1.username}/shelves/{self.private_shelf.external_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test as owner of shelf
        self.client.force_authenticate(user=self.user1)
        # private shelf
        response = self.client.get(
            f"/v4/users/{self.user1.username}/shelves/{self.private_shelf.external_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test with different user in url than that of whom it belongs to
        self.client.force_authenticate(user=self.user2)
        # public shelf
        response = self.client.get(
            f"/v4/users/{self.user2.username}/shelves/{self.shelf2.external_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_shelf(self):
        updated_data = {
            "name": "Updated Shelf",
        }
        # Test as anonymous user
        response = self.client.patch(
            f"/v4/users/{self.user1.username}/shelves/{self.shelf2.external_id}",
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as different user
        self.client.force_authenticate(user=self.user2)
        response = self.client.patch(
            f"/v4/users/{self.user1.username}/shelves/{self.shelf2.external_id}",
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(
            f"/v4/users/{self.user1.username}/shelves/{self.shelf2.external_id}",
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_shelf(self):
        # Test as anonymous user
        response = self.client.delete(
            f"/v4/users/{self.user1.username}/shelves/{self.shelf2.external_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as different user
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(
            f"/v4/users/{self.user1.username}/shelves/{self.shelf2.external_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(
            f"/v4/users/{self.user1.username}/shelves/{self.shelf2.external_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class AddToShelfTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            username="testuser1", email="testuser1@example.com"
        )
        self.user2 = User.objects.create(
            username="testuser2", email="testuser2@example.com"
        )
        self.shelf_data = {
            "name": "Test Shelf",
            "description": "Description of Test Shelf",
            "visibility": 3,
        }
        self.shelf = Shelf.objects.create(**self.shelf_data, user_id=self.user1.id)

        self.story_data_a = {
            "title": "Test Story 1",
            "description": "Description of Test Story 1",
            "genre": 10,
            "visibility": 3,
            "language": "en",
            "allow_comments": True,
            "author": self.user1,
        }
        self.story = Story.objects.create(**self.story_data_a)

        self.leaf_data_a = {
            "text": "Test Leaf 1",
            "caption": "Caption of Test Leaf 1",
            "visibility": 3,
            "author": self.user2,
        }
        self.leaf = Leaf.objects.create(**self.leaf_data_a)

    def test_add_story(self):
        # Test as anonymous user
        response = self.client.post(
            f"/v4/users/{self.user1.username}/shelves/{self.shelf.external_id}/add_or_remove",
            data={"story_id": self.story.external_id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as different user
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(
            f"/v4/users/{self.user1.username}/shelves/{self.shelf.external_id}/add_or_remove",
            data={"story_id": self.story.external_id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            f"/v4/users/{self.user1.username}/shelves/{self.shelf.external_id}/add_or_remove",
            data={"story_id": self.story.external_id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_leaf(self):
        # Test as anonymous user
        response = self.client.post(
            f"/v4/users/{self.user1.username}/shelves/{self.shelf.external_id}/add_or_remove",
            data={"leaf_id": self.leaf.external_id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as different user
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(
            f"/v4/users/{self.user1.username}/shelves/{self.shelf.external_id}/add_or_remove",
            data={"leaf_id": self.leaf.external_id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            f"/v4/users/{self.user1.username}/shelves/{self.shelf.external_id}/add_or_remove",
            data={"leaf_id": self.leaf.external_id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
