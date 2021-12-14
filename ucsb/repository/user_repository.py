from ucsb.models import user

def save_user(email):
    res = ""
    try:
        use = user(email=email)
        use.save()
        res = "User saved"
    except Exception as e:
        res = "Error: " + str(e)
    return res