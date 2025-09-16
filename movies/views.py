from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Theater, Seat, Booking
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

def movie_list(request):
    search_query = request.GET.get('search')
    if search_query:
        movies = Movie.objects.filter(name__icontains=search_query)
    else:
        movies = Movie.objects.all()
    return render(request, 'movies/movie_list.html', {'movies': movies})

def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie=movie)
    return render(request, 'movies/theater_list.html', {'movie': movie, 'theaters': theaters})

@login_required(login_url='/login/')
def book_seats(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)
    seats = Seat.objects.filter(theater=theater)
    if request.method == 'POST':
        selected_seats_ids = request.POST.getlist('seats')
        
        if not selected_seats_ids:
            return render(request, "movies/seat_selection.html", {'theaters': theater, "seats": seats, 'error': "No seat selected"})

        error_seats = []
        for seat_id in selected_seats_ids:
            seat = get_object_or_404(Seat, id=seat_id, theater=theater)
            if seat.is_booked:
                error_seats.append(seat.seat_number)
        
        if error_seats:
            error_message = f"The following seats are already booked: {', '.join(error_seats)}"
            return render(request, 'movies/seat_selection.html', {'theaters': theater, "seats": seats, 'error': error_message})

        for seat_id in selected_seats_ids:
            seat = get_object_or_404(Seat, id=seat_id, theater=theater)
            try:
                Booking.objects.create(
                    user=request.user,
                    seat=seat,
                    movie=theater.movie,
                    theater=theater
                )
                seat.is_booked = True
                seat.save()
            except IntegrityError:
                # This handles the rare case where the seat is booked between the check and the creation
                error_message = f"The seat {seat.seat_number} was booked by another user. Please select another seat."
                return render(request, 'movies/seat_selection.html', {'theaters': theater, "seats": seats, 'error': error_message})

        return redirect('profile')
        
    return render(request, 'movies/seat_selection.html', {'theaters': theater, "seats": seats})