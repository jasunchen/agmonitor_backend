from ucsb.models import user_asset, asset_data
from rest_framework.response import Response
from django.forms.models import model_to_dict
from rest_framework.decorators import api_view
from datetime import datetime

@api_view(['POST'])
def create_asset_data(request):
    id = request.data.get('id')
    tmp_asset = user_asset.objects.get(id=id)
    data = request.data.get('data')
    res = []
    asset_data_start_time = asset_data.objects.filter(asset_id=tmp_asset).values_list('start_time', flat=True)
    for d in data:
        start_time_str = d['start_time']
        start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M').strftime('%s')
        if start_time not in asset_data_start_time:
            tmp_data = asset_data(asset_id=tmp_asset, start_time=start_time, interval=d['interval'], consumed_energy=d['consumed_energy'], produced_energy=d['produced_energy'])
            tmp_data.save()
    return Response({"detail": "Data created successfully"}, status=200)


@api_view(['DELETE'])
def deleteAssetData(request):
    id = request.data.get('id')
    delete_asset_data(id)
    return Response({"detail": "Data deleted successfully"}, status=200)



def delete_asset_data(id):
    tmp_asset = user_asset.objects.get(id=id)
    data_set = asset_data.objects.filter(asset_id=tmp_asset)
    for d in data_set:
        d.delete()
    return True