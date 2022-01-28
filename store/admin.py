from django.contrib import admin

from .models import (
    Category,
    Product, 
    Cart, 
    Order,
    Payment,
    MembershipForm,
    Contact,
    UserProfile,
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

class CartAdmin(admin.ModelAdmin):

    list_display = ('id','user', 'ordered')
    list_per_page = 25

admin.site.register(Cart, CartAdmin)

class OrderAdmin(admin.ModelAdmin):

    list_display = ('id','user', 'shipping_address', 'country', 'ordered')
    list_display_links = ('id', 'user')
    search_fields = ('user',)
    list_per_page = 25

admin.site.register(Order, OrderAdmin)

class PaymentAdmin(admin.ModelAdmin):

    list_display = ('id', 'user', 'stripe_charge_id', 'amount')
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