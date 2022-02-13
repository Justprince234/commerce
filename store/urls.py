from django.urls import path
from store import views
from .views import (
    CountryListView,
    OrderDetailView,
    OrderItemDeleteView,
    PaymentListView,
    StripeConfigView,
    OrderQuantityUpdateView,
    CartView
)

app_name = 'store'

urlpatterns = [
    path('product/<slug:category_slug>/<slug:product_slug>/', views.ProductDetail.as_view()),
    path('product/<slug:category_slug>/', views.CategoryDetail.as_view()),
    path('products/', views.ListProductApi.as_view()),
    path('products/search/', views.search),
    path('countries/', CountryListView.as_view(), name='country-list'),
    path('order-summary/', OrderDetailView.as_view(), name='order-summary'),
    path('order-items/<pk>/delete/',
        OrderItemDeleteView.as_view(), name='order-item-delete'),
    path('update-quantity/',
        OrderQuantityUpdateView.as_view(), name='order-item-update-quantity'),
    path('stripe-config/', StripeConfigView.as_view(), name='stripe-config'),
    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('membershipform/', views.MembershipFormList.as_view()),
    path('contactlist/', views.ContactList.as_view()),
    path('cart-item/', CartView.as_view(), name='cart-item'),
    path('checkout/', views.checkout, name='checkout')
]