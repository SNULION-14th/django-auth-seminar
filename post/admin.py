# ./post/admin.py

from django.contrib import admin
from .models import Post  # 우리가 만든 Post 모델 불러오기

# admin 사이트에 Post 모델 등록
admin.site.register(Post)