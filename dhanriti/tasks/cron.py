from django.utils import timezone
import croniter
from celery import shared_task
from django.db import models
from django.http import HttpResponse, HttpResponseForbidden

from dhanriti.models.tanks import Canvas, Flow, Funnel, FlowRateType

@shared_task
def cron_watch(request=None, cron_key=None):
    if cron_key and cron_key != "3z1OxJQuzkvKKw9ZJDWnZE8R8SuysN7ghdFzwk870UzLXB84ww":
        return HttpResponseForbidden("Incorrect password")

    if cron_key is None:
        pass
    
    all_canvases = Canvas.objects.all()
    
    for canvas in all_canvases:
        cron = canvas.inflow_rate
        last_flow = Flow.objects.filter(canvas=canvas, funnel=None, manual=False).order_by("-created_at").first()
        if last_flow:
            last_flow = last_flow.created_at
        else:
            last_flow = canvas.created_at

        next_flow = croniter.croniter(cron, last_flow).get_next(timezone.now().__class__)


        print(next_flow)
        if next_flow < timezone.now():
            print(f"Triggering canvas {canvas.name} inflow")
            Flow.objects.create(canvas=canvas, flowed=canvas.inflow)

        funnels = Funnel.objects.filter(canvas=canvas, flow_rate_type=FlowRateType.TIMELY)

        for funnel in funnels:
            cron = funnel.flow_rate
            last_flow = Flow.objects.filter(funnel=funnel, funnel__deleted=False, manual=False).order_by("-created_at").first()
            if last_flow:
                last_flow = last_flow.created_at
            else:
                last_flow = funnel.created_at

            next_flow = croniter.croniter(cron, last_flow).get_next(timezone.now().__class__)

            if next_flow < timezone.now():
                print(f"Triggering funnel {funnel.name} flow")
                Flow.objects.create(funnel=funnel, flowed=funnel.flow, canvas=canvas)

    return HttpResponse("Done")
        
        

