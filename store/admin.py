from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

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

class CategoryAdmin2(DraggableMPTTAdmin):
    mptt_indent_field = "name"
    list_display = ('tree_actions', 'indented_title',
                    'related_products_count', 'related_products_cumulative_count')
    list_display_links = ('indented_title',)
    prepopulated_fields = {"slug": ("name",)}
    MPTT_ADMIN_LEVEL_INDENT = 20

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Add cumulative product count
        qs = Category.objects.add_related_count(
                qs,
                Product,
                'category',
                'products_cumulative_count',
                cumulative=True)

        # Add non cumulative product count
        qs = Category.objects.add_related_count(qs,
                 Product,
                 'category',
                 'products_count',
                 cumulative=False)
        return qs

    def related_products_count(self, instance):
        return instance.products_count
    related_products_count.short_description = 'Related products (for this specific category)'

    def related_products_cumulative_count(self, instance):
        return instance.products_cumulative_count
    related_products_cumulative_count.short_description = 'Related products (in tree)'

admin.site.register(Category, CategoryAdmin2)

class ProductAdmin(admin.ModelAdmin):

    list_display = ('id', 'name', 'category', 'description', 'price', 'membership_price')
    prepopulated_fields = {"slug": ("name",)}
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_per_page = 25

admin.site.register(Product, ProductAdmin)

class CartAdmin(admin.ModelAdmin):

    list_display = ('id', 'user', 'ordered')
    list_per_page = 25

admin.site.register(Cart, CartAdmin)

class OrderAdmin(admin.ModelAdmin):

    list_display = ('user', 'shipping_address', 'country', 'ordered')
    list_display_links = ('user',)
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