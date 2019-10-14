from django.urls import path

from papertrading import views

urlpatterns = [
    path('', views.TradesListView.as_view(), name='blotter'),
]