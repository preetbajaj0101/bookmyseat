from django.db import models
from django.contrib.auth.models import User


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    LANGUAGE_CHOICES = [
        ('EN', 'English'),
        ('HI', 'Hindi'),
        ('ES', 'Spanish'),
        ('FR', 'French'),
    ]

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="movies/")
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    cast = models.TextField()
    description = models.TextField(blank=True, null=True)
    genres = models.ManyToManyField(Genre)
    language = models.CharField(
        max_length=2, choices=LANGUAGE_CHOICES, default='EN')

    def __str__(self):
        return self.name


class Auditorium(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Theater(models.Model):
    name = models.CharField(max_length=255)
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name='theaters')

    def __str__(self):
        return f'{self.name} - {self.movie.name}'


class Show(models.Model):
    theater = models.ForeignKey(
        Theater, on_delete=models.CASCADE, related_name='shows')
    auditorium = models.ForeignKey(Auditorium, on_delete=models.CASCADE)
    time = models.DateTimeField()

    def __str__(self):
        return f'{self.theater.name} - {self.auditorium.name} at {self.time}'


class Seat(models.Model):
    TIER_CHOICES = [
        ('PLATINUM', 'Platinum'),
        ('GOLD', 'Gold'),
        ('SILVER', 'Silver'),
    ]
    show = models.ForeignKey(
        Show, on_delete=models.CASCADE, related_name='seats', null=True)
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)
    tier = models.CharField(
        max_length=10, choices=TIER_CHOICES, default='SILVER')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=150.00)

    def __str__(self):
        if self.show:
            return f'{self.seat_number} in {self.show.auditorium.name}'
        return self.seat_number


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    show = models.ForeignKey(Show, on_delete=models.CASCADE, null=True)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Booking by {self.user.username} for {self.seat.seat_number} at {self.show.theater.name}'