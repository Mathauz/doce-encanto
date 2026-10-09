from django.contrib import admin

from .models import Order, OrderItem, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "active", "featured")
    list_filter = ("active", "featured")
    search_fields = ("name", "description")
    list_editable = ("price", "active", "featured")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "unit_price", "quantity", "subtotal")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "payment_method", "total", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("recipient_name", "user__username", "user__email")
    list_editable = ("status",)
    readonly_fields = ("user", "total", "created_at", "updated_at")
    inlines = [OrderItemInline]

