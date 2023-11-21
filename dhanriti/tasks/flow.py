from dhanriti.models.enums import FlowRateType, FlowType
from dhanriti.models.tanks import Canvas, Flow, Funnel


def trigger_canvas_inflow(canvas : Canvas):
    Flow.objects.create(canvas=canvas, flowed=canvas.inflow)

def trigger_funnel_flow(funnel: Funnel, timely_trigger=False, bypass_last_flow=False):
    print ("--- New Flow ---")
    in_tank = funnel.in_tank
    last_flow = None
    if not in_tank:
        in_tank_filled = funnel.canvas.filled
        last_flow = Flow.objects.filter(canvas=funnel.canvas)
    else:
        last_flow = Flow.objects.filter(funnel=Funnel.objects.get(out_tank=funnel.in_tank))
        in_tank_filled = in_tank.filled

    last_flow = last_flow.order_by("-created_at").first()

    if funnel.flow_rate_type == FlowRateType.CONSEQUENT:
        if last_flow and not bypass_last_flow:
            deductable = last_flow.flowed
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

    tank_space = funnel.out_tank.capacity - funnel.out_tank.filled
    if flow > tank_space:
        print(f"Flow reduced to {tank_space} from {flow} because tank does not have space")
        flow = tank_space

    print(f"flowing {flow} from {funnel.in_tank.name if funnel.in_tank else 'Main Tank'} to {funnel.out_tank.name}")

    Flow.objects.create(funnel=funnel, flowed=flow)