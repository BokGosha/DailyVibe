from django.urls import path
from . import views


app_name = 'blog'

urlpatterns = [
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.user_profile, name='profile'),
    path('profile/<str:username>/follow/', views.user_follow, name='follow'),
    path('profile/<str:username>/delete_follow/',
         views.delete_follow, name='delete_follow'),
    path('following/', views.following, name='following'),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'),
    path(
        'location/<slug:location_slug>/',
        views.location_posts,
        name='location_posts'),
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/comment/',
         views.add_comment, name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.edit_comment, name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.delete_comment, name='delete_comment'),
    path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('', views.index, name='index'),
]
