from django.urls import path

from dashboard import views

urlpatterns = [
	path('', views.Index.as_view()),
]
