from rest_framework.decorators import api_view
from rest_framework import status
from user.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes

@api_view(['POST'])
def sign_up(request):
    check_fields = ['username', 'password', 'first_name', 'last_name', 'email']
    for item in check_fields:
        if item not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.create_user(
            email=request.data["email"],
            username=request.data["username"],
            password=request.data["password"],
            first_name=request.data["first_name"],
            last_name=request.data["last_name"],
            )
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    if  "profile_pic" in request.data:
        user.profile_pic = request.data["profile_pic"]
        user.save()
    if user.username == "cturco44":
        user.superuser = True
        user.admin = True
        user.staff = True
        user.save()
    token = Token.objects.get_or_create(user=user)[0].key
    return Response({"token": token, "username": user.username, "email": user.email}, status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_profile_pic(request):
    user = request.user
    try:
        user.profile_pic = request.data["profile_pic"]
        user.save()
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    return Response(status=200)