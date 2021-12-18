from ucsb.models import user_asset, user
from rest_framework.response import Response
from django.forms.models import model_to_dict
from rest_framework.decorators import api_view

@api_view(['POST', 'DELETE'])
def create_asset(request):
    email = request.data.get('email')
    tmp_user = user(user_email=email)
    name = request.data.get('name')
    desc = request.data.get('desc')
    asset = user_asset(user=tmp_user, asset_name=name, description=desc)
    asset.save()
    return Response("Asset created successfully")

#test function
@api_view(['GET'])
def getAllAssets(request):
    res = []
    result = user_asset.objects.all()
    for r in result:
        res.append(model_to_dict(r))
    return Response(res)