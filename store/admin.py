from django.contrib import admin

from .models import (
    Category,
    Product, 
    OrderProduct, 
    Order,
    CheckoutAddress,
    Payment,
    Coupon,
    MembershipForm,
    Contact,
    UserProfile,
    Cart
)

admin.site.site_header = 'Direshop777'
admin.site.site_title = 'Direshop777'
admin.site.index_title = 'Direshop777 Admin'

class CategoryAdmin(admin.ModelAdmin):

    list_display = ('id', 'name',)
    prepopulated_fields = {"slug": ("name",)}
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_per_page = 25

admin.site.register(Category, CategoryAdmin)

class ProductAdmin(admin.ModelAdmin):

    list_display = ('id', 'name', 'category', 'description', 'price', 'membership_price')
    prepopulated_fields = {"slug": ("name",)}
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_per_page = 25

admin.site.register(Product, ProductAdmin)

class OrderProductAdmin(admin.ModelAdmin):

    list_display = ('id', 'product', 'quantity', 'ordered')
    list_display_links = ('id', )
    search_fields = ('product',)
    list_per_page = 25

admin.site.register(OrderProduct, OrderProductAdmin)

class OrderAdmin(admin.ModelAdmin):

    list_display = ('id', 'first_name', 'last_name', 'phone', 'email', 'ordered_date', 'ordered', 'checkout_address', 'payment')
    list_display_links = ('id', 'first_name')
    search_fields = ('first_name',)
    list_per_page = 25

admin.site.register(Order, OrderAdmin)

class CheckoutAddressAdmin(admin.ModelAdmin):

    list_display = ('id', 'apartment_number', 'street_address', 'state', 'country', 'zip')
    list_display_links = ('id', 'street_address')
    search_fields = ('street_address',)
    list_per_page = 25

admin.site.register(CheckoutAddress, CheckoutAddressAdmin)

class PaymentAdmin(admin.ModelAdmin):

    list_display = ('id', 'stripe_charge_id', 'amount')
    list_display_links = ('id', 'stripe_charge_id')
    search_fields = ('stripe_charge_id',)
    list_per_page = 25

admin.site.register(Payment, PaymentAdmin)

class MembershipFormAdmin(admin.ModelAdmin):
    
    list_display = ('id', 'email', 'first_name', 'last_name', 'mobile_number')
    list_display_links = ('id', 'email')
    search_fields = ('email',)
    list_per_page = 25

admin.site.register(MembershipForm, MembershipFormAdmin)

class ContactAdmin(admin.ModelAdmin):
    
    list_display = ('id', 'name', 'email', 'query')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_per_page = 25

admin.site.register(Contact, ContactAdmin)

admin.site.register(UserProfile)
admin.site.register(Coupon)
admin.site.register(Cart)