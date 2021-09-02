from django.db import models


class FileType(models.Model):
    name = models.CharField(max_length=200)


class File(models.Model):
    url = models.URLField()

    type = models.ForeignKey(FileType, on_delete=models.SET_NULL, null=True, blank=True)
