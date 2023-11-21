from django.db.models.signals import post_save
from django.dispatch import receiver
from dhanriti.models.tanks import Flow, Funnel
from dhanriti.tasks.flow import trigger_funnel_flow

@receiver(
    post_save,
    sender=Flow,
    dispatch_uid="add_notification_follow",
)
def flowed(sender, instance: Flow, created, raw, **kwargs):
    # check if it is a newly created object
    if created:
        if instance.canvas and not instance.funnel:
            instance.canvas.filled += instance.flowed
            instance.canvas.save()
            for funnel in Funnel.objects.filter(canvas=instance.canvas, in_tank=None):
                trigger_funnel_flow(funnel)
        elif instance.funnel and not instance.canvas:
            if instance.funnel.in_tank:
                instance.funnel.in_tank.filled -= instance.flowed
                instance.funnel.in_tank.save()
            else:
                instance.funnel.canvas.filled -= instance.flowed
                instance.funnel.canvas.save()
            instance.funnel.out_tank.filled += instance.flowed
            instance.funnel.out_tank.save()
            for funnel in Funnel.objects.filter(in_tank=instance.funnel.out_tank):
                trigger_funnel_flow(funnel)
