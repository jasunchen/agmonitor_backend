from ucsb.models import user_asset, user
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ucsb.repository.asset_data_repository import delete_asset_data_helper
from django.forms.models import model_to_dict
from ucsb.repository.helpers import *

@api_view(['POST'])
def add_asset(request):

    params = ["email", "name", "description", "type_of_asset"]
    
    #Check for Required Fields
    for p in params:
        if request.data.get(p, None) == None:
            return Response(
                {"message": "Missing Required Parameters: {}".format(p)}, 
                status = 400)

    email = request.data.get('email')
    tmp_user = user(user_email=email)
    name = request.data.get('name')
    desc = request.data.get('description')

    if request.data.get("type_of_asset", None) == "generation":
        params = ["declination", "azimuth", "modules_power"]
        #Check for Required Fields
        for p in params:
            if request.data.get(p, None) == None:
                return Response(
                    {"message": "Missing Required Parameters: {}".format(p)}, 
                    status = 400)
        
        declination = request.data.get('declination')
        azimuth = request.data.get('azimuth')
        modules_power = request.data.get('modules_power')
        asset = user_asset(user=tmp_user, asset_name=name, description=desc, declination=declination, azimuth=azimuth, modules_power=modules_power, type_of_asset="generation")
        asset.save()
    elif request.data.get("type_of_asset", None) == "flexible":
        params = ["start_charge_time", "end_charge_time"]
        #Check for Required Fields
        for p in params:
            if request.data.get(p, None) == None:
                return Response(
                    {"message": "Missing Required Parameters: {}".format(p)}, 
                    status = 400)
        
        start_time = request.data.get('start_charge_time')
        end_time = request.data.get('end_charge_time')
        asset = user_asset(user=tmp_user, asset_name=name, description=desc, start_charge_time=start_time, end_charge_time=end_time, type_of_asset="flexible")
        asset.save()
    else:
        asset = user_asset(user=tmp_user, asset_name=name, description=desc)
        asset.save()


    return Response({"detail":"Asset created successfully"})

@api_view(['POST'])
def update_asset(request):

    params = ["id", "name", "description", "type_of_asset"]
    
    #Check for Required Fields
    for p in params:
        if request.data.get(p, None) == None:
            return Response(
                {"message": "Missing Required Parameters: {}".format(p)}, 
                status = 400)
    
    id = request.data.get('id')
    name = request.data.get('name')
    desc = request.data.get('description')
    try:
        asset = user_asset.objects.get(id=id)
    except:
        return Response({"detail":"Asset does not exist"}, status=400)

    asset.asset_name = name
    asset.description = desc
    if asset.type_of_asset == "generation":
        params = ["declination", "azimuth", "modules_power"]
        #Check for Required Fields
        for p in params:
            if request.data.get(p, None) == None:
                return Response(
                    {"message": "Missing Required Parameters: {}".format(p)}, 
                    status = 400)
        
        declination = request.data.get('declination')
        azimuth = request.data.get('azimuth')
        modules_power = request.data.get('modules_power')
        asset.declination = declination
        asset.azimuth = azimuth
        asset.modules_power = modules_power
    elif asset.type_of_asset == "flexible":
        params = ["start_charge_time", "end_charge_time"]
        #Check for Required Fields
        for p in params:
            if request.data.get(p, None) == None:
                return Response(
                    {"message": "Missing Required Parameters: {}".format(p)}, 
                    status = 400)
        
        start_time = request.data.get('start_charge_time')
        end_time = request.data.get('end_charge_time')
        asset.start_charge_time = start_time
        asset.end_charge_time = end_time
    asset.save()
    
    return Response({"detail":"Asset updated successfully"})

@api_view(['DELETE'])
def delete_asset(request):

    params = ["id"]
    
    #Check for Required Fields
    for p in params:
        if request.data.get(p, None) == None:
            return Response(
                {"message": "Missing Required Parameters: {}".format(p)}, 
                status = 400)

    #Check for Invalid Parameters
    if verify(request.data, params): 
        return Response(
            {"message": "Request has invalid parameter not in {}".format(params)}, 
            status = 400)

    id = request.data.get('id')
    try:
        asset = user_asset.objects.get(id=id)
    except:
        return Response({"detail":"Asset does not exist"}, status=400)
    delete_asset_data_helper(id)
    user_asset.objects.filter(id=id).delete()
    return Response({"detail": "Asset deleted successfully"})

@api_view(['GET'])
def get_all_assets(request):

    params = ["email"]
    
    #Check for Required Fields
    for p in params:
        if request.query_params.get(p, None) == None:
            return Response(
                {"message": "Missing Required Parameters: {}".format(p)}, 
                status = 400)

    #Check for Invalid Parameters
    if verify(request.query_params, params): 
        return Response(
            {"message": "Request has invalid parameter not in {}".format(params)}, 
            status = 400)

    email = request.query_params.get('email')
    tmp_user = user.objects.get(user_email=email)
    bases = user_asset.objects.filter(user=tmp_user, type_of_asset='base').values('id', 'asset_name', 'description')
    generations = user_asset.objects.filter(user=tmp_user, type_of_asset='generation').values('id', 'asset_name', 'description', 'declination', 'azimuth', 'modules_power')
    felxible_assets = user_asset.objects.filter(user=tmp_user, type_of_asset='flexible').values('id', 'asset_name', 'description', 'start_charge_time', 'end_charge_time', 'duration', 'demand')
    result = {"base": bases, "generation": generations, "flexible": felxible_assets}
    return Response(result)

@api_view(['GET'])
def get_single_asset(request):
    id = request.query_params.get('id')
    
    try:
        asset = user_asset.objects.get(id=id)
    except:
        return Response({"detail":"Asset does not exist"}, status=400)
    
    return Response(model_to_dict(asset))