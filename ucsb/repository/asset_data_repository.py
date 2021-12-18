from ucsb.models import user_asset, asset_data
from rest_framework.response import Response
from django.forms.models import model_to_dict
from rest_framework.decorators import api_view
import datetime

@api_view(['POST'])
def create_asset_data(request):
    id = request.data.get('id')
    tmp_asset = user_asset.objects.get(id=id)
    data = request.data.get('data')
    res = []
    res.append(model_to_dict(tmp_asset))
    for d in data:
        date = datetime(2015, 10, 9, 23, 55, 59, 342380)
        tmp_data = asset_data(asset_id=tmp_asset, start_time=date, interval=d['interval'], consumed_energy=d['consumed_energy'], produced_energy=d['produced_energy'])
        # tmp_data.save()
        result = model_to_dict(tmp_data)
        res.append(result)

    return Response(res)



def delete_asset_data(id):
    tmp_asset = user_asset.objects.get(id=id)
    data_set = asset_data.objects.filter(asset_id=tmp_asset)
    for d in data_set:
        d.delete()
    return True