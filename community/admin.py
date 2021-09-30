from django.contrib import admin

# Register your models here.
from community.models import Post, PostComment, QuestionType, ReviewComment, Review, Question, Answer, Notice

admin.site.register(Post)
admin.site.register(PostComment)
admin.site.register(Review)
admin.site.register(ReviewComment)
admin.site.register(QuestionType)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Notice)
