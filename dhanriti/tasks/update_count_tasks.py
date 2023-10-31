from celery import shared_task
from django.http import HttpResponse, HttpResponseForbidden

from ..models import Clap, Comment, CommentLike, Leaf, LeafRead, Story, StoryRead


@shared_task
def update_reads_claps_comments(request=None, cron_key=None):
    if cron_key and cron_key != "3z1OxJQuzkvKKw9ZJDWnZE8R8SuysN7ghdFzwk870UzLXB84ww":
        return HttpResponseForbidden("Incorrect password")

    if cron_key is None:
        pass
    stories = Story.objects.all().prefetch_related("parts")
    leaves = Leaf.objects.all()
    comments = Comment.objects.all()
    for story in stories:
        reads_count = StoryRead.objects.filter(part__story=story).count()
        story_claps_count = Clap.objects.filter(part__story=story).count()
        story_comments_count = Comment.objects.filter(part__story=story).count()
        story.reads = reads_count
        story.claps = story_claps_count
        story.comments = story_comments_count
        story.save()
    for leaf in leaves:
        leaf_read_count = LeafRead.objects.filter(leaf=leaf).count()
        leaf_claps_count = Clap.objects.filter(leaf=leaf).count()
        leaf_comments_count = Comment.objects.filter(leaf=leaf).count()
        leaf.claps = leaf_claps_count
        leaf.comments = leaf_comments_count
        leaf.reads = leaf_read_count
        leaf.save()
    for comment in comments:
        comment_likes_count = CommentLike.objects.filter(comment=comment).count()
        comment.likes = comment_likes_count
        comment.save()

    if cron_key is not None:
        return HttpResponse("Task Performed Successfully")
