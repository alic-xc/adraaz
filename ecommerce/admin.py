from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ShippingLocation)
admin.site.register(Contact)
admin.site.register(ShippingInfo)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = ['token']
    list_display = ('order_date', 'token', 'status', 'payment_method', 'shipping')

    fields = ('token', 'status', 'payment_method', 'user_shipping', 'shipping', 'display_cart', 'user_details')
    readonly_fields = ['display_cart', 'token', 'payment_method', 'shipping', 'user_shipping', 'user_details']