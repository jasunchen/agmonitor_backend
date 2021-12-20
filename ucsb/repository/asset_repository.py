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
    return Response("Asset created successfully")

@api_view(['POST'])
def update_asset(request):
    id = request.data.get('id')
    user_asset.objects.filter(id=id).update(asset_name=request.data.get('name'), description=request.data.get('description'))
    return Response("Asset updated successfully")

@api_view(['DELETE'])
def delete_asset(request):
    id = request.data.get('id')
    delete_asset_data_helper(id)
    user_asset.objects.filter(id=id).delete()
    return Response({"detail": "Asset deleted successfully"})

@api_view(['GET'])
def get_all_assets(request):
    email = request.query_params.get('email')
    tmp_user = user.objects.get(user_email=email)
    result = user_asset.objects.filter(user=tmp_user).values('id', 'asset_name', 'description')
    return Response(result)