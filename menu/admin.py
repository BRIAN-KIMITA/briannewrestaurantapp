from django.contrib import admin
from .models import MenuItem, Order, OrderItem

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'phone', 'ordered_at', 'total_price_display')
    search_fields = ('customer_name', 'phone', 'email')
    inlines = [OrderItemInline]
    readonly_fields = ('ordered_at',)

    def total_price_display(self, obj):
        return f"Ksh {obj.total_price():,.2f}"
    total_price_display.short_description = 'Total Price'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'item', 'quantity', 'subtotal_display')

    def subtotal_display(self, obj):
        return f"Ksh {obj.subtotal():,.2f}"
    subtotal_display.short_description = 'Subtotal'
