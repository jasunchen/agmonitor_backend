from ucsb.models import user_asset

def create_asset(user, name, desc):
    res = ""
    try:
        asset = user_asset.UserAsset(user, name, desc)
        asset.save()
        res = "Asset created successfully"
    except Exception as e:
        res = "Error: " + str(e)
    return res