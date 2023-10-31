from rest_framework import status
from rest_framework.test import APITestCase

from dhanriti.models import Award, Awarded, Part, Story, User


class AwardTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin", password="adminpassword"
        )
        self.award_data = {
            "name": "Gold",
            "cost": 100.00,
        }

    def test_create_award(self):
        # Test as admin
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post("/v4/awards", self.award_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test as client
        self.client.force_authenticate(user=None)
        response = self.client.post("/v4/awards", self.award_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_awards(self):
        response = self.client.get("/v4/badges")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertTrue("results" in json)

    def test_retrieve_award(self):
        created_award = Award.objects.create(**self.award_data)
        response = self.client.get(f"/v4/awards/{created_award.external_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertTrue("name" in json)

    def test_update_award(self):
        # Test as Admin
        self.client.force_authenticate(user=self.admin_user)
        created_award = Award.objects.create(**self.award_data)
        updated_data = {"cost": 250.00}
        response = self.client.patch(
            f"/v4/awards/{created_award.external_id}", updated_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(float(json["cost"]), float(updated_data["cost"]))

        # Test as Client
        self.client.force_authenticate(user=None)
        response = self.client.patch(
            f"/v4/awards/{created_award.external_id}", updated_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_award(self):
        # Test as Admin
        self.client.force_authenticate(user=self.admin_user)
        created_award = Award.objects.create(**self.award_data)
        response = self.client.delete(f"/v4/awards/{created_award.external_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Test as Client
        self.client.force_authenticate(user=None)
        response = self.client.delete(f"/v4/awards/{created_award.external_id}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AwardedTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="testuser2", email="testuser2@example.com"
        )
        self.user_b = User.objects.create(
            username="testuser3", email="testuser3@example.com"
        )
        self.story_data = {
            "title": "Yatra Tatra Sarvatra",
            "description": "World through the lens of Advaita Vedanta",
            "genre": 10,
            "visibility": 3,
            "language": "en",
            "allow_comments": True,
            "author": self.user,
        }
        self.story = Story.objects.create(**self.story_data)
        self.part_one_data = {
            "title": "What am I?",
            "content": "I am not the body, the mind, the intellect, the panchabhoota. I am the form of etarnal "
            "consciousness and bliss",
            "visibility": 3,
            "story": self.story,
        }

        self.part_two_data = {
            "title": "Why am I here?",
            "content": "Avidya i.e. thinking I am different from the Brahmm i.e. eternal Consciousness",
            "visibility": 3,
            "story": self.story,
        }
        self.part_one = Part.objects.create(**self.part_one_data)
        self.part_two = Part.objects.create(**self.part_two_data)
        self.goldaward = Award.objects.create(name="Gold", cost=100)
        self.silveraward = Award.objects.create(name="Silver", cost=50)
        self.awarded_one = Awarded.objects.create(
            award=self.goldaward,
            part=self.part_one,
            user=self.user_b,
            comment="Interesting",
        )
        self.awarded_two = Awarded.objects.create(
            award=self.silveraward,
            part=self.part_two,
            user=self.user_b,
            comment="Amazing",
        )

    def test_awarded_storyURL(self):
        url = f"/v4/stories/{self.story.url}/awards"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertTrue("results" in json)
        self.assertEqual(len(json["results"]), 2)

    def test_awarded_partURL(self):
        url = f"/v4/parts/{self.part_one.url}/awards"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertTrue("results" in json)
        self.assertEqual(len(json["results"]), 1)
