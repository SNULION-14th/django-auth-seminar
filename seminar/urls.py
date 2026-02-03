# ./seminar/urls.py

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/post/', include('post.urls')), # post/의 urls.py 파일로 가서 url을 찾아라
    path('api/account/', include('account.urls')),  # account/의 urls.py 파일로 가서 url을 찾아라
    # 추가
    path('api/tag/', include('tag.urls')),  # tag/의 urls.py 파일로 가서 url을 찾아라

    # API 데이터 다운로드
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger 문서 진입
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]