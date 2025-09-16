from django import forms

class SeatCreationForm(forms.Form):
    rows = forms.CharField(
        label="Row Letters",
        help_text="Enter a range of row letters, e.g., 'A-J'.",
        max_length=10
    )
    seats_per_row = forms.IntegerField(
        label="Seats Per Row",
        help_text="Enter the number of seats in each row, e.g., 14.",
        min_value=1
    )