
# Register your models here.
# account/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # 1. 유저 목록 화면에서 보여줄 필드 설정
    list_display = ('id', 'username', 'college', 'major', 'is_staff')
    
    # 2. 유저 상세 수정 화면에 커스텀 필드 추가
    # 기본 필드셋 뒤에 'Additional Info'라는 섹션으로 대학과 전공을 추가합니다.
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('college', 'major')}),
    )

    # 3. 유저 생성 화면에도 커스텀 필드 추가
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('college', 'major')}),
    )