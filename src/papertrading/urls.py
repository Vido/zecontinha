from django.urls import path

from papertrading import views

urlpatterns = [
    path('', views.TradesListView.as_view(), name='blotter'),
    path('boleta', views.EnterTradesFormView.as_view(), name='boleta'),
    path('liquida', views.ExitTradesFormView.as_view(), name='liquida'),
]
