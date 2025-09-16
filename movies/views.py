from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Theater, Seat, Booking, Genre, Show
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from collections import defaultdict

def movie_list(request):
    search_query = request.GET.get('search')
    genre_filters = request.GET.getlist('genre')
    language_filter = request.GET.get('language')

    movies = Movie.objects.all()

    if search_query:
        movies = movies.filter(name__icontains=search_query)

    if genre_filters:
        movies = movies.filter(genres__name__in=genre_filters).distinct()

    if language_filter:
        movies = movies.filter(language=language_filter)

    genres = Genre.objects.all()
    languages = Movie.LANGUAGE_CHOICES

    return render(request, 'movies/movie_list.html', {
        'movies': movies,
        'genres': genres,
        'languages': languages,
        'selected_genres': genre_filters,
        'selected_language': language_filter
    })


def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie=movie)
    return render(request, 'movies/theater_list.html', {'movie': movie, 'theaters': theaters})


def show_list(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)
    shows = Show.objects.filter(theater=theater)
    return render(request, 'movies/show_selection.html', {'theater': theater, 'shows': shows})


@login_required(login_url='/login/')
def book_seats(request, show_id):
    show = get_object_or_404(Show, id=show_id)
    
    seats_query = Seat.objects.filter(show=show).order_by('seat_number')

    seat_rows = defaultdict(list)
    for seat in seats_query:
        row_letter = seat.seat_number[0] 
        seat_rows[row_letter].append(seat)

    # Sort rows in reverse alphabetical order to place 'A' at the back
    sorted_seat_rows = sorted(seat_rows.items(), reverse=True)

    if request.method == 'POST':
        selected_Seats = request.POST.getlist('seats')
        error_seats = []
        if not selected_Seats:
            return render(request, "movies/seat_selection.html", {'show': show, "seat_rows": sorted_seat_rows, 'error': "No seat selected"})
        
        for seat_id in selected_Seats:
            seat = get_object_or_404(Seat, id=seat_id, show=show)
            if seat.is_booked:
                error_seats.append(seat.seat_number)
                continue
            try:
                Booking.objects.create(
                    user=request.user, seat=seat, movie=show.theater.movie, show=show
                )
                seat.is_booked = True
                seat.save()
            except IntegrityError:
                error_seats.append(seat.seat_number)
        
        if error_seats:
            error_message = f"The following seats are already booked: {', '.join(error_seats)}"
            return render(request, 'movies/seat_selection.html', {'show': show, "seat_rows": sorted_seat_rows, 'error': error_message})
        
        return redirect('profile')
    
    return render(request, 'movies/seat_selection.html', {'show': show, "seat_rows": sorted_seat_rows})