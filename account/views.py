# ./account/views.py

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from account.request_serializers import SignInRequestSerializer, SignUpRequestSerializer, TokenRefreshRequestSerializer
from .serializers import UserSerializer

User = get_user_model()
from rest_framework_simplejwt.tokens import RefreshToken

def generate_token_in_serialized_data(user):
    token = RefreshToken.for_user(user)
    refresh_token, access_token = str(token), str(token.access_token)
    serialized_data = UserSerializer(user).data
    serialized_data["token"] = {"access": access_token, "refresh": refresh_token}
    return serialized_data

def set_token_on_response_cookie(user, status_code):
    token = RefreshToken.for_user(user)
    serialized_data = UserSerializer(user).data
    res = Response(serialized_data, status=status_code)
    res.set_cookie("refresh_token", value=str(token), httponly=True)
    res.set_cookie("access_token", value=str(token.access_token), httponly=True)
    return res
class SignUpView(APIView):
    @extend_schema(
        summary="회원가입",
        description="회원가입을 진행합니다.",
        request=SignUpRequestSerializer,
        responses={201: UserSerializer, 400: "Bad Request"},
    )
    def post(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.save()
            user.set_password(request.data.get("password"))
            user.save()

            return set_token_on_response_cookie(user, status_code=status.HTTP_201_CREATED)
						                    
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SignInView(APIView):
    @extend_schema(
        summary="로그인",
        description="로그인을 진행합니다.",
        request=SignInRequestSerializer,
        responses={200: UserSerializer, 404: "Not Found", 400: "Bad Request"},
    )
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response(
                {"message": "missing fields ['username', 'password'] in body"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                return Response(
                    {"message": "Password is incorrect"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return set_token_on_response_cookie(user, status_code=status.HTTP_200_OK)
						
        except User.DoesNotExist:
            return Response(
                {"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
class TokenRefreshView(APIView):
    @extend_schema(
        summary="토큰 재발급",
        description="access 토큰을 재발급 받습니다.",
        request=TokenRefreshRequestSerializer,
        responses={200: UserSerializer},
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        
        #### 1
        if not refresh_token:
            return Response(
                {"detail": "no refresh token"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
        #### 2
            RefreshToken(refresh_token).verify()
        except:
            return Response(
                {"detail": "please signin again."}, status=status.HTTP_401_UNAUTHORIZED
            )
            
        #### 3
        new_access_token = str(RefreshToken(refresh_token).access_token)
        response = Response({"detail": "token refreshed"}, status=status.HTTP_200_OK)
        response.set_cookie("access_token", value=str(new_access_token), httponly=True)
        return response



from rest_framework_simplejwt.exceptions import TokenError
class LogoutAPIView(APIView):

    @extend_schema(
        summary="로그아웃",
        description="Refresh 토큰을 블랙리스트에 추가하고 쿠키를 삭제하여 로그아웃합니다.",
        request=TokenRefreshRequestSerializer, 
        responses={
            200: {"description": "성공적으로 로그아웃 되었습니다."}, 
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    def post(self, request):
        
        #로그인 되어있을 때만 가능
        author = request.user
        if not author.is_authenticated:
            return Response({"detail": "please signin"}, status=status.HTTP_401_UNAUTHORIZED)
                   
        # refresh request 시리얼라이저를 활용해 refresh token 추출
        serializer = TokenRefreshRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {"detail": "no refresh token"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        refresh_token = serializer.validated_data.get("refresh")
            
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            response = Response(
                {"message": "성공적으로 로그아웃 되었습니다."}, 
                status=status.HTTP_200_OK
            )

            #쿠키 삭제
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

            return response

        except TokenError:
            return Response(
                {"message": "invalid or expired Token"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
