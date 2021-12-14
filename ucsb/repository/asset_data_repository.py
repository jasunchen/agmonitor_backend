from ucsb.models import asset_data

def create_asset_data(start_time, interval, asset_id, consumed_energy, produced_energy):
    res = ""
    try:
        asset_data_obj = asset_data(start_time=start_time, interval=interval, asset_id=asset_id, consumed_energy=consumed_energy, produced_energy=produced_energy)
        asset_data_obj.save()
        res = "Asset data created successfully"
    except Exception as e:
        res = "Error creating asset data"
    return res