from django.views.generic import DetailView, ListView, DeleteView, UpdateView, FormView, View
from django.shortcuts import get_object_or_404, redirect, render
from django.http.response import Http404

from .models import Podcast, Episode, Comment, Category
from .forms import PublishPodcastForm, PublishCategoryForm, PublishEpisodeForm
from .mixins import AccessSuperUserMixin
from account.mixins import LoginMixin

from datetime import datetime


# Create your views here.


class Podcasts(ListView):
    model = Podcast
    template_name = "podcasts.html"
    context_object_name = "podcasts"
    paginate_by = 6


class PodcastView(DetailView):
    model = Podcast
    template_name = "episodes.html"
    context_object_name = "podcast"

    def get_context_data(self, *args, **kwargs):
        context = super(PodcastView, self).get_context_data()
        episodes = Episode.manager.get_episodes(podcast_object=self.object)
        context["episodes"] = episodes
        return context


class DeletePodcast(DeleteView):
    model = Podcast
    success_url = "/"


class UpdatePodcast(UpdateView):
    model = Podcast
    fields = ("title", "description")
    template_name = "update_podcast.html"
    success_url = "/"

    def form_valid(self, form, *args, **kwargs):
        form.save()
        return super(UpdatePodcast, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(UpdatePodcast, self).get_context_data()
        context["object"] = self.object
        return context


class CategoryView(ListView):
    model = Category
    template_name = "category.html"
    context_object_name = "categories"


class PublishCategory(AccessSuperUserMixin, FormView):
    form_class = PublishCategoryForm
    template_name = "publish_category.html"
    success_url = "/"

    def form_valid(self, form, *args, **kwargs):
        form.save()
        return super(PublishCategory, self).form_valid(form)


class PublishPodcast(FormView):
    form_class = PublishPodcastForm
    template_name = "publish_podcast.html"
    success_url = "/"

    def form_valid(self, form, *args, **kwargs):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()
        return super(PublishPodcast, self).form_valid(form)


class Episodes(ListView):
    model = Episode
    template_name = "episodes.html"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["podcast"] = get_object_or_404(Podcast, pk=kwargs.get('pk'))


class EpisodeView(DetailView):
    model = Episode
    template_name = "episode.html"

    def get_context_data(self, *args, **kwargs):
        context = super(EpisodeView, self).get_context_data()
        context["comments"] = Comment.objects.filter(episode=self.object)
        return context


class DeleteEpisode(DeleteView):
    model = Episode
    success_url = "/"


class UpdateEpisode(UpdateView):
    model = Episode
    fields = ("title", "description", "file", "podcast")
    success_url = "/"
    template_name = "update_episode.html"

    def form_valid(self, form, *args, **kwargs):
        now = datetime.now()
        instance = form.save(commit=False)
        instance.updated_at = now
        instance.save()
        return super(UpdateEpisode, self).form_valid(form)


class PublishEpisode(View):
    template_name = "publish_episode.html"

    def get(self, *args, **kwargs):
        user_podcasts = Podcast.objects.filter(user=self.request.user)
        context = {"podcasts": user_podcasts}
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        data = self.request.POST
        title = data["title"]
        file = self.request.FILES["file"]
        podcast = get_object_or_404(Podcast, pk=data["podcast"])

        if not Episode.objects.filter(podcast=podcast, title=title):
            episode = Episode()
            episode.create_episode(title=title,
                                   description=data["description"],
                                   podcast=podcast,
                                   file=file)
        else:
            raise Http404("This title is already used in your podcast . please change it")
        return redirect("Podcast:podcast", pk=data["podcast"])


class LikeEpisode(View):

    def post(self, *args, **kwargs):
        episode_pk = self.request.POST.get("episode_id")
        episode = get_object_or_404(Episode, pk=episode_pk)
        episode.like_episode(request=self.request)
        episode.save()
        return redirect("Podcast:episode", pk=episode_pk)


class PublishComment(LoginMixin, View):

    def post(self, *args, **kwargs):
        body = self.request.POST.get("body")
        episode_id = self.request.POST.get("episode_id")
        episode = get_object_or_404(Episode, pk=episode_id)
        user = self.request.user

        comment = Comment()
        comment.text = body
        comment.episode = episode
        comment.user = user
        comment.save()
        return redirect("Podcast:episode", pk=episode_id)


class DeleteComment(DeleteView):
    model = Comment
    success_url = "/"


class MarkPodcast(View):

    def get(self, *args, **kwargs):
        podcast_pk = kwargs.get("podcast_pk")
        podcast = get_object_or_404(Podcast, pk=podcast_pk)
        user = self.request.user

        if user in podcast.mark.all():
            podcast.mark.remove(user)
        else:
            podcast.mark.add(user)
        podcast.save()

        return redirect("Podcast:podcast", pk=podcast_pk)
