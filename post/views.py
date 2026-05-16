# ./post/views.py

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
# 수정
from .models import Post, Like
from .serializers import PostSerializer
from .request_serializers import PostListRequestSerializer, PostDetailRequestSerializer

from django.contrib.auth import get_user_model
from tag.models import Tag
from account.request_serializers import SignInRequestSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter

User = get_user_model()

class PostListView(APIView):
    @extend_schema(
        summary="게시글 목록 조회",
        description="게시글 목록을 조회합니다.",
        responses={
            200: PostSerializer(many=True),
            404: "Not Found",
            400: "Bad Request",
        },
    )
    def get(self, request): 
        posts = Post.objects.all() # Post를 다 가져와라
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
       
        
    @extend_schema(
        summary="게시글 생성",
        description="게시글을 생성합니다.",
        request=PostListRequestSerializer,
        responses={201: PostSerializer, 404: "Not Found", 400: "Bad Request", 401: "Unauthorized"},
    )
    
    def post(self, request):
        title = request.data.get("title")
        content = request.data.get("content")
        tag_contents = request.data.get("tags")
        author = request.user
        if not author.is_authenticated:
            return Response(
                {"detail": "please signin"}, status=status.HTTP_401_UNAUTHORIZED
            )
        if not title or not content:
            return Response(
                {"detail": "[title, content] fields missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ## 유저 정보를 바로 넣어서 post 생성!
        post = Post.objects.create(title=title, content=content, author=author)

        if tag_contents is not None:
            for tag_content in tag_contents:
                if not Tag.objects.filter(content=tag_content).exists():
                    post.tags.create(content=tag_content)
                else:
                    post.tags.add(Tag.objects.get(content=tag_content))

        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PostDetailView(APIView):
    @extend_schema(
        summary="게시글 상세 조회",
        description="게시글 1개의 상세 정보를 조회합니다.",
        responses={200: PostSerializer, 400: "Bad Request"},
    )
    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(instance=post)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="게시글 삭제",
        description="게시글을 삭제합니다.",
        request=SignInRequestSerializer,
        responses={204: "No Content", 404: "Not Found", 400: "Bad Request"},
    )
    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except:
            return Response(
                {"detail": "Post Not found."}, status=status.HTTP_404_NOT_FOUND
            )
        author = request.user
        if not author.is_authenticated:
            return Response(
                {"detail": "please signin"}, status=status.HTTP_401_UNAUTHORIZED
            )
        if post.author != author:
            return Response(
                {"detail": "You are not the author of this post."},
                status=status.HTTP_403_FORBIDDEN,
            )

        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="게시글 수정",
        description="게시글을 수정합니다.",
        request=PostDetailRequestSerializer,
        responses={200: PostSerializer, 404: "Not Found", 400: "Bad Request"},
    )
    def put(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except:
            return Response(
                {"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND
            )

        author = request.user
        if not author.is_authenticated:
            return Response(
                {"detail": "please signin"}, status=status.HTTP_401_UNAUTHORIZED
            )
        if post.author != author:
            return Response(
                {"detail": "You are not the author of this post."},
                status=status.HTTP_403_FORBIDDEN,
            )

        title = request.data.get("title")
        content = request.data.get("content")
        if not title or not content:
            return Response(
                {"detail": "[title, content] fields missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        post.title = title
        post.content = content

        tag_contents = request.data.get("tags")
        if tag_contents is not None:
            post.tags.clear()
            for tag_content in tag_contents:
                if not Tag.objects.filter(content=tag_content).exists():
                    post.tags.create(content=tag_content)
                else:
                    post.tags.add(Tag.objects.get(content=tag_content))
        post.save()
        serializer = PostSerializer(instance=post)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LikeView(APIView):
    @extend_schema(
        summary="좋아요 토글",
        description="좋아요를 토글합니다. 이미 좋아요가 눌려있으면 취소합니다.",
        request=SignInRequestSerializer,
        responses={200: PostSerializer, 404: "Not Found", 400: "Bad Request"},
    )
    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except:
            return Response(
                {"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND
            )
        author = request.user
        if not author.is_authenticated:
            return Response(
                {"detail": "please signin"}, status=status.HTTP_401_UNAUTHORIZED
            )

        is_liked = post.like_set.filter(user=author).count() > 0

        if is_liked == True:
            post.like_set.get(user=author).delete()
            print("좋아요 취소")
        else:
            Like.objects.create(user=author, post=post)
            print("좋아요 누름")

        serializer = PostSerializer(instance=post)
        return Response(serializer.data, status=status.HTTP_200_OK)