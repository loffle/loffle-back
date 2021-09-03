from django.contrib.auth.models import User
from django.db import models

from file.models import File


class CommonManager(models.Manager):
    def get_queryset(self):
        # queryset = Post.objects.filter(is_deleted=False)
        # queryset = Post.objects.filter(is_deleted=False).prefetch_related('like').select_related('user')
        # 세 queryset 성능 및 속도 비교해보기
        return super().get_queryset().prefetch_related('like').select_related('user').filter(is_deleted=False)


# --------------------------------------------------------

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, editable=False)

    user = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    # file = models.ManyToManyField(File, on_delete=models.SET_NULL, null=True, blank=True)  # File
    like = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    objects = CommonManager()


class PostComment(models.Model):
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, editable=False)

    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="postcomments", on_delete=models.CASCADE)
    like = models.ManyToManyField(User, related_name="liked_postcomments", blank=True)

    # class Meta:
    #     db_table = '_'.join((__package__, 'post_comment'))
    objects = CommonManager()


class Review(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, editable=False)

    user = models.ForeignKey(User, related_name="reviews", on_delete=models.CASCADE)
    # file = models.ManyToManyField(File, on_delete=models.SET_NULL, null=True, blank=True)
    # raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE)
    like = models.ManyToManyField(User, related_name="liked_reviews", blank=True)

    objects = CommonManager()


class ReviewComment(models.Model):
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, editable=False)

    review = models.ForeignKey(Review, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="reviewcomments", on_delete=models.CASCADE)
    like = models.ManyToManyField(User, related_name="liked_reviewcomments", blank=True)

    objects = CommonManager()


class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, editable=False)

    user = models.ForeignKey(User, related_name="notices", on_delete=models.CASCADE)
    # file = models.ManyToManyField(File, on_delete=models.SET_NULL, null=True, blank=True)  # File

    objects = CommonManager()


# ================= #
# Question & Answer #
# ================= #

class QuestionType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Question(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, editable=False)

    user = models.ForeignKey(User, related_name="questions", on_delete=models.CASCADE)
    # file = models.ManyToManyField(File, on_delete=models.SET_NULL, null=True, blank=True)  # File
    question_type = models.ForeignKey(QuestionType, related_name="questions", on_delete=models.SET_NULL, null=True)

    objects = CommonManager()


class Answer(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, editable=False)

    user = models.ForeignKey(User, related_name="answers", on_delete=models.CASCADE)
    # file = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)  # File
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)

    objects = CommonManager()
