from rest_framework import status
from rest_framework.test import APITestCase

from dhanriti.models import Note, Part, Story, User


class NoteTestCase(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create(
            username="testuser", email="testuser1@example.com"
        )
        self.user_b = User.objects.create(
            username="testuser2", email="testuser2@example.com"
        )
        self.story_data = {
            "title": "Test Story 1",
            "description": "Description of Test Story 1",
            "genre": 10,
            "visibility": 3,
            "language": "en",
            "allow_comments": True,
            "author": self.user_a,
        }
        self.story = Story.objects.create(**self.story_data)

        self.part_data = {
            "title": "Test Part 1",
            "content": "Content of Test Part 1",
            "story": self.story,
            "visibility": 3,
        }
        self.part = Part.objects.create(**self.part_data)

        self.story_note_data_a = {
            "story": self.story.external_id,
            "title": "Test story note content",
            "user": self.user_a.id,
        }
        self.story_note_data_b = {
            "story": self.story.external_id,
            "title": "Test story note content",
            "user": self.user_b.id,
        }

        self.part_note_data_a = {
            "part": self.part.external_id,
            "title": "Test part note content",
            "user": self.user_a.id,
        }
        self.part_note_data_b = {
            "part": self.part.external_id,
            "title": "Test part note content",
            "user": self.user_b.id,
        }

        self.note = Note.objects.create(
            story=self.story,
            title="Test note content",
            description="Description of Test note content",
            line=2,
            color="blue",
            user=self.user_a,
        )

    def test_create_story_note(self):
        # Test as anonymous user
        self.client.force_authenticate(user=None)
        response = self.client.post("/v4/notes", self.story_note_data_a, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as reader
        self.client.force_authenticate(user=self.user_b)
        response = self.client.post("/v4/notes", self.story_note_data_b, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test as author
        self.client.force_authenticate(user=self.user_a)
        response = self.client.post("/v4/notes", self.story_note_data_a, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_part_note(self):
        # Test as reader
        self.client.force_authenticate(user=self.user_b)
        response = self.client.post("/v4/notes", self.part_note_data_b, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test as author
        self.client.force_authenticate(user=self.user_a)
        response = self.client.post("/v4/notes", self.part_note_data_a, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_note(self):
        # Test as anonymous user
        self.client.force_authenticate(user=None)
        response = self.client.get("/v4/notes")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get("/v4/notes")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(str(json["count"]), "1")

    def test_patch_note(self):
        update_data = {
            "title": "Test note content updated",
            "description": "Description of Test note content updated",
        }

        # Test as anonymous user
        self.client.force_authenticate(user=None)
        response = self.client.patch(
            f"/v4/notes/{self.note.external_id}", update_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user_a)
        response = self.client.patch(
            f"/v4/notes/{self.note.external_id}", update_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(json["title"], update_data["title"])

    def test_delete_note_as_owner(self):
        # Test as anonymous user
        self.client.force_authenticate(user=None)
        response = self.client.delete(f"/v4/notes/{self.note.external_id}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user_a)
        response = self.client.delete(f"/v4/notes/{self.note.external_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
