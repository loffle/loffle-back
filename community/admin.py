from django.contrib import admin

# Register your models here.
from community.models import Post, PostComment, QuestionType

admin.site.register(Post)
admin.site.register(PostComment)
admin.site.register(QuestionType)
