from django.contrib.auth.models import User
from django.db import models

from file.models import File


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(User, related_name="post_user", on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.SET_NULL, null=True)  # File
    like = models.ManyToManyField(User)


class PostComment(models.Model):
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="post_comment_user", on_delete=models.CASCADE)
    like = models.ManyToManyField(User)


# class Review(models.Model):
#     title = models.CharField(max_length=200)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     modified_at = models.DateTimeField(auto_now=True)
#
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     file = models.ForeignKey(File, on_delete=models.SET_NULL)
#     raffle = models.ForeignKey(Raffle, on_delete=models.SET_NULL)
#     like = models.ManyToManyField(User)
#
#
# class ReviewComment(models.Model):
#     content = models.CharField(max_length=200)
#     created_at = models.DateTimeField(auto_now_add=True)
#     modified_at = models.DateTimeField(auto_now=True)
#
#     review = models.ForeignKey(Review, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     like = models.ManyToManyField(User)

