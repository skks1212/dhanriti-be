from rest_framework.test import APITestCase

from dhanriti.models import Follow, Leaf, Part, Story, User, enums


class NotificationTestCase(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_superuser(
            username="testuser", email="testuser1@example.com"
        )
        self.user_b = User.objects.create(
            username="testuser2", email="testuser2@example.com"
        )
        self.user_c = User.objects.create(
            username="testuser3", email="testuser3@example.com"
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
        self.story_part_data = {
            "title": "Test Part 1",
            "content": "Content of Test Part 3",
            "visibility": 3,
        }
        self.story_part = Part.objects.create(story=self.story, **self.story_part_data)

        self.story_part_data2 = {
            "title": "Test Part 2",
            "content": "Content of Test Part 2",
            "visibility": 3,
        }

        self.leaf_data = {
            "img_url": "https://cdn.dhanriti.net/media/1689260857.jpg",
            "text": "Test Leaf 1",
            "caption": "Caption of Test Leaf 1",
            "visibility": 3,
            "author": self.user_a,
            "claps": 99,
            "reads": 99,
        }
        self.leaf = Leaf.objects.create(**self.leaf_data)

    def test_follow_notification(self):
        self.client.force_authenticate(user=self.user_b)
        self.client.post(
            f"/v4/users/{self.user_a.username}/follow",
            format="json",
        )
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get("/v4/notifications")
        json = response.json()
        self.assertEqual(json["count"], 1)
        self.assertEqual(json["results"][0]["type"], enums.NotificationType.FOLLOW)

    def test_clap_notification(self):
        self.client.force_authenticate(user=self.user_b)
        self.client.post(
            f"/v4/leaves/{self.leaf.url}/clap",
            format="json",
        )
        self.client.post(
            f"/v4/stories/{self.story.url}/parts/{self.story_part.url}/clap",
        )
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get("/v4/notifications")
        json = response.json()
        self.assertEqual(json["count"], 3)
        self.assertEqual(json["results"][0]["type"], enums.NotificationType.CLAP)
        self.assertEqual(
            json["results"][1]["type"], enums.NotificationType.CLAP_MILESTONE
        )
        self.assertEqual(json["results"][2]["type"], enums.NotificationType.CLAP)

    def test_comment_notification(self):
        self.client.force_authenticate(user=self.user_b)
        self.client.post(
            f"/v4/leaves/{self.leaf.url}/comments",
            format="json",
            data={"comment": "Test Comment"},
        )
        self.client.post(
            f"/v4/stories/{self.story.url}/parts/{self.story_part.url}/comments",
            format="json",
            data={"comment": "Test Comment"},
        )
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get("/v4/notifications")
        json = response.json()
        self.assertEqual(json["count"], 2)
        self.assertEqual(json["results"][0]["type"], enums.NotificationType.COMMENT)
        self.assertEqual(json["results"][1]["type"], enums.NotificationType.COMMENT)

    def test_comment_like_notification(self):
        self.client.force_authenticate(user=self.user_b)
        self.client.post(
            f"/v4/leaves/{self.leaf.url}/comments",
            format="json",
            data={"comment": "Test Comment"},
        )
        self.client.post(
            f"/v4/stories/{self.story.url}/parts/{self.story_part.url}/comments",
            format="json",
            data={"comment": "Test Comment"},
        )
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get("/v4/notifications")
        json = response.json()
        self.assertEqual(json["count"], 2)
        self.assertEqual(json["results"][0]["type"], enums.NotificationType.COMMENT)
        self.assertEqual(json["results"][1]["type"], enums.NotificationType.COMMENT)

    def test_part_added_notification(self):
        self.client.force_authenticate(user=self.user_b)
        self.client.post(
            f"/v4/stories/{self.story.url}/parts/{self.story_part.url}/clap",
            format="json",
        )

        Follow.objects.create(follower=self.user_c, followed=self.user_a)

        self.client.force_authenticate(user=self.user_a)
        self.client.post(
            f"/v4/stories/{self.story.url}/parts",
            format="json",
            data=self.story_part_data2,
        )

        self.client.force_authenticate(user=self.user_b)
        response = self.client.get("/v4/notifications")
        json = response.json()
        self.assertEqual(json["count"], 1)
        self.assertEqual(
            json["results"][0]["type"], enums.NotificationType.PART_PUBLISH
        )

        self.client.force_authenticate(user=self.user_c)
        response = self.client.get("/v4/notifications")
        json = response.json()
        self.assertEqual(json["count"], 1)
        self.assertEqual(
            json["results"][0]["type"], enums.NotificationType.PART_PUBLISH
        )

    def test_read_milestone_notification(self):
        self.client.force_authenticate(user=self.user_b)
        self.client.get(f"/v4/leaves/{self.leaf.url}")
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get("/v4/notifications")
        json = response.json()
        self.assertEqual(json["count"], 1)
        self.assertEqual(
            json["results"][0]["type"], enums.NotificationType.LEAF_VIEWS_MILESTONE
        )
