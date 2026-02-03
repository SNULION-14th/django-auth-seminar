# ./post/models.py

# Model 관련 fields, methods를 모아놓은 놈입니다
from django.db import models
# 현재 시간 알기 위해
from django.utils import timezone
# 지금 우리가 관심 있는건 settings에서 선언한 유저 모델
from django.conf import settings

# 추가
from tag.models import Tag

# models.Model을 상속하여 Post라는 class를 선언해줍니다
class Post(models.Model):
		# title은 최대 256자의 character!
    title = models.CharField(max_length=256)
    
    # content는 글자 제한 없는 텍스트
    content = models.TextField()
    
    # created_at의 경우는 현재 시간 자동으로 입력되게!
    created_at = models.DateTimeField(default=timezone.now)

    # settings.AUTH_USER_MODEL로부터 유저 모델 참조
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)

    # 좋아요 누른 유저들
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='like_posts', through='Like')

    # 추가
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')

	# 이건 print하면 어떤 값을 return할 지 알려주는 것!
    def __str__(self):
        return self.title


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)