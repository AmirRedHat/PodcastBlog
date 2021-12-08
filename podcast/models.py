from django.db import models
from django.http.response import Http404

from datetime import datetime
from account.models import User
from .manager import EpisodeManager
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=150)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Podcast(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="podcast_user")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="podcast_category")
    cover = models.ImageField(default="default.jpg")
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    mark = models.ManyToManyField(User, related_name="podcast_mark")

    objects = models.Manager()

    class Meta:
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["-date"])
        ]

    def __str__(self):
        return self.title


def file_validator(file):
    file_name = file.name.split('/')[-1] or file.name.split("\\")[-1]
    if file_name.endswith("mp3") or file_name.endswith("wav") or file_name.endswith("m4a"):
        if ".py" not in file_name or ".exe" not in file_name or ".php" not in file_name or ".js" not in file_name:
            return file
    else:
        raise Http404("file format is invalid")


class Episode(models.Model):
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE, related_name="episode_podcast")
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to="episodes/", validators=[file_validator])
    date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=None)
    like = models.ManyToManyField(User, related_name="episode_like")
    saved = models.ManyToManyField(User, related_name="episode_saved")

    objects = models.Manager()
    manager = EpisodeManager()

    class Meta:
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["podcast"])
        ]

    def __str__(self) -> str:
        return f"{self.podcast}-{self.title}"

    def create_episode(self, **fields):
        self.title = fields.get("title")
        self.description = fields.get("description")
        self.podcast = fields.get("podcast")
        self.file = fields.get("file")
        self.updated_at = datetime.now()
        self.save()

    def like_episode(self, request):
        user = request.user
        if user in self.like.all():
            self.like.remove(user)
        else:
            self.like.add(user)


class Comment(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name="comment_episode")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_user")
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    like = models.ManyToManyField(User, related_name="comment_like")

    objects = models.Manager()

    class Meta:
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["episode"]),
            models.Index(fields=["user"])
        ]

    def __str__(self):
        return self.text
