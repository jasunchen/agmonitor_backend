from ucsb.models import user_asset, user
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ucsb.repository.asset_data_repository import delete_asset_data_helper

@api_view(['POST'])
def add_asset(request):
    email = request.data.get('email')
    tmp_user = user(user_email=email)
    name = request.data.get('name')
    desc = request.data.get('description')
    asset = user_asset(user=tmp_user, asset_name=name, description=desc)
    asset.save()
    return Response({"detail":"Asset created successfully"})

@api_view(['POST'])
def update_asset(request):
    id = request.data.get('id')
    name = request.data.get('name')
    desc = request.data.get('description')
    try:
        asset = user_asset.objects.get(id=id)
    except:
        return Response({"detail":"Asset does not exist"}, status=400)
    asset.asset_name = name
    asset.description = desc
    asset.save()
    
    return Response({"detail":"Asset updated successfully"})

@api_view(['DELETE'])
def delete_asset(request):
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
    email = request.query_params.get('email')
    tmp_user = user.objects.get(user_email=email)
    result = user_asset.objects.filter(user=tmp_user).values('id', 'asset_name', 'description')
    return Response(result)
from ucsb.models import user_asset
from rest_framework.response import Response
from rest_framework.decorators import api_view

# def create_asset(user, name, desc):
#     res = ""
#     try:
#         asset = user_asset.UserAsset(user, name, desc)
#         asset.save()
#         res = "Asset created successfully"
#     except Exception as e:
#         res = "Error: " + str(e)
#     return res


@api_view(["POST"])
def create_asset(request):
    # request parameter
    description = request.POST.get("description")
    asset_name = request.POST.get("asset_name")
    user_id = request.POST.get("user_id")
    # if empty
    if (description == None or asset_name == None or user_id == None):
        res = {"status_cooe":10001,"message":"Please check whether the required parameters are empty"}
        return Response(res)
    else:
        # database
        try:
            asset = user_asset.objects.get_or_create(description=description,asset_name=asset_name,user_id=user_id)
            res = {"status_cooe":200,"message":"Asset created successfully"}
        except Exception as e:
            res = {"status_cooe":20001,"message":"Error: " + str(e)}
        return Response(res)
