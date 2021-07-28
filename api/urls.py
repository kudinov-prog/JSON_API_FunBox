from django.urls import path

from .views import PostVisitsView


urlpatterns = [
    path('visited_links', PostVisitsView.as_view())
]
