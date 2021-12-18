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
