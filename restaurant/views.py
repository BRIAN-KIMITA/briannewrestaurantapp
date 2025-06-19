from django.shortcuts import render,redirect,get_object_or_404
from menu.models import MenuItem
from .forms import ReservationForm
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required


# Create your views here.
def index(request):
    menu_items = MenuItem.objects.all()
    return render(request, 'index.html', {'menu_items': menu_items})

def about(request):
    return render(request,'about.html')
@login_required
def book_table(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save()

            # Email to restaurant
            send_mail(
                subject='New Table Reservation',
                message=(
                    f'New reservation received:\n\n'
                    f'Name: {reservation.name}\n'
                    f'Date: {reservation.date}\n'
                    f'Time: {reservation.time}\n'
                    f'Guests: {reservation.guests}\n'
                    f'Email: {reservation.email}\n'
                    f'Phone: {reservation.phone}'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],  # your own email
                fail_silently=False,
            )

            # Confirmation email to customer
            send_mail(
                subject='Table Reservation Confirmation',
                message=(
                    f'Dear {reservation.name},\n\n'
                    f'Thank you for your reservation!\n'
                    f'Here are your reservation details:\n'
                    f'Date: {reservation.date}\n'
                    f'Time: {reservation.time}\n'
                    f'Guests: {reservation.guests}\n\n'
                    f'We look forward to serving you.\n'
                    f'-- BRIAN COOKIES RESTAURANT'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reservation.email],
                fail_silently=False,
            )

            messages.success(request, "Your reservation has been submitted! A confirmation email has been sent.")
            return redirect('book_table')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ReservationForm()
    return render(request, 'book.html', {'form': form})

def home(request):
    return render(request,'home.html')
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # or auto-login & redirect to 'menu'
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})
