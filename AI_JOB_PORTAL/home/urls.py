from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('submit_job/<int:job_id>/', views.submit_job, name='submit_job'),
    path('edit_info/',views.edit_info,name='edit_info'),
    path('success/',views.success,name='success'),


]