from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('submit_job/<int:job_id>/', views.submit_job, name='submit_job'),


]