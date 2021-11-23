from django.http import JsonResponse
from django.http.response import Http404
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib import messages
from user.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

@api_view(['POST'])
def sign_up(request):
    check_fields = ['username', 'password', 'first_name', 'last_name', 'profile_pic', 'email']
    for item in check_fields:
        if item not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # try:
    user = User.objects.create_user(
        email=request.data["email"],
        username=request.data["username"],
        password=request.data["password"],
        first_name=request.data["first_name"],
        last_name=request.data["last_name"],
        profile_pic=request.data["profile_pic"],
        )
    # except:
    #     return Response(status=status.HTTP_400_BAD_REQUEST)
    
    token = Token.objects.get_or_create(user=user)[0].key
    return Response({"token": token}, status.HTTP_200_OK)
    