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
        start_time = datetime.strptime(start_time_str, '%m/%d/%Y %H:%M').strftime('%s')
        if start_time not in asset_data_start_time:
            tmp_data = asset_data(asset_id=tmp_asset, start_time=start_time, interval=d['interval'], consumed_energy=d['consumed_energy'], produced_energy=d['produced_energy'])
            tmp_data.save()
    return Response({"detail": "Data created successfully"}, status = 200)

def delete_asset_data_helper(id):
    try:
        tmp_asset = user_asset.objects.get(id=id)
    except:
        return Response({"detail": "Asset does not exist"}, status = 400)
    asset_data.objects.filter(asset_id=tmp_asset).delete()
    return Response({"detail": "Data deleted successfully"}, status = 200)