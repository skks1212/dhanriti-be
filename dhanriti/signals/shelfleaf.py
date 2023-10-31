from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from dhanriti.models import Shelf, ShelfLeaf


@receiver(
    post_save,
    sender=ShelfLeaf,
    dispatch_uid="shelf_leaf_added",
)
def shelf_leaf_added(sender, instance: ShelfLeaf, created, raw, **kwargs):
    if not created or raw:
        # check if it is deleted
        if instance.deleted:
            shelf = instance.shelf
            shelf.leaf_order.remove(str(instance.leaf.external_id))
            shelf.save()
        return

    Shelf.objects.filter(pk=instance.shelf_id).update(
        # append to leaf_order
        leaf_order=[
            *instance.shelf.leaf_order,
            instance.leaf.external_id,
        ],
    )


@receiver(pre_delete, sender=ShelfLeaf, dispatch_uid="shelf_leaf_deleted")
def shelf_leaf_deleted(sender, instance, **kwargs):
    shelf = instance.shelf
    shelf.leaf_order.remove(str(instance.leaf.external_id))
    shelf.save()
