# from requests import Response
import ast
from datetime import datetime

from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializer import *


# Create your views here.

class CouriersView(viewsets.ModelViewSet):
    queryset = Couriers.objects.all()
    serializer_class = CouriersSerializer


@api_view(['POST'])
def couriers_list(request):
    flag_valid = True
    res = {}
    error = {}
    res["couriers"] = []
    error["couriers"] = []
    if request.method == 'POST':
        data = request.data['data']

        for elem in data:
            serializer = CouriersSerializer(data=elem)

            if serializer.is_valid():

                res["couriers"].append({"courier_id": elem["courier_id"]})

            else:
                flag_valid = False
                error["couriers"].append({"courier_id": elem["courier_id"]})

                continue
        if flag_valid:
            for elem in data:
                serializer = CouriersSerializer(data=elem)
                if serializer.is_valid():
                    serializer.save()

            return Response({"couriers": [{"id": val["courier_id"]} for val in res["couriers"]]},
                            status=status.HTTP_201_CREATED)
        return Response({"validation_error": {"couriers": [{"id": val["courier_id"]} for val in error["couriers"]]}},
                        status=status.HTTP_400_BAD_REQUEST)


class OrdersView(viewsets.ModelViewSet):
    queryset = Orders.objects.all()
    serializer_class = OrderSerializer


