from rest_framework import status
from rest_framework.test import APITestCase

from dhanriti.models import Search, Story, User


class SearchResult(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.public_story_data = {
            "title": "Test Story 1",
            "description": "This is public story",
            "genre": 6,
            "visibility": 3,
            "language": "en",
            "allow_comments": True,
            "author": self.user,
        }
        self.private_story_data = {
            "title": "Test Story 2",
            "description": "This is private story",
            "genre": 6,
            "visibility": 1,
            "language": "en",
            "allow_comments": True,
            "author": self.user,
        }
        self.public_story = Story.objects.create(**self.public_story_data)
        self.private_story = Story.objects.create(**self.private_story_data)

    def test_search_results(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/v4/search?query=test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure only public stories are returned
        json = response.json()
        for result in json["stories"]:
            story_id = str(result["visibility"])
            self.assertNotIn(story_id, "1")


class SearchHistory(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", email="testuser@gmail.com")
        self.newuser = User.objects.create(
            username="newuser", email="newuser@gmail.com"
        )
        self.search_term = Search.objects.create(
            user_id=self.user.id, query="DaVinci", search_ip="127.0.0.1"
        )

    def test_search_history(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/v4/search/history")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertIn(
            str(self.search_term.query),
            [str(term["query"]) for term in json["results"]],
        )

        # Test as unauthorised client
        self.client.force_authenticate(user=None)
        response = self.client.get("/v4/search/history")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_search_history(self):
        self.client.force_authenticate(user=self.newuser)
        response = self.client.post(
            "/v4/search/history", {"query": "TestQuery"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test as unauthorised client:
        self.client.force_authenticate(user=None)
        response = self.client.post(
            "/v4/search/history", {"query": "TestQuery"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_search_history(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            f"/v4/search/history/{self.search_term.external_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Ensure other user cannot access or delete:
        self.client.force_authenticate(user=self.newuser)
        response = self.client.delete(
            f"/v4/search/history/{self.search_term.external_id}"
        )  # delete request for search_query by testuser
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
