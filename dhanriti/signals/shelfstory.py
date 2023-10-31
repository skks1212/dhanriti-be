from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from dhanriti.models import Shelf, ShelfStory


@receiver(
    post_save,
    sender=ShelfStory,
    dispatch_uid="shelf_story_added",
)
def shelf_story_added(sender, instance: ShelfStory, created, raw, **kwargs):
    if not created or raw:
        # check if it is deleted
        if instance.deleted:
            shelf = instance.shelf
            shelf.story_order.remove(str(instance.story.external_id))
            shelf.save()
        return

    Shelf.objects.filter(pk=instance.shelf_id).update(
        # append to story_order
        story_order=[
            *instance.shelf.story_order,
            instance.story.external_id,
        ],
    )


@receiver(pre_delete, sender=ShelfStory, dispatch_uid="shelf_story_deleted")
def shelf_story_deleted(sender, instance, **kwargs):
    shelf = instance.shelf
    shelf.story_order.remove(str(instance.story.external_id))
    shelf.save()
