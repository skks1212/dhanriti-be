from dhanriti.models.enums import FlowRateType, FlowType
from dhanriti.models.tanks import Canvas, Flow, Funnel


def trigger_canvas_inflow(canvas : Canvas, manual_trigger=False):
    Flow.objects.create(canvas=canvas, flowed=canvas.inflow, manual=manual_trigger)

def trigger_funnel_flow(funnel: Funnel, timely_trigger=False, bypass_last_flow=False, manual_trigger=False):
    last_flow = None
    flow = 0
    if not funnel.in_tank:
        in_tank_filled = funnel.canvas.filled
        last_flow = Flow.objects.filter(canvas=funnel.canvas, funnel=None)
    else:
        last_flow = Flow.objects.filter(funnel=Funnel.objects.get(out_tank=funnel.in_tank))
        in_tank_filled = funnel.in_tank.filled

    last_flow = last_flow.order_by("-created_at").first()

    if funnel.flow_rate_type == FlowRateType.CONSEQUENT:
        if last_flow and not bypass_last_flow:
            deductable = last_flow.flowed if not (last_flow.meta and last_flow.meta.get("reduced", False)) else last_flow.meta.get("original_flow", 0)
        else:
            deductable = in_tank_filled

        if funnel.flow_type == FlowType.PERCENTAGE:
            flow = (deductable * funnel.flow) / 100
        else:
            if funnel.flow < deductable:
                flow = funnel.flow
            else:
                flow = deductable
    elif timely_trigger:
        if funnel.flow_type == FlowType.PERCENTAGE:
            flow = (in_tank_filled * funnel.flow) / 100
        else:
            flow = funnel.flow if funnel.flow < in_tank_filled else in_tank_filled
    else:
        return

    reduce_reason = None
    tank_space = funnel.out_tank.capacity - funnel.out_tank.filled
    if flow > tank_space:
        print(f"Flow reduced to {tank_space} from {flow} because out tank does not have space")
        flow = tank_space
        reduce_reason = "out_tank_space"
    elif flow > funnel.in_tank.filled:
        print(f"Flow reduced to {funnel.in_tank.filled} from {flow} because in tank does not have enough money")
        reduce_reason = "in_tank_space"
        flow = funnel.in_tank.filled

    print(f"flowing {flow} from {funnel.in_tank.name if funnel.in_tank else 'Main Tank'} to {funnel.out_tank.name}")

    Flow.objects.create(funnel=funnel, flowed=flow, canvas=funnel.canvas, manual=manual_trigger, meta={
        "reduced": flow != funnel.flow,
        "reduced_reason": reduce_reason,
        "original_flow": funnel.flow
    })