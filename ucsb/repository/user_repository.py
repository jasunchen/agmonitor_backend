from ucsb.models import user
from rest_framework.response import Response
from django.forms.models import model_to_dict
from rest_framework.decorators import api_view

@api_view(['POST', 'DELETE'])
def edit_user(request):
    if request.method == 'POST':
        email = request.data.get('email')
        if email == '':
            return Response({"detail": "Email cannot be empty"}, status=400)
        tmp_user = user(user_email=email)
        tmp_user.save()
        return Response({"detail": "User created successfully"}, status=200)
    elif request.method == 'DELETE':
        email = request.data.get('email')
        if email == '':
            return Response({"detail": "Email cannot be empty"}, status=400)
        tmp_user = user.objects.get(user_email=email)
        tmp_user.delete()
        return Response({"detail": "User deleted successfully"})
    else:
        return Response({"detail": "Error: Invalid request"}, status=400)
    


#test function
@api_view(['GET'])
def getAllUsers(request):
    res = []
    result = user.objects.all()
    for r in result:
        res.append(model_to_dict(r))
    return Response(res)