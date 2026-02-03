# ./post/urls.py

from django.urls import path
# 수정
from .views import PostListView, PostDetailView, LikeView

app_name = 'post'

# api/post/로 시작하는 url은 이곳으로 왔다.
# 그 이후에 붙는 것부터 여기서 찾는 것이다.
# 예) api/post/3이라면 <int:post_id>로
urlpatterns = [
    # CBV url path
    path("", PostListView.as_view()),
    path("<int:post_id>/", PostDetailView.as_view()),
    # 추가
    path("<int:post_id>/like/", LikeView.as_view()),
]