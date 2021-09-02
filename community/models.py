from django.contrib.auth.models import User
from django.db import models

from file.models import File


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    user = models.ForeignKey(User, related_name="post_user", on_delete=models.CASCADE)
    # file = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)  # File
    like = models.ManyToManyField(User, blank=True)



class PostComment(models.Model):
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="postcomment_user", on_delete=models.CASCADE)
    like = models.ManyToManyField(User, blank=True)



    # class Meta:
    #     db_table = '_'.join((__package__, 'post_comment'))


class Review(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    user = models.ForeignKey(User, related_name="review_user", on_delete=models.CASCADE)
    # file = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)
    # raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE)
    like = models.ManyToManyField(User, blank=True)



class ReviewComment(models.Model):
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="reviewcomment_user", on_delete=models.CASCADE)
    like = models.ManyToManyField(User, blank=True)




class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # file = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)  # File


# ================= #
# Question & Answer #
# ================= #

class QuestionType(models.Model):
    name = models.CharField(max_length=100)

class Question(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # file = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)  # File
    question_type = models.ForeignKey(QuestionType, on_delete=models.SET_NULL, null=True)



class Answer(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # file = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)  # File
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
