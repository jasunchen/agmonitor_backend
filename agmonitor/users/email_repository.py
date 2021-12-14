from models import User

def save_user(email):
    res = ""
    try:
        user = User(email=email)
        user.save()
        res = "User saved"
    except:
        res = "User not saved"
    return res

save_user("kaiwen_li@ucsb.edu")