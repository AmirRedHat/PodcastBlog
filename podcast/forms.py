from django.forms import ModelForm
from .models import Podcast, Episode, Category


class PublishCategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ("name", )


class PublishPodcastForm(ModelForm):
    class Meta:
        model = Podcast
        fields = ("category", "title", "description")


class PublishEpisodeForm(ModelForm):
    class Meta:
        model = Episode
        fields = ("podcast", "title", "description", "file")
