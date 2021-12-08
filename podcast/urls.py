from django.urls import path
from . import views

app_name = "Podcast"
urlpatterns = [
    path("podcasts", views.Podcasts.as_view(), name="podcasts"),
    path("", views.Podcasts.as_view(), name="podcasts"),
    path("podcast/<int:pk>", views.PodcastView.as_view(), name="podcast"),
    path("podcast/delete", views.DeletePodcast.as_view(), name="delete_podcast"),
    path("podcast/update", views.UpdatePodcast.as_view(), name="update_podcast"),
    path("podcast/publish", views.PublishPodcast.as_view(), name="publish_podcast"),
    path("podcast/mark/<int:podcast_pk>", views.MarkPodcast.as_view(), name="mark_podcast"),

    path("category/", views.CategoryView.as_view(), name="category"),
    path("category/publish", views.PublishCategory.as_view(), name="publish_category"),


    path("episode/<int:pk>", views.EpisodeView.as_view(), name="episode"),
    path("episode/delete/<int:pk>", views.DeleteEpisode.as_view(), name="delete_episode"),
    path("episode/update/<int:pk>", views.UpdateEpisode.as_view(), name="update_episode"),
    path("episode/publish", views.PublishEpisode.as_view(), name="publish_episode"),
    path("episode/like", views.LikeEpisode.as_view(), name="like_episode"),

    path("comment/publish", views.PublishComment.as_view(), name="publish_comment"),
    path("comment/delete", views.DeleteComment.as_view(), name="delete_comment"),

    # path("search_podcast/", views.SearchPodcast.as_view(), name="search_podcast"),
    # path("search_publisher/", views.SearchPublisher.as_view(), name="search_publisher"),
]
