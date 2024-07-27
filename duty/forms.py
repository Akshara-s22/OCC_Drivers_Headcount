from django import forms
from .models import Driver, Trip
from django.forms import inlineformset_factory

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['driver_name', 'staff_id', 'duty_card_no']
        labels = {
            'driver_name': 'Driver Name',
            'staff_id': 'Staff ID',
            'duty_card_no': 'Duty Card No',
        }
        widgets = {
            'driver_name': forms.TextInput(attrs={'class': 'form-control'}),
            'staff_id': forms.TextInput(attrs={'class': 'form-control'}),
            'duty_card_no': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['route_name', 'pick_up_time', 'drop_off_time', 'shift_time', 'head_count']
        labels = {
            'route_name': 'Route Name',
            'pick_up_time': 'Pick Up Time',
            'drop_off_time': 'Drop Off Time',
            'shift_time': 'Shift Time',
            'head_count': 'Head Count',
        }
        widgets = {
            'route_name': forms.TextInput(attrs={'class': 'form-control'}),
            'pick_up_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'drop_off_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'shift_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'head_count': forms.NumberInput(attrs={'class': 'form-control'}),
        }

TripFormSet = inlineformset_factory(Driver, Trip, form=TripForm, extra=1)
