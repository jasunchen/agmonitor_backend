<<<<<<< HEAD
from ucsb.models import user_asset, asset_data
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime

@api_view(['POST'])
def add_asset_data(request):
    id = request.data.get('id')
    data = request.data.get('data')
    res = add_asset_data_helper(data, id)
    return res

@api_view(['GET'])
def get_asset_data(request):
    id = request.query_params.get('id')
    try:
        tmp_asset = user_asset.objects.get(id=id)
    except:
        return Response({"detail": "Asset does not exist"}, status = 400)
    result = asset_data.objects.filter(asset_id=tmp_asset).values('interval', 'consumed_energy', 'produced_energy', 'start_time', 'asset_id')
    return Response(result)

@api_view(['DELETE'])
def delete_asset_data(request):
    id = request.data.get('id')
    res = delete_asset_data_helper(id)
    return res

def add_asset_data_helper(data, id):
    try:
        tmp_asset = user_asset.objects.get(id=id)
    except:
        return Response({"detail": "Asset does not exist"}, status = 400)
    asset_data_start_time = asset_data.objects.filter(asset_id=tmp_asset).values_list('start_time', flat=True)
    for d in data:
        start_time_str = d['start_time']
        try:
            start_time = datetime.strptime(start_time_str, '%m/%d/%Y %H:%M').strftime('%s')
        except:
            err_message = "Invalid start time format\nYour start time: {}\nCorrect format: mm/dd/yyyy hh:mm".format(start_time_str)
            return Response({"detail": err_message }, status = 400)
        if start_time not in asset_data_start_time:
            interval = d['interval']
            consumed_energy = d['consumed_energy']
            produced_energy = d['produced_energy']
            if not (isinstance(interval,int) and isinstance(consumed_energy,float) and isinstance(produced_energy,float)):
                err_message = "Invalid data format\nYour data: " + str(d) + "\nCorrect format: {'interval': int, 'consumed_energy': float, 'produced_energy': float}"
                return Response({"detail": err_message}, status = 400)
            tmp_data = asset_data(asset_id=tmp_asset, start_time=start_time, interval=interval, consumed_energy=consumed_energy, produced_energy=produced_energy)
            tmp_data.save()
    return Response({"detail": "Data created successfully"}, status = 200)

def delete_asset_data_helper(id):
    try:
        tmp_asset = user_asset.objects.get(id=id)
    except:
        return Response({"detail": "Asset does not exist"}, status = 400)
    asset_data.objects.filter(asset_id=tmp_asset).delete()
    return Response({"detail": "Data deleted successfully"}, status = 200)
=======
from ucsb.models import asset_data
from rest_framework.response import Response
from rest_framework.decorators import api_view

# def create_asset_data(start_time, interval, asset_id, consumed_energy, produced_energy):
#     res = ""
#     try:
#         asset_data_obj = asset_data(start_time=start_time, interval=interval, asset_id=asset_id, consumed_energy=consumed_energy, produced_energy=produced_energy)
#         asset_data_obj.save()
#         res = "Asset data created successfully"
#     except Exception as e:
#         res = "Error: " + str(e)
#     return res



@api_view(["POST"])
def create_asset_data(request):
    # request
    start_time = request.POST.get("start_time")
    interval = request.POST.get("interval")
    asset_id = request.POST.get("asset_id")
    consumed_energy = request.POST.get("consumed_energy")
    produced_energy = request.POST.get("produced_energy")
    # if empty
    if (start_time == None or interval == None or asset_id == None or consumed_energy == None or produced_energy == None):
        res = {"status_cooe":10001,"message":"Please check whether the required parameters are empty"}
        return Response(res)
    else:
        # database
        try:
            asset_data.objects.get_or_create(
                start_time=start_time, interval=int(interval), asset_id_id=int(asset_id),
                consumed_energy=consumed_energy, produced_energy=produced_energy)
            res = {"status_cooe": 200, "message": "Asset data created successfully"}
        except Exception as e:
            res = {"status_cooe": 20001, "message":"Error: " + str(e)}
        return Response(res)
>>>>>>> 5e312d7d0f1d3c180cd4da2409e4c4ed25dca767
