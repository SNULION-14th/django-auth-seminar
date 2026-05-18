# ./account/views.py

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from account.request_serializers import (
    LogoutRequestSerializer,
    SignInRequestSerializer,
    SignUpRequestSerializer,
    TokenRefreshRequestSerializer,
)
from .serializers import AccessTokenResponseSerializer, TokenResponseSerializer, UserSerializer

User = get_user_model()


def get_token_data(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def get_auth_response(user, status_code):
    token_data = get_token_data(user)
    response = Response(token_data, status=status_code)
    response.set_cookie("access_token", value=token_data["access"], httponly=True)
    response.set_cookie("refresh_token", value=token_data["refresh"], httponly=True)
    return response


class SignUpView(APIView):
    @extend_schema(
        summary="회원가입",
        description="회원가입을 진행하고 access token과 refresh token을 발급합니다.",
        request=SignUpRequestSerializer,
        responses={201: TokenResponseSerializer, 400: "Bad Request"},
    )
    def post(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.save()
            user.set_password(request.data.get("password"))
            user.save()

            return get_auth_response(user, status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignInView(APIView):
    @extend_schema(
        summary="로그인",
        description="로그인을 진행하고 access token과 refresh token을 발급합니다.",
        request=SignInRequestSerializer,
        responses={200: TokenResponseSerializer, 404: "Not Found", 400: "Bad Request"},
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
            return get_auth_response(user, status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )


class TokenRefreshView(APIView):
    @extend_schema(
        summary="토큰 재발급",
        description="refresh token을 검증한 뒤 새로운 access token을 발급합니다.",
        request=TokenRefreshRequestSerializer,
        responses={200: AccessTokenResponseSerializer, 400: "Bad Request", 401: "Unauthorized"},
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            refresh.verify()
            access_token = str(refresh.access_token)
        except TokenError:
            return Response(
                {"detail": "invalid or blacklisted refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = Response({"access": access_token}, status=status.HTTP_200_OK)
        response.set_cookie("access_token", value=access_token, httponly=True)
        return response


class LogoutView(APIView):
    @extend_schema(
        summary="로그아웃",
        description="refresh token을 blacklist에 등록하고 토큰 쿠키를 삭제합니다.",
        request=LogoutRequestSerializer,
        responses={204: None, 400: "Bad Request", 401: "Unauthorized"},
    )
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"detail": "invalid or already blacklisted refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response
