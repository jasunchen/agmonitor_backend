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
