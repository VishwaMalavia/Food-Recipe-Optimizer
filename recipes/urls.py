from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('recipe/', views.recipe_view, name='recipe'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('favorite/', views.favorite_list, name='favorite'),
    path('toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
]
