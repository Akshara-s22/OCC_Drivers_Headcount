from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .forms import DriverTripFormSet, CustomUserCreationForm
from .models import DriverTrip, DriverImportLog, DutyCardTrip
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, timedelta
import pandas as pd
import logging
import xlsxwriter
from .decorators import user_in_driverimportlog_required

# Setup logger
logger = logging.getLogger(__name__)

@login_required
def home(request):
    # Fetch the staff name using the logged-in user's username (assumed to be their staff ID)
    staff_id = request.user.username
    staff_name = DriverImportLog.objects.filter(staff_id=staff_id).values_list('driver_name', flat=True).first()
    
    if not staff_name:
        staff_name = request.user.username  # Fallback to username if staff name is not found

    # Example of converting datetime to string
    driver_trips = DriverTrip.objects.filter(driver__staff_id=staff_id)
    driver_trip_data = []
    for trip in driver_trips:
        trip_data = {
            'route_name': trip.route_name,
            'pick_up_time': trip.pick_up_time.strftime('%H:%M:%S'),  # Convert time to string
            'drop_off_time': trip.drop_off_time.strftime('%H:%M:%S'),  # Convert time to string
            'shift_time': trip.shift_time.strftime('%H:%M:%S'),  # Convert time to string
            'head_count': trip.head_count,
            'trip_type': trip.trip_type,
            'date': trip.date.strftime('%Y-%m-%d')  # Convert date to string
        }
        driver_trip_data.append(trip_data)

    context = {
        'staff_name': staff_name,
        'driver_trips': driver_trip_data,
    }

    return render(request, 'duty/home.html', context)


@login_required
def enter_head_count(request):
    # Fetch the staff name using the logged-in user's username (assumed to be their staff ID)
    staff_id = request.user.username
    driver = DriverImportLog.objects.filter(staff_id=staff_id).first()
    staff_name = driver.driver_name if driver else request.user.username  # Fallback to username if staff name is not found

    if request.method == 'POST':
        trip_formset = DriverTripFormSet(request.POST, prefix='drivertrip_set')

        duty_card_no = request.POST.get('duty_card_no')
        duty_card = DutyCardTrip.objects.filter(duty_card_no=duty_card_no).first()

        if not duty_card_no:
            return render(request, 'duty/enter_head_count.html', {  
                'trip_formset': trip_formset,
                'staff_name': staff_name,
                'error_message': "Please fill in the Duty Card No.",
            })

        desired_date = datetime.today().date()  # Default to today
        if 'tomorrow' in request.POST:
            desired_date = datetime.today().date() + timedelta(days=1)
        elif 'day_after_tomorrow' in request.POST:
            desired_date = datetime.today().date() + timedelta(days=2)

        duplicate_entry = False

        try:
            if trip_formset.is_valid():
                for form in trip_formset:
                    if form.is_valid():
                        form.cleaned_data['date'] = desired_date
                        trip_date = form.cleaned_data.get('date')
                        existing_trip = DriverTrip.objects.filter(
                            duty_card=duty_card,
                            date=trip_date
                        ).exists()

                        if existing_trip:
                            duplicate_entry = True
                            form.add_error(None, f"Data for Duty Card No {duty_card_no} on {trip_date} already exists.")
                            break

                if duplicate_entry:
                    return render(request, 'duty/enter_head_count.html', {
                        'trip_formset': trip_formset,
                        'staff_name': staff_name,
                        'duty_card': duty_card,
                        'error_message': "Duplicate entry found. Please check your input.",
                    })
                else:
                    for form in trip_formset:
                        if form.is_valid():
                            trip = form.save(commit=False)
                            trip.date = desired_date  # Set the date to the desired date
                            trip.duty_card = duty_card
                            trip.driver = driver  # Set the driver ID from the logged-in user's staff ID
                            trip.save()

                    return redirect('success')  # Redirect to the success page after saving the data
            else:
                return render(request, 'duty/enter_head_count.html', {
                    'trip_formset': trip_formset,
                    'staff_name': staff_name,
                    'duty_card': duty_card,
                    'error_message': "Please correct the errors below.",
                })

        except Exception as e:
            logger.error(f"Error occurred while entering head count: {str(e)}")
            return render(request, 'duty/enter_head_count.html', {
                'trip_formset': trip_formset,
                'staff_name': staff_name,
                'error_message': f"An error occurred: {str(e)}",
                'duty_card': duty_card,
            })
    else:
        initial_data = [{'date': datetime.today().date()}]
        trip_formset = DriverTripFormSet(prefix='drivertrip_set', initial=initial_data)

    return render(request, 'duty/enter_head_count.html', {
        'trip_formset': trip_formset,
        'staff_name': staff_name,
    })

@login_required
def success(request):
    return render(request, 'duty/success.html')

