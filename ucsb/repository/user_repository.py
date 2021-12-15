from ucsb.models import user
from rest_framework.response import Response
from django.forms.models import model_to_dict
from rest_framework.decorators import api_view

@api_view(['POST'])
def save_user(request):
    res = ""
    try:
        email = request.data.get('email')
        use = user(user_email=email)
        use.save()
    except Exception as e:
        res = "Error: " + str(e)
    return Response(res)

@api_view(['GET'])
def getAllUsers(request):
    res = []
    try:
        result = user.objects.all()
        for r in result:
            res.append(model_to_dict(r))
    except Exception as e:
        res = "Error: " + str(e)
    return Response(res)