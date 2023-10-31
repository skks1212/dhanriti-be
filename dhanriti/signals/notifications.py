from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from dhanriti.models import (
    Clap,
    Comment,
    CommentLike,
    Follow,
    LeafRead,
    Notification,
    Part,
    Report,
    StoryRead,
    User,
)
from dhanriti.models.enums import NotificationType, VisibilityType
from dhanriti.serializers import (
    CommentSerializer,
    LeafSerializer,
    StoryPartSerializer,
    StorySerializer,
    UserPublicSerializer,
)
from dhanriti.serializers.reports import ReportSerializer


@receiver(
    post_save,
    sender=Follow,
    dispatch_uid="add_notification_follow",
)
def user_followed(sender, instance: Follow, created, raw, **kwargs):
    if not created or raw:
        # Ignore if it's not a new Follow or if it's a raw signal
        return
    Notification.objects.create(
        user=instance.followed,
        type=NotificationType.FOLLOW,
        content={
            "user": UserPublicSerializer(instance.follower).data,
        },
    )


@receiver(
    post_save,
    sender=Clap,
    dispatch_uid="add_notification_clap",
)
def user_clapped(sender, instance: Clap, created, raw, **kwargs):
    if not created or raw:
        # Ignore if it's not a new Clap or if it's a raw signal
        return
    if instance.leaf and instance.clapper != instance.leaf.author:
        Notification.objects.create(
            user=instance.leaf.author,
            type=NotificationType.CLAP,
            content={
                "user": UserPublicSerializer(instance.clapper).data,
                "leaf": LeafSerializer(instance.leaf).data,
            },
        )
    if instance.part and instance.clapper != instance.part.story.author:
        Notification.objects.create(
            user=instance.part.story.author,
            type=NotificationType.CLAP,
            content={
                "user": UserPublicSerializer(instance.clapper).data,
                "part": StoryPartSerializer(instance.part).data,
            },
        )


@receiver(post_save, sender=Comment, dispatch_uid="add_notification_comment")
def user_commented(sender, instance: Comment, created, raw, **kwargs):
    if not created or raw:
        # Ignore if it's not a new Comment or if it's a raw signal
        return
    if instance.leaf and instance.commenter != instance.leaf.author:
        Notification.objects.create(
            user=instance.leaf.author,
            type=NotificationType.COMMENT,
            content={
                "user": UserPublicSerializer(instance.commenter).data,
                "leaf": LeafSerializer(instance.leaf).data,
                "comment": CommentSerializer(instance).data,
            },
        )
    if instance.part and instance.commenter != instance.part.story.author:
        Notification.objects.create(
            user=instance.part.story.author,
            type=NotificationType.COMMENT,
            content={
                "user": UserPublicSerializer(instance.commenter).data,
                "part": StoryPartSerializer(instance.part).data,
                "comment": CommentSerializer(instance).data,
            },
        )
    if instance.parent and instance.parent.commenter != instance.commenter:
        Notification.objects.create(
            user=instance.parent.commenter,
            type=NotificationType.COMMENT_REPLY,
            content={
                "user": UserPublicSerializer(instance.commenter).data,
                "comment": CommentSerializer(instance).data,
                "replied_to": CommentSerializer(instance.parent).data,
            },
        )


@receiver(
    post_save,
    sender=CommentLike,
    dispatch_uid="add_notification_comment_like",
)
def user_liked_comment(sender, instance: CommentLike, created, raw, **kwargs):
    if not created or raw:
        # Ignore if it's not a new CommentLike or if it's a raw signal
        return
    if instance.comment.commenter != instance.liker:
        Notification.objects.create(
            user=instance.comment.commenter,
            type=NotificationType.COMMENT_LIKE,
            content={
                "user": UserPublicSerializer(instance.liker).data,
                "comment": CommentSerializer(instance.comment).data,
            },
        )


