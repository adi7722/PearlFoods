
from django.contrib import admin
from pearlfoods.models import *

class ContactAdmin(admin.ModelAdmin):
    list_display = ('contact_id', 'name', 'email', 'date')
    search_fields = ('name', 'email')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'name',
        'status',
        'payment_status',
        'phone',
        'delivery_address',
        'order_date',
        'order_price',
        'order_items_details'
    )
    inlines = [OrderItemInline]

    def user(self, obj):
        return obj.user.username
    user.admin_order_field = 'user'
    user.short_description = 'User'

    def order_date(self, obj):
        return obj.date
    order_date.admin_order_field = 'date'
    order_date.short_description = 'Order Date'

    def order_price(self, obj):
        return obj.price
    order_price.admin_order_field = 'price'
    order_price.short_description = 'Total Price'

    def order_items_details(self, obj):
        items = obj.order_items.all()
        details = []
        for item in items:
            # Split the flavor name to remove the unit (e.g., "Himaliyan Salajeet - Packet" -> "Himaliyan Salajeet")
            flavor_name = item.flavor.split(' - ')[0]
            
            try:
                # Now look up the product using the cleaned name (without the unit)
                flavor_obj = Product.objects.get(name__iexact=flavor_name)
                price = flavor_obj.price_per_unit * item.quantity
                details.append(f"{item.flavor} (Qty: {item.quantity}, Price: {price})")
            except Product.DoesNotExist:
                # Handle case where product is not found
                details.append(f"{item.flavor} (Qty: {item.quantity}, Price: Not Available)")
        return ", ".join(details)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_unit')
    search_fields = ('name',)

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    readonly_fields = ('flavor', 'quantity')

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'total_price')
    inlines = [CartItemInline]

    def total_price(self, obj):
        return obj.total_price()
    total_price.admin_order_field = 'total_price'
    total_price.short_description = 'Total Price'

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating','status' ,'created_at')
    search_fields = ('name', 'feedback', 'status')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address')
    search_fields = ('user__username', 'phone_number')

admin.site.register(Contact, ContactAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

