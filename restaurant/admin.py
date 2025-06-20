from django.contrib import admin
from .models import Reservation
# Register your models here.
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'guests', 'date', 'time', 'created_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('date', 'guests')