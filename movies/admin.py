from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render, redirect
from django.utils.html import format_html
from .models import Movie, Theater, Seat, Booking, Genre, Auditorium, Show
from .forms import SeatCreationForm

# Register models that don't need a custom admin view
admin.site.register(Genre)
admin.site.register(Auditorium)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'language')
    filter_horizontal = ('genres',)

@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ('name', 'movie')

@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('theater', 'auditorium', 'time', 'add_seats_link')
    list_filter = ('theater', 'auditorium')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/add-seats/',
                self.admin_site.admin_view(self.add_seats_view),
                name='movies_show_add_seats',
            ),
        ]
        return custom_urls + urls

    def add_seats_link(self, obj):
        return format_html(
            '<a class="button" href="/admin/movies/show/{}/add-seats/">Add Seats</a>',
            obj.pk
        )
    add_seats_link.short_description = 'Bulk Add Seats'

    def add_seats_view(self, request, object_id):
        show = self.get_object(request, object_id)
        if request.method == 'POST':
            form = SeatCreationForm(request.POST)
            if form.is_valid():
                try:
                    start_row, end_row = form.cleaned_data['rows'].upper().split('-')
                    seats_per_row = form.cleaned_data['seats_per_row']
                    
                    if len(start_row) != 1 or len(end_row) != 1 or ord(start_row) > ord(end_row):
                        raise ValueError("Invalid row range. Please use format like 'A-J'.")

                    seats_to_create = []
                    for row_ord in range(ord(start_row), ord(end_row) + 1):
                        row_letter = chr(row_ord)
                        for seat_num in range(1, seats_per_row + 1):
                            seat_number = f"{row_letter}{seat_num}"
                            seats_to_create.append(Seat(show=show, seat_number=seat_number))
                    
                    Seat.objects.bulk_create(seats_to_create)
                    self.message_user(request, f"Successfully created seats for show '{show}'.", messages.SUCCESS)
                    return redirect('/admin/movies/show/')
                
                except Exception as e:
                    self.message_user(request, f"Failed to create seats. Error: {e}", messages.ERROR)
        else:
            form = SeatCreationForm()

        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['form'] = form
        context['title'] = f"Add Seats for {show}"
        context['object_id'] = object_id
        
        return render(request, 'admin/movies/show/add_seats.html', context)

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('show', 'seat_number', 'is_booked', 'tier', 'price')
    list_filter = ('show__theater', 'is_booked', 'tier')
    actions = ['assign_platinum_tier', 'assign_gold_tier', 'assign_silver_tier']

    def assign_platinum_tier(self, request, queryset):
        updated_count = queryset.update(tier='PLATINUM', price=300.00)
        self.message_user(request, f"{updated_count} seats were successfully marked as Platinum.")
    assign_platinum_tier.short_description = "Assign Platinum Tier (Rs. 300)"

    def assign_gold_tier(self, request, queryset):
        updated_count = queryset.update(tier='GOLD', price=200.00)
        self.message_user(request, f"{updated_count} seats were successfully marked as Gold.")
    assign_gold_tier.short_description = "Assign Gold Tier (Rs. 200)"

    def assign_silver_tier(self, request, queryset):
        updated_count = queryset.update(tier='SILVER', price=150.00)
        self.message_user(request, f"{updated_count} seats were successfully marked as Silver.")
    assign_silver_tier.short_description = "Assign Silver Tier (Rs. 150)"

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'seat', 'movie', 'show', 'booked_at')