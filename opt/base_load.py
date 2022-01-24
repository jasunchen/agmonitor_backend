from ucsb.models import user, user_asset, asset_data
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def test_optimization(request):
    print(calculate_base_load('alexmei@ucsb.edu', 0, 100000000000000000))
    return Response({"detail": "success"}, status=200)


def calculate_base_load(user_email, start_time, end_time):
    # Construct Output Map
    time_map = { 15 * t : { "sum" : 0, "count" : 0 } for t in range(96)}
    
    try:
        # Get All Base Assets
        tmp_user = user.objects.get(user_email=user_email)
        bases = user_asset.objects.filter(user=tmp_user, type_of_asset='base').values('id')
    
        # Get Data From Base Assets
        for base in bases:
            result = asset_data.objects.filter(asset_id=base['id'], start_time__gte=start_time, start_time__lte=end_time).values('consumed_energy', 'start_time')
            for d in result:
                minutes = d['start_time'] % 86400 // 60
                time_map[minutes]["sum"] += d['consumed_energy']
                time_map[minutes]["count"] += 1

    except: 
        print("ERROR")

    # Compute Running Average
    # 2D list with elements containing [
    # first element: time in minutes (i.e., 1425 = 23:45) use x // 60 for hrs, x % 60 for mins
    # second element: average base load in KWH
    #]
    return [[k, v["sum"] / v["count"] if v["count"] != 0 else 0] for k, v in time_map.items()]
    

    

    