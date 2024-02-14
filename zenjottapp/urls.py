from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('journal/', views.journal, name='journal'),
    path('log_mood/', views.log_mood, name='log_mood'),
    path('log_entry/', views.log_entry, name='log_entry'),
    path('new_entry/', views.new_entry, name='new_entry'),
    path('make_post', views.make_post, name='make_post'),
    path('memes/', views.memes, name='memes'),
    path('resources/', views.resources, name='resources'),
    path('community', views.community, name='community'),
    path('create/', views.create, name='create'),
    path('comment/<int:pk>', views.comment, name='comment'),
    path('moodtracker/', views.moodtracker, name='moodtracker'),
    path('<int:pk>', views.entry, name='entry'),
    path('delete/<int:pk>', views.delete, name='delete'),
    path('edit/<int:pk>', views.edit, name='edit'),
    path('register/', views.register, name='register'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout')
]