@api_view(['POST'])
def order_list(request):
    flag_valid = True
    res = {}
    error = {}
    res["orders"] = []
    error["orders"] = []
    if request.method == 'POST':
        data = request.data['data']
        for elem in data:
            serializer = OrderSerializer(data=elem)

            if serializer.is_valid():

                res["orders"].append({"order_id": elem["order_id"]})

            else:
                flag_valid = False
                error["orders"].append({"order_id": elem["order_id"]})

                continue
        if flag_valid:
            for elem in data:
                serializer = OrderSerializer(data=elem)
                if serializer.is_valid():
                    serializer.save()
            return Response({"orders": [{"id": val["order_id"]} for val in res["orders"]]},
                            status=status.HTTP_201_CREATED)
        return Response({"validation_error": {"orders": [{"id": val["order_id"]} for val in error["orders"]]}},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def complete(request):
    """complete realization"""
    courier_id_data = request.data['courier_id']
    order_id_data = request.data['order_id']
    complete_time_data = request.data['complete_time']

    try:
        info_order = Orders.objects.get(pk=order_id_data)
    except Exception:
        return Response({"error": "there is(in db) no such courier"}, status=status.HTTP_400_BAD_REQUEST)

    if info_order.complete is not True and info_order.courier is not None and info_order.courier.courier_id == courier_id_data:
        Orders.objects.filter(pk=order_id_data).update(complete=True, complete_time=complete_time_data)

        return Response({"order_id": order_id_data}, status=status.HTTP_200_OK)
    else:

        return Response({"error": "there is no appropriate order"}, status=status.HTTP_400_BAD_REQUEST)


def schedule(courier_node, order, order_time_format, courier_time_format, assign_time_data) -> int:
    """check coincidence in delivery hours and working hours"""
    courier_id_data = courier_node.courier_id
    for order_node_f in order_time_format:
        for courier_node_f in courier_time_format:
            if (order_node_f[0] <= courier_node_f[0] and order_node_f[1] >= courier_node_f[0]) or (
                    courier_node_f[0] <= order_node_f[0] <= courier_node_f[1] and courier_node_f[0] <= order_node_f[
                1] <=
                    courier_node_f[1]) or (
                    order_node_f[1] >= courier_node_f[1] and order_node_f[0] <= courier_node_f[1]):
                Orders.objects.filter(pk=order.order_id).update(courier=courier_node,
                                                                assign_time=assign_time_data)
                Couriers.objects.filter(pk=courier_id_data).update(
                    assign_time_current_for_delivery=assign_time_data)
                return order.order_id


def assign_service(courier_node, acceptable_orders, assign_time_data)->list:
    """link orders and couriers"""
    res = []
    courier_time = ast.literal_eval(courier_node.working_hours)
    courier_time = [elem.split("-") for elem in courier_time]
    courier_time_format = [
        ((datetime.strptime(elem[0], '%H:%M')), (datetime.strptime(elem[1], '%H:%M'))) for
        elem in courier_time]
    for order in acceptable_orders:

        if order.region in ast.literal_eval(courier_node.regions) and (
                order.complete is not True) and order.courier is None:
            order_time = ast.literal_eval(order.delivery_hours)
            order_time = [elem.split("-") for elem in order_time]
            order_time_format = [
                ((datetime.strptime(elem[0], '%H:%M')), (datetime.strptime(elem[1], '%H:%M'))) for
                elem in order_time]

            res.append(schedule(courier_node, order, order_time_format, courier_time_format, assign_time_data))
    return res


@api_view(['POST'])
def assign(request):
    """assign realization"""
    courier_id_data = request.data['courier_id']
    assign_time_data = datetime.now()
    try:
        courier_node = Couriers.objects.get(pk=courier_id_data)
    except Exception:
        return Response({"error": "there is(in db) no such courier"}, status=status.HTTP_400_BAD_REQUEST)

    if courier_node.courier_type == "foot":
        acceptable_weight = 10
    elif courier_node.courier_type == "bike":
        acceptable_weight = 15
    else:
        acceptable_weight = 50
    res = []

    try:
        acceptable_orders = Orders.objects.filter(weight__lte=acceptable_weight,complete=False)
    except Exception:

        return Response({"orders": []}, status=status.HTTP_200_OK)

    res = assign_service(courier_node, acceptable_orders, assign_time_data)
    for order in acceptable_orders:

        if order.region in ast.literal_eval(courier_node.regions) and (
                order.complete is not True) and order.courier == courier_node:
            res.append(order.order_id)
            assign_time_data = order.assign_time
    if len(res) == 0:
        return Response({"orders": []}, status=status.HTTP_200_OK)
    else:
        return Response({"orders": [{"id": elem} for elem in res], "assign_time": assign_time_data},
                        status=status.HTTP_200_OK)


@api_view(['PATCH', 'GET'])
def change(request, pk):
    """2 and 6 points realizations"""
    try:
        node = Couriers.objects.get(pk=pk)
    except Exception:
        return Response({"error": "there is(in db) no such courier"}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'PATCH':

        allowed_val = ["courier_type", "regions", "working_hours"]

        try:
            old_orders = Orders.objects.filter(courier=node)
        except Exception:
            old_orders = []

        for order in old_orders:
            if order.complete is True:
                del order
        if len(old_orders) != 0:
            assign_time_data = old_orders[0].assign_time

            for order in old_orders:
                order.courier = None
                order.assign_time = None

        for field in request.data.keys():
            val = request.data[field]
            if field in allowed_val:
                if field == 'regions':
                    node.regions = val
                elif field == 'courier_type':
                    node.courier_type = val
                else:
                    node.working_hours = val

            else:

                return Response({"error": "invalid field"}, status=status.HTTP_400_BAD_REQUEST)

            raw_courier = {"courier_id": node.courier_id, "courier_type": node.courier_type,
                           "regions": ast.literal_eval(str(node.regions)),
                           "working_hours": ast.literal_eval(str(node.working_hours))}

            serializer = CouriersSerializer(data=request.data, partial=True)
            if serializer.is_valid():

                # достала ордеры отвязала
                Orders.objects.filter(courier=node, complete=False).update(courier=None, assign_time=None)
                # update
                for field in request.data.keys():

                    val = request.data[field]
                    if field in allowed_val:
                        if field == 'regions':
                            node.regions = val

                            Couriers.objects.filter(pk=pk).update(regions=val)

                        elif field == 'courier_type':
                            node.courier_type = val
                            Couriers.objects.filter(pk=pk).update(courier_type=val)
                        else:
                            node.working_hours = val
                            Couriers.objects.filter(pk=pk).update(working_hours=val)

                    else:

                        return Response({"error": "invalid field"}, status=status.HTTP_400_BAD_REQUEST)

                courier_new_node = Couriers.objects.get(pk=pk)
                if len(old_orders) != 0:
                    assign_service(courier_new_node, old_orders, assign_time_data)
                return Response({"courier_id": pk, "courier_type": courier_new_node.courier_type,
                                 "regions": ast.literal_eval(courier_new_node.regions),
                                 "working_hours": ast.literal_eval(courier_new_node.working_hours)},
                                status=status.HTTP_200_OK)
            else:

                return Response({"error": "invalid data for courier"}, status=status.HTTP_400_BAD_REQUEST)

    #     6
    elif request.method == "GET":

        if node.courier_type == "foot":
            c = 2
        elif node.courier_type == "bike":
            c = 5
        else:
            c = 9

        res_answ = {"courier_id": pk, "courier_type": node.courier_type, "regions": ast.literal_eval(node.regions),
                    "working_hours": ast.literal_eval(node.working_hours)}

        acceptable_orders = Orders.objects.filter(courier=pk).order_by('complete_time')

        flag_complete = 0
        statistic = {}

        for region in ast.literal_eval(node.regions):
            statistic[region] = []
        t = []
        previous = None
        earnings = 0
        coeff = 500 * c

        for order_node in acceptable_orders:
            if order_node.complete is True:
                flag_complete += 1

                # гарантировано ключ такой есть и заказы сортированы по времени выполн

                if flag_complete == 1:
                    val = abs(node.assign_time_current_for_delivery - order_node.complete_time)
                    previous = order_node.complete_time

                    earnings += coeff
                else:
                    val = abs(order_node.complete_time - previous)
                    previous = order_node.complete_time
                    earnings += coeff
                statistic[order_node.region].append(val.seconds)
        res_answ["earnings"] = earnings
        if flag_complete == 0:
            return Response(res_answ, status=status.HTTP_200_OK)

        # среднее по району
        for reg in statistic.keys():
            statistic[reg] = [elem / len(statistic[reg]) for elem in statistic[reg]]

            if len(statistic[reg]) != 0:
                statistic[reg] = sum(statistic[reg])
                t.append(statistic[reg])

        t_val = min(t)
        rating = (60 * 60 - min(t_val, 60 * 60)) / (60 * 60) * 5
        res_answ["rating"] = round(rating, 2)
        return Response(res_answ, status=status.HTTP_200_OK)
    else:
        return Response({}, status=status.HTTP_400_BAD_REQUEST)
