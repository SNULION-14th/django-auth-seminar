# ./account/views.py

from django.contrib.auth import get_user_model

from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed

from drf_spectacular.utils import extend_schema, inline_serializer

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.settings import api_settings

from account.request_serializers import (
    SignInRequestSerializer,
    SignUpRequestSerializer,
    TokenRefreshRequestSerializer,
)

from .serializers import UserSerializer


User = get_user_model()


def generate_token_in_serialized_data(user):
    token = RefreshToken.for_user(user)
    refresh_token = str(token)
    access_token = str(token.access_token)

    serialized_data = UserSerializer(user).data
    serialized_data["token"] = {
        "access": access_token,
        "refresh": refresh_token,
    }

    return serialized_data


def set_token_on_response_cookie(user, status_code):
    token = RefreshToken.for_user(user)
    refresh_token = str(token)
    access_token = str(token.access_token)

    user_data = UserSerializer(user).data

    # Swagger에서 access/refresh token을 복사하기 쉽도록 body에도 token 포함
    user_data["token"] = {
        "access": access_token,
        "refresh": refresh_token,
    }

    response = Response(user_data, status=status_code)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="Lax",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="Lax",
    )

    return response


def get_authenticated_user(request):
    """
    Authorization header에 access token이 있으면 header로 인증하고,
    없으면 cookie의 access_token으로 인증합니다.
    """

    jwt_authenticator = JWTAuthentication()

    try:
        # Authorization: Bearer <access_token> 방식 인증
        auth_result = jwt_authenticator.authenticate(request)

        if auth_result is not None:
            user, _ = auth_result
            return user

        # Cookie 기반 인증
        access_token = request.COOKIES.get("access_token")

        if not access_token:
            return None

        validated_token = jwt_authenticator.get_validated_token(access_token)
        user = jwt_authenticator.get_user(validated_token)

        return user

    except (InvalidToken, AuthenticationFailed):
        return None


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

            return set_token_on_response_cookie(
                user,
                status_code=status.HTTP_201_CREATED,
            )

        return Response(
            user_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


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

            return set_token_on_response_cookie(
                user,
                status_code=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {"message": "User does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )


class TokenRefreshView(APIView):
    @extend_schema(
        summary="토큰 재발급",
        description="access 토큰을 재발급 받습니다.",
        request=TokenRefreshRequestSerializer,
        responses={200: UserSerializer},
    )
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "no refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.verify()

        except TokenError:
            return Response(
                {"detail": "please signin again."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        new_access_token = str(token.access_token)

        response = Response(
            {"detail": "token refreshed"},
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=False,
            samesite="Lax",
        )

        return response


class LogoutView(APIView):
    @extend_schema(
        summary="로그아웃",
        description="사용자를 로그아웃 시키고 refresh token을 blacklist 처리합니다.",
        request=inline_serializer(
            name="LogoutRequestSerializer",
            fields={
                "refresh": serializers.CharField(),
            },
        ),
        responses={
            204: None,
            400: inline_serializer(
                name="LogoutBadRequestResponseSerializer",
                fields={
                    "detail": serializers.CharField(),
                },
            ),
            401: inline_serializer(
                name="LogoutUnauthorizedResponseSerializer",
                fields={
                    "detail": serializers.CharField(),
                },
            ),
        },
    )
    def post(self, request):
        user = get_authenticated_user(request)

        if user is None:
            return Response(
                {"detail": "please signin"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "no refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)

            token_user_id = token.payload.get(api_settings.USER_ID_CLAIM)
            request_user_id = getattr(user, api_settings.USER_ID_FIELD)

            if str(token_user_id) != str(request_user_id):
                return Response(
                    {"detail": "invalid refresh token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token.blacklist()

        except TokenError:
            return Response(
                {"detail": "invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response