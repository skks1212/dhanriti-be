from django.test import RequestFactory
from rest_framework.test import APITestCase

from dhanriti.models import Clap, Comment, Leaf, Part, Story, StoryRead, User
from dhanriti.tasks.update_count_tasks import update_reads_claps_comments


class CronJob(APITestCase):
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
        self.story_data_a = {
            "title": "Test Story 1",
            "description": "Description of Test Story 1",
            "genre": 10,
            "visibility": 3,
            "language": "en",
            "allow_comments": True,
            "author": self.user_b,
        }
        self.story_a = Story.objects.create(**self.story_data_a)

        self.part_one_data = {
            "title": "Test 1",
            "content": "Description of Part 1",
            "visibility": 3,
        }

        self.part_two_data = {
            "title": "Test 2",
            "content": "Description of Part 2",
            "visibility": 3,
        }
        self.story_one_part_one = Part.objects.create(
            **self.part_one_data, story=self.story_a
        )
        self.story_one_part_two = Part.objects.create(
            **self.part_two_data, story=self.story_a
        )

        self.leaf_data = {
            "text": "Test Leaf",
            "caption": "Caption of Leaf",
            "visibility": 3,
            "author": self.user_b,
        }
        self.leaf = Leaf.objects.create(**self.leaf_data)

    def test_update_counts(self):
        factory = RequestFactory()
        request = factory.get("/v4/stories")
        self.client.force_authenticate(user=None)
        StoryRead.objects.create(part=self.story_one_part_one, reader=self.user_b)
        Clap.objects.create(part=self.story_one_part_two, clapper=self.user_c)
        Clap.objects.create(leaf=self.leaf, clapper=self.user_c)
        Comment.objects.create(
            part=self.story_one_part_one,
            comment="TestComment",
            commenter=self.user_b,
        )
        update_reads_claps_comments(
            request=request,
            cron_key="3z1OxJQuzkvKKw9ZJDWnZE8R8SuysN7ghdFzwk870UzLXB84ww",
        )
        response = self.client.get(f"/v4/stories/{self.story_a.url}")
        json = response.json()
        self.assertEqual(str(json["reads"]), "1")
        self.assertEqual(str(json["comments"]), "1")
        self.assertEqual(str(json["claps"]), "1")

        response = self.client.get(f"/v4/leaves/{self.leaf.url}")
        json = response.json()
        self.assertEqual(str(json["claps"]), "1")