@receiver(
    post_save,
    sender=Clap,
    dispatch_uid="add_notification_story_leaf_clap_milestone",
)
def clap_milestone(sender, instance: Clap, created, raw, **kwargs):
    if not created or raw:
        # Ignore if it's not a new Clap or if it's a raw signal
        return
    if instance.part and instance.clapper != instance.part.story.author:
        claps = instance.part.story.claps
        if claps in [99, 499, 999, 4999, 9999, 49999, 99999, 499999, 999999]:
            Notification.objects.create(
                user=instance.part.story.author,
                type=NotificationType.CLAP_MILESTONE,
                content={
                    "story": StorySerializer(instance.part.story).data,
                    "claps": int(claps) + 1,
                },
            )
    if instance.leaf and instance.clapper != instance.leaf.author:
        claps = instance.leaf.claps
        if claps in [99, 499, 999, 4999, 9999, 49999, 99999, 499999, 999999]:
            Notification.objects.create(
                user=instance.leaf.author,
                type=NotificationType.CLAP_MILESTONE,
                content={
                    "leaf": LeafSerializer(instance.leaf).data,
                    "claps": int(claps) + 1,
                },
            )


@receiver(
    post_save,
    sender=StoryRead,
    dispatch_uid="add_notification_read_milestone",
)
def story_read_milestone(sender, instance: StoryRead, created, raw, **kwargs):
    if not created or raw:
        # Ignore if it's not a new StoryRead or if it's a raw signal
        return
    if instance.part and instance.reader != instance.part.story.author:
        reads = instance.part.story.reads
        if reads in [99, 499, 999, 4999, 9999, 49999, 99999, 499999, 999999]:
            Notification.objects.create(
                user=instance.part.story.author,
                type=NotificationType.STORY_VIEWS_MILESTONE,
                content={
                    "story": StorySerializer(instance.part.story).data,
                    "reads": int(reads) + 1,
                },
            )


@receiver(post_save, sender=LeafRead)
def leaf_read_milestone(sender, instance: LeafRead, created, raw, **kwargs):
    if not created or raw:
        # Ignore if it's not a new LeafRead or if it's a raw signal
        return
    if instance.leaf and instance.reader != instance.leaf.author:
        reads = instance.leaf.reads
        if reads in [99, 499, 999, 4999, 9999, 49999, 99999, 499999, 999999]:
            Notification.objects.create(
                user=instance.leaf.author,
                type=NotificationType.LEAF_VIEWS_MILESTONE,
                content={
                    "leaf": LeafSerializer(instance.leaf).data,
                    "reads": int(reads) + 1,
                },
            )


@receiver(
    post_save,
    sender=Part,
    dispatch_uid="add_notification_new_part",
)
def new_part_added(sender, instance: Part, created, raw, **kwargs):
    if not created or raw:
        # Ignore if it's not a new Part or if it's a raw signal
        return
    if instance.visibility != VisibilityType.PUBLIC:
        return
    clappers = (
        Clap.objects.filter(part__story=instance.story)
        .values_list("clapper", flat=True)
        .distinct()
    )
    followers = (
        Follow.objects.filter(followed=instance.story.author)
        .values_list("follower", flat=True)
        .distinct()
    )

    # combine followers and clappers
    target_users = list(followers)
    target_users.extend(list(clappers))
    users = User.objects.filter(pk__in=target_users).exclude(
        pk=instance.story.author.pk
    )

    for user in users:
        Notification.objects.create(
            user=user,
            type=NotificationType.PART_PUBLISH,
            content={
                "user": UserPublicSerializer(instance.story.author).data,
                "part": StoryPartSerializer(instance).data,
            },
        )


@receiver(
    pre_save,
    sender=Report,
    dispatch_uid="add_notification_report_judgement",
)
def judgement(sender, instance: Report, **kwargs):
    try:
        current: Report = Report.objects.get(pk=instance.pk)
    except Report.DoesNotExist:
        # The report hasn't been created
        return

    if current.judgement == instance.judgement or current.user is None:
        # The report the judgement hasn't changed or was created by anonymous user
        return

    Notification.objects.create(
        user=instance.user,
        type=NotificationType.REPORT_JUDGEMENT,
        content={
            "report": ReportSerializer(instance).data,
        },
    )
