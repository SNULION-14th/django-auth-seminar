# ./post/serializers.py

from rest_framework.serializers import ModelSerializer
from tag.serializers import TagSerializer
from .models import Post

class PostSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    class Meta:
        model = Post
        fields = "__all__"