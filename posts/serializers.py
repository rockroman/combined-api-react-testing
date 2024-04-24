from rest_framework import serializers
from posts.models import Post,Tag
from likes.models import Like
import json


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [ 'id','name',]


class PostSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    is_owner = serializers.SerializerMethodField()
    profile_id = serializers.ReadOnlyField(source='owner.profile.id')
    profile_image = serializers.ReadOnlyField(source='owner.profile.image.url')
    # tags = TagSerializer(many=True, read_only=False)
    like_id = serializers.SerializerMethodField()
    likes_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()
    

    def validate_mp3(self, value):
        request = self.context.get('request')
        if request and request.method == 'POST':
            if value is None:
                return 
            if value:
                if not value.name.lower().endswith('.mp3'):
                    raise serializers.ValidationError("Only MP3 audio files are allowed.")
                elif value.size > 50 * 1024 * 1024:
                    raise serializers.ValidationError('MP3 file size larger than 50MB!')
        else:
            if value is None:
                return self.instance.mp3
            if value:
                if not value.name.lower().endswith('.mp3'):
                    raise serializers.ValidationError("Only MP3 audio files are allowed.")
                elif value.size > 50 * 1024 * 1024:
                    raise serializers.ValidationError('MP3 file size larger than 50MB!')
        return value
        
    def validate_video(self, value):
        request = self.context.get('request')
        if request and request.method == 'POST':
            if value is None:
                return 
            if not value.name.lower().endswith(('.mp4', '.avi', '.mov')):
                raise serializers.ValidationError("Only MP4, AVI, and MOV video files are allowed.")
            elif value.size > 50 * 1024 * 1024:
                raise serializers.ValidationError('Video size larger than 50MB!')
        else:
            if value is None:
                return self.instance.video
            if not value.name.lower().endswith(('.mp4', '.avi', '.mov')):
                raise serializers.ValidationError("Only MP4, AVI, and MOV video files are allowed.")
            elif value.size > 50 * 1024 * 1024:
                raise serializers.ValidationError('Video size larger than 50MB!')
        return value
    

    def validate_image(self, value):
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError('Image size larger than 2MB!')
        if value.image.height > 4096:
            raise serializers.ValidationError(
                'Image height larger than 4096px!'
            )
        if value.image.width > 4096:
            raise serializers.ValidationError(
                'Image width larger than 4096px!'
            )
        return value
    
    def validate(self, data):
        print("data in validate method ",data)

        # added not to trigger validate method since uploaded file was validated on Post
        # request and no need validating if instance is not changing
        # also checking if instance exists to prevent error when creating post with no
        # files 
        if 'mp3' in data and self.instance and self.instance.mp3 != data['mp3']:
            mp3 = data.get('mp3')
            print(mp3)
            # Validate video file
            self.validate_mp3(mp3)

        # Check if 'video' field is present in the data and has changed
        # added not to trigger validate method since uploaded file was validated on Post
        # request and no need validating if instance is not changing
        if 'video' in data and self.instance and  self.instance.video != data['video']:
            video = data.get('video')
            # Validate video file
            self.validate_video(video)

        # Check if 'image' field is present in the data
        if 'image' in data:
            image = data.get('image')
            # Validate image file
            self.validate_image(image)

        return data

    def get_is_owner(self, obj):
        request = self.context['request']
        return request.user == obj.owner

    def get_like_id(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            like = Like.objects.filter(
                owner=user, post=obj
            ).first()
            return like.id if like else None
        return None
    
    
    # def create(self, validated_data):
    #     # Extract tags data from validated data
    #     tags_data = validated_data.pop('tags', [])
        
    #     # Create post instance
    #     post = Post.objects.create(**validated_data)

    #     # Create and associate tags with the post
    #     for tag_data in tags_data:
    #         tag_name = tag_data.get('name')
    #         if tag_name:
    #             tag, _ = Tag.objects.get_or_create(name=tag_name)
    #             post.tags.add(tag)

    #     return post

    class Meta:
        model = Post
        fields = [
            'id', 'owner', 'is_owner', 'profile_id',
            'profile_image','tags', 'created_at', 'updated_at',
            'title', 'content', 'image', 'image_filter',
            'like_id', 'likes_count', 'comments_count','video','mp3',
        ]
        extra_kwargs = {
            'image': {'required': False}
        }
