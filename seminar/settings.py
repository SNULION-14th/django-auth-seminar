# ./seminar/settings.py

from pathlib import Path
import environ
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# OS에서 선언된 DEBUG 변수를 불러오고, 만약 없다면 False로 기본값을 설정합니다
env = environ.Env(
    DEBUG=(bool, False)
)

# .env 파일을 가져와서, 해당 파일 내부의 SECRET_KEY라는 변수 내부의 값을 가져옵니다
environ.Env.read_env(
    env_file=BASE_DIR / '.env'
)

# 파이썬 변수 선언하여 해당 값을 할당
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework', # DRF 라이브러리
    'drf_spectacular', # Swagger 문서 생성 라이브러리
    'post.apps.PostConfig', # post/apps.py내에 정의된 PostConfig 클래스를 지칭
    'account.apps.AccountConfig', # account/apps.py내에 정의된 AccountConfig 클래스를 지칭
    # 추가
    'tag.apps.TagConfig', # tag/apps.py내에 정의된 TagConfig 클래스를 지칭
    'rest_framework_simplejwt',  # 🔹 JWT 라이브러리 추가
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'seminar.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'seminar.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = 'static/'

import os
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# AllowAny 뒤에 컴마 주의!
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES' : (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # 🔹 JWT를 인증 방식으로 사용
    )
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Likelion_API',
    'DESCRIPTION': 'DRF 세미나 API 명세서입니다.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # OTHER SETTINGS
    ## 추가
    # Swagger에서 전역적으로 사용할 보안 스키마 정의
    'SECURITY': [{'jwtAuth': []}],
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'jwtAuth': { 
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        }
    },
}

AUTH_USER_MODEL = 'account.User'

REST_USE_JWT = True  # 🔹 Django에서 JWT 사용을 활성화

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),  # 🔹 Access Token의 유효 기간: 30분
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),  # 🔹 Refresh Token의 유효 기간: 1일
    'ROTATE_REFRESH_TOKENS': True,  # 🔹 Refresh Token을 사용할 때마다 새 토큰 발급
    'BLACKLIST_AFTER_ROTATION': True,  # 🔹 이전 Refresh Token을 블랙리스트에 추가하여 재사용 방지
    'AUTH_HEADER_TYPES': ('Bearer',),  # 🔹 인증 헤더 타입을 "Bearer"로 설정
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),  # 🔹 Access Token 클래스를 지정
    'ACCESS_TOKEN': 'access_token',  # 🔹 Access Token의 이름 지정
    'REFRESH_TOKEN': 'refresh_token',  # 🔹 Refresh Token의 이름 지정
}