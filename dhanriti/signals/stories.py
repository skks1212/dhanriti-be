from django.db.models.signals import post_save
from django.dispatch import receiver

from dhanriti.models import Part, Story


@receiver(
    post_save,
    sender=Part,
    dispatch_uid="part_added",
)
def part_added(sender, instance: Part, created, raw, **kwargs):
    if not created or raw:
        # check if it is deleted
        if instance.deleted:
            story = instance.story
            story.parts_order.remove(str(instance.external_id))
            story.save()
        return
    Story.objects.filter(pk=instance.story_id).update(
        # append to parts_order
        parts_order=[
            *instance.story.parts_order,
            instance.external_id,
        ],
    )
