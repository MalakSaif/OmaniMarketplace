from django.contrib import admin
from .models import Brand, Product, Order, OrderItem, Feedback

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'user']
    search_fields = ['name', 'user__username']

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Feedback)