@login_required
@user_in_driverimportlog_required  # Apply the custom decorator here
def report_view(request):
    # Retrieve filters from the request
    date_filter = request.GET.get('date')
    route_filter = request.GET.get('route')
    shift_time_filter = request.GET.get('shift_time')
    trip_type_filter = request.GET.get('trip_type')

    # Start with all DriverTrip objects
    driver_trips = DriverTrip.objects.all()

    # Apply date filter if provided
    if date_filter:
        try:
            date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
            driver_trips = driver_trips.filter(date=date_obj)
        except ValueError:
            driver_trips = driver_trips.none()

    # Apply route filter if provided (case-insensitive)
    if route_filter:
        driver_trips = driver_trips.filter(route_name__icontains=route_filter)

    # Apply shift time filter if provided
    if shift_time_filter:
        try:
            parsed_shift_time = datetime.strptime(shift_time_filter, '%H:%M').time()
            driver_trips = driver_trips.filter(shift_time=parsed_shift_time)
        except ValueError:
            driver_trips = driver_trips.none()

    # Apply trip type filter if provided (case-insensitive)
    if trip_type_filter:
        driver_trips = driver_trips.filter(trip_type__iexact=trip_type_filter)

    # Get distinct routes and shift times
    routes = driver_trips.values_list('route_name', flat=True).distinct()
    shift_times = driver_trips.values_list('shift_time', flat=True).distinct()

    # Prepare the context
    context = {
        'driver_trips': driver_trips,
        'routes': routes,
        'shift_times': shift_times,
    }

    # Render the appropriate template based on the request type
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'duty/report_data.html', context)
    else:
        return render(request, 'duty/report_data.html', context)

def download_report(request):
    date_filter = request.GET.get('date')
    route_filter = request.GET.get('route')
    shift_time_filter = request.GET.get('shift_time')
    trip_type_filter = request.GET.get('trip_type')

    driver_trips = DriverTrip.objects.all()

    if date_filter:
        driver_trips = driver_trips.filter(date=date_filter)
    if route_filter:
        driver_trips = driver_trips.filter(route_name=route_filter)
    if shift_time_filter:
        driver_trips = driver_trips.filter(shift_time=shift_time_filter)
    if trip_type_filter:
        driver_trips = driver_trips.filter(trip_type=trip_type_filter)

    data = []
    for trip in driver_trips:
        data.append({
            'Staff ID': trip.driver.staff_id,
            'Driver Name': trip.driver.driver_name,
            'Duty Card No': trip.duty_card.duty_card_no,
            'Route Name': trip.route_name,
            'Pick Up Time': trip.pick_up_time.strftime("%H:%M"),
            'Drop Off Time': trip.drop_off_time.strftime("%H:%M"),
            'Shift Time': trip.shift_time.strftime("%H:%M"),
            'Trip Type': trip.trip_type,
            'Date': trip.date.strftime("%Y-%m-%d"),
            'Head Count': trip.head_count,
        })

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=driver_trip_report_{date_filter}.xlsx'

    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Driver Trips', index=False)

    return response 

def staff_id_autocomplete(request):
    if 'term' in request.GET:
        term = request.GET.get('term')
        qs = DriverImportLog.objects.filter(staff_id__icontains=term)
        staff_ids = list(qs.values_list('staff_id', flat=True))
        return JsonResponse(staff_ids, safe=False)
    return JsonResponse([], safe=False)

def get_driver_name(request):
    staff_id = request.GET.get('staff_id', None)
    if staff_id:
        driver_log = DriverImportLog.objects.filter(staff_id=staff_id).first()
        if driver_log:
            return JsonResponse({'driver_name': driver_log.driver_name})
        else:
            return JsonResponse({'driver_name': ''})
    return JsonResponse({'driver_name': ''})

def duty_card_no_autocomplete(request):
    if 'term' in request.GET:
        term = request.GET.get('term')
        qs = DutyCardTrip.objects.filter(duty_card_no__icontains=term).values_list('duty_card_no', flat=True)
        duty_card_nos = list(set(qs))
        return JsonResponse(duty_card_nos, safe=False)

def get_duty_card_details(request):
    if 'duty_card_no' in request.GET:
        duty_card_no = request.GET.get('duty_card_no')
        trips = DutyCardTrip.objects.filter(duty_card_no=duty_card_no)
        trip_details = list(trips.values('route_name', 'pick_up_time', 'drop_off_time', 'shift_time', 'trip_type'))

        for trip in trip_details:
            trip['pick_up_time'] = trip['pick_up_time'].strftime("%H:%M")
            trip['drop_off_time'] = trip['drop_off_time'].strftime("%H:%M")
            trip['shift_time'] = trip['shift_time'].strftime("%H:%M")
            trip['trip_type'] = trip['trip_type']
            trip['date'] = datetime.today().strftime("%Y-%m-%d")

        return JsonResponse({'trips': trip_details}, safe=False)
    
    return JsonResponse({'trips': []}, safe=False)

@login_required
def route_autocomplete(request):
    if 'term' in request.GET:
        qs = DriverTrip.objects.filter(route_name__istartswith=request.GET.get('term'))
        routes = list(qs.values_list('route_name', flat=True).distinct())
        return JsonResponse(routes, safe=False)
    return JsonResponse([], safe=False)

@login_required
def shift_time_autocomplete(request):
    if 'term' in request.GET:
        qs = DriverTrip.objects.filter(shift_time__startswith(request.GET.get('term')))
        shift_times = list(qs.values_list('shift_time', flat=True).distinct())
        shift_times = [time.strftime("%H:%M") for time in shift_times]
        return JsonResponse(shift_times, safe=False)
    return JsonResponse([], safe=False)

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            logger.debug("Form is valid, saving user.")
            user = form.save()
            messages.success(request, 'Your account has been created successfully! Please log in.')
            return redirect('login')  # Redirect to the login page
        else:
            logger.warning("Form is not valid.")
    else:
        logger.debug("GET request, rendering signup form.")
        form = CustomUserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')
