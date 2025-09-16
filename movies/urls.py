from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('<int:movie_id>/theaters', views.theater_list, name='theater_list'),
    path('theater/<int:theater_id>/shows',
         views.show_list, name='show_list'),
    path('show/<int:show_id>/seats/book/',
         views.book_seats, name='book_seats'),
]