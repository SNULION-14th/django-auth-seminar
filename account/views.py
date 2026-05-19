# ./account/views.py

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from account.request_serializers import SignInRequestSerializer, SignUpRequestSerializer
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken #추가
from rest_framework_simplejwt.exceptions import TokenError
from account.request_serializers import SignInRequestSerializer, SignUpRequestSerializer, SignOutRequestSerializer, TokenRefreshRequestSerializer


User = get_user_model()

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
    # 수정
    def post(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.save()
            user.set_password(request.data.get("password"))
            user.save()

            # 추가: 회원가입 완료 시, Acess Token과 Refresh Token을 발급하고 응답에 포함. -> 회원가입 후에도 토큰 이용해 사용자 인증 유지 가능.
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
            
            ##수정
            return set_token_on_response_cookie(user, status_code=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response(
                {"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

class SignOutView(APIView):
    @extend_schema(
        summary = "로그아웃",
        description = "로그아웃을 진행합니다.",
        request=SignOutRequestSerializer,
        responses={401:"Unauthorized", 400: "Bad Request", 204: None},
    )   

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail":"please signin"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "no refresh token"},
                status = status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            token = RefreshToken(refresh_token)
            token.verify()
            token.blacklist()

        except TokenError:
            return Response(
                {"detail": "no refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        
        
        res = Response(status=status.HTTP_204_NO_CONTENT)
        res.delete_cookie("access")
        res.delete_cookie("refresh")
        return res


class TokenRefreshView(APIView):
    @extend_schema(
        summary="토큰 재발급",
        description="access 토큰을 재발급 받습니다.",
        request=TokenRefreshRequestSerializer,
        responses={200: UserSerializer},
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        
        #### 1. 사용자의 요청 body로부터 refresh 토큰의 값을 가져옴. 그 값이 없을 경우 400 에러 반환.
        if not refresh_token:
            return Response(
                {"detail": "no refresh token"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
        #### 2. 받아온 refresh token이 유효한지 검증. 만약 refresh token이 유효하지 않은 경우, validation error가 발생하여 except 구문 동작, 401 에러 반환. 
            RefreshToken(refresh_token).verify()
        except:
            return Response(
                {"detail": "please signin again."}, status=status.HTTP_401_UNAUTHORIZED
            )
            
        #### 3. refresh token이 유효한 상태임을 확인하면 새로운 access_token을 발급하고, 이를 쿠키에 담아 사용자에게 응답으로 보냄. 
        new_access_token = str(RefreshToken(refresh_token).access_token)
        response = Response({"detail": "token refreshed"}, status=status.HTTP_200_OK)
        response.set_cookie("access_token", value=str(new_access_token), httponly=True)
        return response