from rest_framework import status
from rest_framework.test import APITestCase

from dhanriti.models import Comment, Leaf, Part, Story, User


class StoryCommentTestCase(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create(
            username="testuser1", email="testuser1@example.com"
        )
        self.user_b = User.objects.create(
            username="testuser2", email="testuser2@example.com"
        )
        self.shelf_data = {"name": "TestShelf", "visibility": 3, "user": self.user_a}
        self.story_data_a = {
            "title": "Test Story 1",
            "description": "Description of Test Story 1",
            "genre": 10,
            "visibility": 3,
            "language": "en",
            "allow_comments": True,
            "author": self.user_b,
        }
        self.story_data_b = {
            "title": "Test Story 2",
            "description": "Description of Test Story 2",
            "genre": 10,
            "visibility": 3,
            "language": "en",
            "allow_comments": False,
            "author": self.user_b,
        }

        self.story_a = Story.objects.create(**self.story_data_a)
        self.story_b = Story.objects.create(**self.story_data_b)

        self.story_part_data_a1 = {
            "title": "Test Part 1",
            "content": "Content of Test Part 3",
            "visibility": 3,
        }
        self.story_part_data_b1 = {
            "title": "Test Part 2",
            "content": "Content of Test Part 2",
            "visibility": 3,
        }

        self.story_part_a1 = Part.objects.create(
            story=self.story_a, **self.story_part_data_a1
        )
        self.story_part_b1 = Part.objects.create(
            story=self.story_b, **self.story_part_data_b1
        )

        self.comment_data_a = {
            "comment": "Test Comment 1",
            "commenter": self.user_a,
        }
        self.comment_data_b = {
            "comment": "Test Comment 2",
        }
        self.comment_a = Comment.objects.create(
            **self.comment_data_a, part=self.story_part_a1
        )

    def test_create_comment(self):
        # Test as anonymous user
        response = self.client.post(
            f"/v4/stories/{self.story_a.url}/parts/{self.story_part_a1.url}/comments",
            self.comment_data_b,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user_a)
        response = self.client.post(
            f"/v4/stories/{self.story_a.url}/parts/{self.story_part_a1.url}/comments",
            self.comment_data_b,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_allow_comments(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.post(
            f"/v4/stories/{self.story_b.url}/parts/{self.story_part_b1.url}/comments",
            self.comment_data_b,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_comments(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(
            f"/v4/stories/{self.story_a.url}/parts/{self.story_part_a1.url}/comments",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch(self):
        # Test as anonymous user
        response = self.client.patch(
            f"/v4/stories/{self.story_a.url}/parts/{self.story_part_a1.url}/comments/{self.comment_a.external_id}",
            {"comment": "New Comment"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user_a)
        response = self.client.patch(
            f"/v4/stories/{self.story_a.url}/parts/{self.story_part_a1.url}/comments/{self.comment_a.external_id}",
            {"comment": "New Comment"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(json["comment"], "New Comment")

    def test_delete(self):
        # Test as anonymous user
        response = self.client.delete(
            f"/v4/stories/{self.story_a.url}/parts/{self.story_part_a1.url}/comments/{self.comment_a.external_id}",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user_a)
        response = self.client.delete(
            f"/v4/stories/{self.story_a.url}/parts/{self.story_part_a1.url}/comments/{self.comment_a.external_id}",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class LeafCommentTestCase(APITestCase):
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
        self.leaf_data_a = {
            "text": "Test Leaf 1",
            "caption": "Caption of Test Leaf 1",
            "visibility": 3,
            "author": self.user_b,
        }
        self.leaf_data_b = {
            "text": "Test Leaf 2",
            "caption": "Caption of Test Leaf 2",
            "visibility": 1,
            "author": self.user_b,
        }

        self.leaf_a = Leaf.objects.create(**self.leaf_data_a)
        self.leaf_b = Leaf.objects.create(**self.leaf_data_b)

        self.comment_data_a = {
            "comment": "Test Comment 1",
            "commenter": self.user_a,
        }
        self.comment_data_b = {
            "comment": "Test Comment 2",
        }

        self.comment_a = Comment.objects.create(**self.comment_data_a, leaf=self.leaf_a)

        self.comment_data_c = {
            "comment": "Test Reply Comment 3",
            "commenter": self.user_c,
            "parent": self.comment_a,
        }
        self.comment_c = Comment.objects.create(**self.comment_data_c, leaf=self.leaf_a)

    def test_create_comment(self):
        # Test as anonymous user
        response = self.client.post(
            f"/v4/leaves/{self.leaf_a.url}/comments",
            self.comment_data_b,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user_a)
        response = self.client.post(
            f"/v4/leaves/{self.leaf_a.url}/comments",
            self.comment_data_b,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_comment_on_private_leaf(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.post(
            f"/v4/leaves/{self.leaf_b.url}/comments",
            self.comment_data_b,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_comments(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(
            f"/v4/leaves/{self.leaf_a.url}/comments",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_comments_on_private_leaf(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(
            f"/v4/leaves/{self.leaf_b.url}/comments",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch(self):
        # Test as anonymous user
        response = self.client.patch(
            f"/v4/leaves/{self.leaf_a.url}/comments/{self.comment_a.external_id}",
            {"comment": "New Comment"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user_a)
        response = self.client.patch(
            f"/v4/leaves/{self.leaf_a.url}/comments/{self.comment_a.external_id}",
            {"comment": "New Comment"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(json["comment"], "New Comment")

    def test_delete(self):
        # Test as anonymous user
        response = self.client.delete(
            f"/v4/leaves/{self.leaf_a.url}/comments/{self.comment_a.external_id}",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user_a)
        response = self.client.delete(
            f"/v4/leaves/{self.leaf_a.url}/comments/{self.comment_a.external_id}",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_reply(self):
        # Test as anonymous user
        response = self.client.post(
            f"/v4/leaves/{self.leaf_a.url}/comments",
            {
                "comment": "Reply comment",
                "parent_comment": f"{self.comment_a.external_id}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user_b)
        response = self.client.post(
            f"/v4/leaves/{self.leaf_a.url}/comments",
            {
                "comment": "Reply comment",
                "parent_comment": f"{self.comment_a.external_id}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_patch_reply(self):
        # Test as anonymous user
        response = self.client.patch(
            f"/v4/leaves/{self.leaf_a.url}/comments/{self.comment_c.external_id}",
            {"comment": "Edited Reply"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user_c)
        response = self.client.patch(
            f"/v4/leaves/{self.leaf_a.url}/comments/{self.comment_c.external_id}",
            {"comment": "Edited Reply"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(json["comment"], "Edited Reply")

    def test_delete_reply(self):
        # Test as anonymous user
        response = self.client.delete(
            f"/v4/leaves/{self.leaf_a.url}/comments/{self.comment_c.external_id}",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user_c)
        response = self.client.delete(
            f"/v4/leaves/{self.leaf_a.url}/comments/{self.comment_c.external_id}",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
