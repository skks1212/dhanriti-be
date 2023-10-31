from rest_framework import status
from rest_framework.test import APITestCase

from dhanriti.models import Part, Shelf, ShelfStory, Story, User


class StoryTestCase(APITestCase):
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
            "genre": 5,
            "visibility": 3,
            "language": "en",
            "allow_comments": True,
            "author": self.user_b,
        }

        self.story_data_c = {
            "title": "Test Story 3",
            "description": "Description of Test Story 3",
            "genre": 5,
            "visibility": 3,
            "language": "en",
            "allow_comments": True,
        }

        self.story_data_d = {
            "title": "Test Story 4",
            "description": "Description of Test Story 4",
            "genre": 6,
            "visibility": 3,
            "language": "en",
            "allow_comments": True,
            "author": self.user_a,
        }

        self.story_data_e = {
            "title": "Test Story 5",
            "description": "Description of Test Story 5",
            "genre": 6,
            "visibility": 3,
            "language": "en",
            "allow_comments": True,
            "author": self.user_a,
            "explicit": True,
        }

        self.story_data_f = {
            "title": "Test Story 6",
            "description": "Description of Test Story 6",
            "genre": 6,
            "visibility": 3,
            "language": "en",
            "allow_comments": True,
            "author": self.user_a,
            "preference_points": -1,
        }

        self.story_a = Story.objects.create(**self.story_data_a)
        self.story_b = Story.objects.create(**self.story_data_b)
        self.story_d = Story.objects.create(**self.story_data_d)
        self.story_e = Story.objects.create(**self.story_data_e)
        self.story_f = Story.objects.create(**self.story_data_f)

        self.part_data_a1 = {
            "title": "Test Part 1",
            "content": "Content of Test Part 1",
            "story": self.story_a,
            "visibility": 3,
        }
        self.part_data_a2 = {
            "title": "Test Part 2",
            "content": "Content of Test Part 2",
            "story": self.story_a,
            "visibility": 3,
        }
        self.part_data_b = {
            "title": "Test Part 2",
            "content": "Content of Test Part 2",
            "story": self.story_b,
            "visibility": 3,
        }
        self.part_data_d = {
            "title": "Test Part 4",
            "content": "Content of Test Part",
            "story": self.story_d,
            "visibility": 3,
        }
        self.part_data_e = {
            "title": "Test Part 5",
            "content": "Content of Test Part",
            "story": self.story_e,
            "visibility": 3,
        }
        self.part_data_f = {
            "title": "Test Part 6",
            "content": "Content of Test Part",
            "story": self.story_f,
            "visibility": 3,
        }

        self.part_a1 = Part.objects.create(**self.part_data_a1)
        self.part_a2 = Part.objects.create(**self.part_data_a2)
        self.part_b = Part.objects.create(**self.part_data_b)
        self.part_d = Part.objects.create(**self.part_data_d)
        self.part_e = Part.objects.create(**self.part_data_e)
        self.part_f = Part.objects.create(**self.part_data_f)

        self.shelf = Shelf.objects.create(**self.shelf_data)

        self.shelf_story_a = ShelfStory.objects.create(
            story=self.story_a, shelf=self.shelf
        )

    def test_filter_shelf_id(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f"/v4/stories?shelf_id={self.shelf.external_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(str(json["count"]), "1")
        self.assertIn(
            str(self.story_a.external_id),
            [str(story["external_id"]) for story in json["results"]],
        )

    def test_filter_genre(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f"/v4/stories?genre={self.story_a.genre}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(str(json["count"]), "1")
        self.assertIn(
            str(self.story_a.external_id),
            [str(story["external_id"]) for story in json["results"]],
        )

    def test_filter_author(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f"/v4/stories?author={self.user_a.username}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(str(json["count"]), "2")
        self.assertIn(
            str(self.story_d.external_id),
            [str(story["external_id"]) for story in json["results"]],
        )
        self.assertIn(
            str(self.story_f.external_id),
            [str(story["external_id"]) for story in json["results"]],
        )

    def test_filter_shortread(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/v4/stories?short_read=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(str(json["count"]), "2")
        self.assertNotIn(
            str(self.story_a.external_id),
            [str(story["external_id"]) for story in json["results"]],
        )

    def test_filter_explicit(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/v4/stories?allow_explicit=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(str(json["count"]), "4")
        self.assertIn(
            str(self.story_e.external_id),
            [str(story["external_id"]) for story in json["results"]],
        )

    def test_create_story(self):
        # Test as anonymous user
        self.client.force_authenticate(user=None)
        story_response = self.client.post(
            "/v4/stories", self.story_data_c, format="json"
        )
        self.assertEqual(story_response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user_a)
        story_response = self.client.post(
            "/v4/stories", self.story_data_c, format="json"
        )
        self.assertEqual(story_response.status_code, status.HTTP_201_CREATED)

    def test_my_stories(self):
        # Test as anonymous user
        self.client.force_authenticate(user=None)
        response = self.client.get("/v4/stories/edit")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test as authenticated user
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get("/v4/stories/edit")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(str(json["count"]), "2")

    def test_patch_story(self):
        self.client.force_authenticate(user=self.user_b)
        response = self.client.patch(
            f"/v4/stories/{self.story_a.url}",
            {"title": "New Title"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(json["title"], "New Title")

    def test_delete_story(self):
        self.client.force_authenticate(user=self.user_b)
        response = self.client.delete(f"/v4/stories/{self.story_a.url}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Story.objects.count(), 4)

    def test_recommended_stories(self):
        self.client.force_authenticate(user=self.user_c)
        self.client.get(f"/v4/stories/{self.story_f.url}/parts/{self.part_f.url}")
        response = self.client.get("/v4/stories?allow_explicit=true&recommended=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(str(json["count"]), "2")
        self.assertIn(
            str(self.story_e.external_id),
            [str(story["external_id"]) for story in json["results"]],
        )
        self.assertIn(
            str(self.story_d.external_id),
            [str(story["external_id"]) for story in json["results"]],
        )


class PartTestCase(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create(
            username="testuser1", email="testuser1@example.com"
        )
        self.shelf_data = {"name": "TestShelf", "visibility": 3, "user": self.user_a}
        self.story_data_a = {
            "title": "Test Story 1",
            "description": "Description of Test Story 1",
            "genre": 10,
            "visibility": 3,
            "language": "en",
            "allow_comments": True,
            "author": self.user_a,
        }
        self.story_a = Story.objects.create(**self.story_data_a)
        self.story_part_data_a1 = {
            "title": "Test Part 1",
            "content": "",
            "visibility": 3,
        }
        self.story_part_data_a2 = {
            "title": "Test Part 2",
            "content": "",
            "visibility": 3,
        }
        self.story_part_test_html = {
            "title": "Test Part 3",
            "content": "",
            "visibility": 3,
        }

        self.story_part_a1 = Part.objects.create(
            story=self.story_a, **self.story_part_data_a1
        )
        self.story_part_a2 = Part.objects.create(
            story=self.story_a, **self.story_part_test_html
        )

    def test_create_part(self):
        self.client.force_authenticate(user=self.user_a)
        part_response = self.client.post(
            f"/v4/stories/{self.story_a.url}/parts",
            self.story_part_data_a2,
            format="json",
        )
        self.assertEqual(part_response.status_code, status.HTTP_201_CREATED)

    def test_create_part_valid_html(self):
        self.client.force_authenticate(user=self.user_a)
        part_response = self.client.patch(
            f"/v4/stories/{self.story_a.url}/parts/{self.story_part_a2.url}",
            {
                "content": "Normal Text<div><br></div><div><b>Bold</b></div><br><div><br></div><div><strike>Strike "
                "through</strike></div><div style='text-align: right;'>Right</div>"
            },
            format="json",
        )
        self.assertEqual(part_response.status_code, status.HTTP_200_OK)

    def test_create_part_invalid_html_style(self):
        self.client.force_authenticate(user=self.user_a)
        part_response = self.client.patch(
            f"/v4/stories/{self.story_a.url}/parts/{self.story_part_a2.url}",
            {
                "content": "<div style='color:blue;text-align:center'>This is a sample text</div>"
            },
            format="json",
        )
        self.assertEqual(part_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_part_invalid_hrml_unclosed_tag(self):
        self.client.force_authenticate(user=self.user_a)
        part_response = self.client.patch(
            f"/v4/stories/{self.story_a.url}/parts/{self.story_part_a2.url}",
            {"content": "<div><br></div><div><b>Bold</b>"},
            format="json",
        )
        self.assertEqual(part_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_part_invalid_hyml_invalid_tag(self):
        self.client.force_authenticate(user=self.user_a)
        part_response = self.client.patch(
            f"/v4/stories/{self.story_a.url}/parts/{self.story_part_a2.url}",
            {
                "content": "<div><br></div><div><b>Bold</b></div><br><p>Paragraph tag</p>"
            },
            format="json",
        )
        self.assertEqual(part_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_part(self):
        self.client.force_authenticate(user=self.user_a)
        part_response = self.client.patch(
            f"/v4/stories/{self.story_a.url}/parts/{self.story_part_a1.url}",
            {"title": "New Title"},
            format="json",
        )
        self.assertEqual(part_response.status_code, status.HTTP_200_OK)
        json = part_response.json()
        self.assertEqual(json["title"], "New Title")

    def test_get_part(self):
        self.client.force_authenticate(user=None)
        part_response = self.client.get(
            f"/v4/stories/{self.story_a.url}/parts/{self.story_part_a1.url}",
            format="json",
        )
        self.assertEqual(part_response.status_code, status.HTTP_200_OK)
        json = part_response.json()
        self.assertEqual(json["title"], self.story_part_data_a1["title"])

    def test_delete_part(self):
        self.client.force_authenticate(user=self.user_a)
        part_response = self.client.delete(
            f"/v4/stories/{self.story_a.url}/parts/{self.story_part_a2.url}",
            format="json",
        )
        self.assertEqual(part_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Part.objects.count(), 1)
