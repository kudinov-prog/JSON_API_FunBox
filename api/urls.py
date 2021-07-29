from django.urls import path

from .views import PostVisitsView, GetDomainsView


urlpatterns = [
    path('visited_links', PostVisitsView.as_view()),
    path('visited_domains', GetDomainsView.as_view())
]
