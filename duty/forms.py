from django import forms
from django.forms import formset_factory
from .models import DriverTrip

class DriverTripForm(forms.ModelForm):
    class Meta:
        model = DriverTrip
        fields = [
            'route_name', 'pick_up_time', 'drop_off_time',
            'shift_time', 'head_count', 'trip_type', 'date'
        ]
        widgets = {
            'route_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Route Name'}),
            'pick_up_time': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'HH:MM'}),
            'drop_off_time': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'HH:MM'}),
            'shift_time': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'HH:MM'}),
            'head_count': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Head Count'}),
            'trip_type': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

DriverTripFormSet = formset_factory(DriverTripForm, extra=1)