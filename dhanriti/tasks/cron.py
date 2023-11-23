from django.utils import timezone
import croniter
from celery import shared_task
from django.db import models
from django.http import HttpResponse, HttpResponseForbidden

from dhanriti.models.tanks import Canvas, Flow, Funnel, FlowRateType, FlowType
from utils.flow import trigger_canvas_inflow, trigger_funnel_flow

@shared_task
def cron_watch(request=None, cron_key=None):
    if cron_key and cron_key != "3z1OxJQuzkvKKw9ZJDWnZE8R8SuysN7ghdFzwk870UzLXB84ww":
        return HttpResponseForbidden("Incorrect password")

    if cron_key is None:
        pass
    
    # Fetch current time once
    now = timezone.now()

    # Fetch all canvases with related flows and funnels to reduce queries in loops
    all_canvases = Canvas.objects.prefetch_related('flows', 'funnels')

    # Process each canvas
    for canvas in all_canvases:
        cron = canvas.inflow_rate
        # Use the related_name of Flow to Canvas if defined, or use flow_set if not defined
        last_flow : Flow = canvas.flows.filter(funnel=None, manual=False).order_by("-created_at").first()
        last_flow_time = last_flow.created_at if last_flow else canvas.created_at

        next_flow_time = croniter.croniter(cron, last_flow_time).get_next(timezone.now().__class__)

        if next_flow_time < now:
            print(f"Triggering canvas {canvas.name} inflow")
            trigger_canvas_inflow(canvas)

    # Fetch all funnels related to the canvases
    all_funnels = Funnel.objects.filter(canvas__in=all_canvases, flow_rate_type=FlowRateType.TIMELY).select_related('canvas')

    # Process each funnel
    for funnel in all_funnels:
        cron = funnel.flow_rate
        last_flow = funnel.flows.filter(funnel__deleted=False, manual=False).order_by("-created_at").first()
        last_flow_time = last_flow.created_at if last_flow else funnel.created_at

        next_flow_time = croniter.croniter(cron, last_flow_time).get_next(timezone.now().__class__)

        if next_flow_time < now:
            print(f"Triggering funnel {funnel.name} flow")

            trigger_funnel_flow(funnel, timely_trigger=True, bypass_last_flow=True)

    if request:
        return HttpResponse("Done")
        
        

