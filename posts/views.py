from django.db.models import Count
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_api.permissions import IsOwnerOrReadOnly
from .models import Post,Tag
from .serializers import PostSerializer,TagSerializer
from rest_framework.response import Response
from django.http import QueryDict


class PostList(generics.ListCreateAPIView):
    """
    List posts or create a post if logged in
    The perform_create method associates the post with the logged in user.
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Post.objects.annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comment', distinct=True)
    ).order_by('-created_at')
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    filterset_fields = [
        'owner__followed__owner__profile',
        'likes__owner__profile',
        'owner__profile',
    ]
    search_fields = [
        'owner__username',
        'title',
    ]
    ordering_fields = [
        'likes_count',
        'comments_count',
        'likes__created_at',
    ]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

        
    def create(self, request, *args, **kwargs):
        # Extract the tags data from the request
        tags_data = request.data.get('tags', [])

        # Ensure that tags_data is a list of strings
        if isinstance(tags_data, str):
            tags_data = [tag.strip() for tag in tags_data.split(',')]
        # Create a list to store the tags
        tags = []

        # Iterate over the tags data and create or retrieve the Tag objects
        for tag_name in tags_data:
            if tag_name:
                # Get or create the tag
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                tags.append(tag)
        # Create a mutable QueryDict object
        mutable_request_data = QueryDict('', mutable=True)

        # Set the tags data in the mutable request data
        mutable_request_data.setlist('tags', [tag.id for tag in tags])

        # Copy other data from the original request
        for key, value in request.data.items():
            if key != 'tags':
                mutable_request_data[key] = value

        # Set the mutable QueryDict as the request data
        request._full_data = mutable_request_data

        # Call the parent create method with the updated request data
        return super().create(request, *args, **kwargs)


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve a post and edit or delete it if you own it.
    """
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Post.objects.annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comment', distinct=True)
    ).order_by('-created_at')
    
    def update(self, request, *args, **kwargs):
        # Fetch the existing post object
        instance = self.get_object()
        print("Existing Post Instance:", instance)
        print("Request Data:", request.data)
        
        # Create serializer instance with existing post object and request data
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    


class TagList(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

