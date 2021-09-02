from rest_framework import serializers

from community.models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        # fields = ('id', 'title', 'content', 'created_at', 'modified_at')
        # read_only_fields = ['user', 'like']