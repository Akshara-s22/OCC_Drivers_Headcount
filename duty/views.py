from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .forms import DriverTripFormSet
from .models import DriverTrip, DriverImportLog, DutyCardTrip
import pandas as pd

def home(request):
    return render(request, 'duty/home.html')

def enter_head_count(request):
    if request.method == 'POST':
        trip_formset = DriverTripFormSet(request.POST, prefix='drivertrip_set')

        staff_id = request.POST.get('staff_id')
        driver = DriverImportLog.objects.filter(staff_id=staff_id).first()
        duty_card_no = request.POST.get('duty_card_no')
        duty_card = DutyCardTrip.objects.filter(duty_card_no=duty_card_no).first()

        duplicate_entry = False

        try:
            if trip_formset.is_valid():
                for form in trip_formset:
                    if form.is_valid():
                        trip_date = form.cleaned_data.get('date')
                        existing_trip = DriverTrip.objects.filter(
                            driver=driver,
                            date=trip_date
                        ).exists()

                        if existing_trip:
                            duplicate_entry = True
                            form.add_error(None, f"Data for Staff ID {staff_id} on {trip_date} already exists.")
                            break

                if duplicate_entry:
                    return render(request, 'duty/enter_head_count.html', {
                        'trip_formset': trip_formset,
                        'staff_id': staff_id,
                        'driver': driver,
                        'duty_card': duty_card,
                    })
                else:
                    for form in trip_formset:
                        if form.is_valid():
                            trip = form.save(commit=False)
                            trip.driver = driver
                            trip.duty_card = duty_card
                            trip.save()

                    return redirect('success')
            else:
                return render(request, 'duty/enter_head_count.html', {
                    'trip_formset': trip_formset,
                    'staff_id': staff_id,
                    'driver': driver,
                    'duty_card': duty_card,
                })

        except Exception as e:
            return render(request, 'duty/enter_head_count.html', {
                'trip_formset': trip_formset,
                'error_message': f"An error occurred: {str(e)}",
                'staff_id': staff_id,
                'driver': driver,
                'duty_card': duty_card,
            })
    else:
        trip_formset = DriverTripFormSet(prefix='drivertrip_set')

    return render(request, 'duty/enter_head_count.html', {
        'trip_formset': trip_formset,
    })

def success(request):
    return render(request, 'duty/success.html')

def report_view(request):
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
        try:
            # Attempt to parse the shift time filter to HH:MM format
            parsed_shift_time = datetime.strptime(shift_time_filter, '%I %p').time()
            driver_trips = driver_trips.filter(shift_time=parsed_shift_time)
        except ValueError:
            # If parsing fails, handle the error (you might want to log this or handle it differently)
            driver_trips = driver_trips.none()
    if trip_type_filter:
        driver_trips = driver_trips.filter(trip_type=trip_type_filter)

    routes = DriverTrip.objects.values_list('route_name', flat=True).distinct()
    shift_times = DriverTrip.objects.values_list('shift_time', flat=True).distinct()

    context = {
        'driver_trips': driver_trips,
        'routes': routes,
        'shift_times': shift_times,
    }

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

        return JsonResponse({'trips': trip_details}, safe=False)
    
    return JsonResponse({'trips': []}, safe=False)
