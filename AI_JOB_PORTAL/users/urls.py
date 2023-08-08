from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout/', views.user_logout, name='logout'),
    path('admin', views.admin, name='admin'),

]