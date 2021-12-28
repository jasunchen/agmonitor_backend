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
    except(user_asset.DoesNotExist):
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
    except (user_asset.DoesNotExist):
        return Response({"detail": "Asset does not exist"}, status = 400)
    asset_data.objects.filter(asset_id=tmp_asset).delete()
    return Response({"detail": "Data deleted successfully"}, status = 200)