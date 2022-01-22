from ucsb.models import user
from rest_framework.response import Response
from django.forms.models import model_to_dict
from rest_framework.decorators import api_view
from ucsb.repository.helpers import *
import smtplib, ssl


@api_view(['POST', 'DELETE'])
def edit_user(request):
    if request.method == 'POST':

        params = ["email", "low_limit", "max_limit", "battery_size", "cost_or_shutoff", "hours_of_power", "longitude", "latitude"]

        #Check for Required Fields
        for p in params:
            if request.data.get(p, None) == None:
                return Response(
                    {"message": "Missing Required Parameters: {}".format(p)},
                    status = 400)

        #Check for Invalid Parameters
        if verify(request.data, params):
            return Response(
                {"message": "Request has invalid parameter not in {}".format(params)},
                status = 400)

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

@api_view(['GET'])
def get_user(request):
    params = ["email"]
    #Check for Required Fields
    for p in params:
        if request.query_params.get(p, None) == None:
            return Response(
                {"message": "Missing Required Parameters: {}".format(p)},
                status = 400)

    #Check for Invalid Parameters
    if verify(request.query_params, params):
        return Response(
            {"message": "Request has invalid parameter not in {}".format(params)},
            status = 400)

    email = request.query_params.get('email')
    tmp_user = user.objects.get(user_email=email)
    return Response(model_to_dict(tmp_user))

@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        email = request.data.get('email')
        if email == '':
            return Response({"detail": "Email cannot be empty"}, status=400)
        try:
            a_user = user.objects.get(user_email=email)
            return Response({"detail": "Has already registered"})
        except (user.DoesNotExist, user.MultipleObjectsReturned):
           tmp_user = user(user_email=email)
           tmp_user.save()
           return Response({"detail": "User created successfully"}, status=200)
    else:
        return Response({"detail": "Error: Invalid request"}, status=400)

@api_view(['POST'])
def post_email(request):
    if request.method == 'POST':
        receiver_email = request.data.get('email')
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "yuyuanwang1999@gmail.com"
        password = "ytpuqhpomlekpeqh"
        message = """\
        Subject: Hi there

        This message is sent from Python."""

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
            return Response({"detail": "User send email successfully"}, status=200)
