from django.db.models import F
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from dhanriti.models import Clap, Comment, CommentLike, Leaf, LeafRead, Story, StoryRead


@receiver(
    post_save,
    sender=Clap,
    dispatch_uid="clap_added",
)
def clap_added(sender, instance: Clap, created, raw, **kwargs):
    if not created or raw:
        return
    if instance.leaf_id:
        Leaf.objects.filter(pk=instance.leaf_id).update(
            claps=F("claps") + 1,
        )
    elif instance.part_id:
        Story.objects.filter(pk=instance.part.story_id).update(
            claps=F("claps") + 1,
        )


@receiver(
    post_delete,
    sender=Clap,
    dispatch_uid="clap_deleted",
)
def clap_deleted(sender, instance: Clap, **kwargs):
    if instance.leaf_id:
        Leaf.objects.filter(pk=instance.leaf_id).update(
            claps=F("claps") - 1,
        )
    elif instance.part_id:
        Story.objects.filter(pk=instance.part.story_id).update(
            claps=F("claps") - 1,
        )


@receiver(
    post_save,
    sender=Comment,
    dispatch_uid="comment_added",
)
def comment_added(sender, instance: Comment, created, raw, **kwargs):
    if not created or raw:
        return
    if instance.leaf_id:
        Leaf.objects.filter(pk=instance.leaf_id).update(
            comments=F("comments") + 1,
        )
    elif instance.part_id:
        Story.objects.filter(pk=instance.part.story_id).update(
            comments=F("comments") + 1,
        )


@receiver(
    post_delete,
    sender=Comment,
    dispatch_uid="comment_deleted",
)
def comment_deleted(sender, instance: Comment, **kwargs):
    print("?????????????????????????")
    if instance.leaf_id:
        print("////////////////", instance.leaf_id)
        Leaf.objects.filter(pk=instance.leaf_id).update(
            comments=F("comments") - 1,
        )
    elif instance.part_id:
        Story.objects.filter(pk=instance.part.story_id).update(
            comments=F("comments") - 1,
        )


@receiver(
    post_save,
    sender=StoryRead,
    dispatch_uid="story_read",
)
def story_read(sender, instance: StoryRead, created, raw, **kwargs):
    if not created or raw:
        return
    Story.objects.filter(pk=instance.part.story_id).update(
        reads=F("reads") + 1,
    )


@receiver(
    post_save,
    sender=LeafRead,
    dispatch_uid="leaf_read",
)
def leaf_read(sender, instance: LeafRead, created, raw, **kwargs):
    if not created or raw:
        return
    Leaf.objects.filter(pk=instance.leaf_id).update(
        reads=F("reads") + 1,
    )


@receiver(
    post_save,
    sender=CommentLike,
    dispatch_uid="comment_like",
)
def comment_like(sender, instance: CommentLike, created, raw, **kwargs):
    if not created or raw:
        return
    Comment.objects.filter(pk=instance.comment_id).update(
        likes=F("likes") + 1,
    )


@receiver(
    post_delete,
    sender=CommentLike,
    dispatch_uid="comment_like_deleted",
)
def comment_like_deleted(sender, instance: CommentLike, **kwargs):
    Comment.objects.filter(pk=instance.comment_id).update(
        likes=F("likes") - 1,
    )
