from django.urls import path

from dashboard import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('b3/pairs_ranking', views.BovespaListView.as_view(), name='b3-pairs'),
    path('b3/pair_stats/<str:x>/<str:y>', views.PairStatsListView.as_view(), name='pairs-stats'),
]