from django.db.models.manager import BaseManager
from django.shortcuts import get_object_or_404
from account.models import User


class EpisodeManager(BaseManager):

    def get_episodes(self, podcast_object):
        return self.model.objects.filter(podcast=podcast_object)


class PodcastManager(BaseManager):

    def get_podcasts(self, *args, **kwargs):
        user = kwargs.get("user")
        if type(user) == str:
            user = get_object_or_404(User, email=user)
            return self.model.objects.filter(user=user)
        elif type(user) == int:
            user = get_object_or_404(User, pk=user)
            return self.model.objects.filter(user=user)
        elif isinstance(user, User):
            return self.model.objects.filter(user=user)
