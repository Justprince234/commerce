from django.urls import path
from store import views
from .views import (
    remove_from_cart,
    reduce_quantity_item,
    add_to_cart,
    CountryListView,
    CheckoutAddressListView,
    CheckoutAddressCreateView,
    CheckoutAddressUpdateView,
    CheckoutAddressDeleteView,
    OrderDetailView,
    OrderItemDeleteView,
    PaymentListView,
)

app_name = 'store'

urlpatterns = [
    path('product/<slug:category_slug>/<slug:product_slug>/', views.ProductDetail.as_view()),
    path('product/<slug:category_slug>/', views.CategoryDetail.as_view()),
    path('products/', views.ListProductApi.as_view()),
    path('products/search/', views.search),
    path('countries/', CountryListView.as_view(), name='country-list'),
    path('addresses/', CheckoutAddressListView.as_view(), name='address-list'),
    path('addresses/create/', CheckoutAddressCreateView.as_view(), name='address-create'),
    path('addresses/<pk>/update/',
        CheckoutAddressUpdateView.as_view(), name='address-update'),
    path('addresses/<pk>/delete/',
        CheckoutAddressDeleteView.as_view(), name='address-delete'),
    path('order-summary/', OrderDetailView.as_view(), name='order-summary'),
    path('order-items/<pk>/delete/',
        OrderItemDeleteView.as_view(), name='order-item-delete'),
    # path('order-item/update-quantity/',
    #     OrderQuantityUpdateView.as_view(), name='order-item-update-quantity'),
    # path('orders/', views.OrdersList.as_view()),
    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('membershipform/', views.MembershipFormList.as_view()),
    path('contactlist/', views.ContactList.as_view()),
    path('add-to-cart/<slug:slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug:slug>/', remove_from_cart, name='remove-from-cart'),
    path('reduce-quantity-item/<slug:slug>/', reduce_quantity_item, name='reduce-quantity-item'),
]