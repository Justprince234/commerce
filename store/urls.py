from django.urls import path
from store import views
from .views import (
    CountryListView,
    CheckoutAddressListView,
    CheckoutAddressCreateView,
    CheckoutAddressUpdateView,
    CheckoutAddressDeleteView,
    OrderDetailView,
    OrderItemDeleteView,
    PaymentListView,
    PaymentView,
    StripeConfigView,
    OrderQuantityUpdateView,
    UserIDView,
    AddCouponView,
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
    path('update-quantity/',
        OrderQuantityUpdateView.as_view(), name='order-item-update-quantity'),
    path('stripe-config/', StripeConfigView.as_view(), name='stripe-config'),
    path('checkout/', PaymentView.as_view(), name='checkout'),
    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('membershipform/', views.MembershipFormList.as_view()),
    path('contactlist/', views.ContactList.as_view()),
    # path('add-to-cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('user-id/', UserIDView.as_view(), name='user-id'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    # path("cart/", views.CartItemAPIView.as_view()),
    # path("cart-item/<int:pk>/", views.CartItemView.as_view()),
    path("cart-item/",views.cartview.as_view()),
     path("cart-item/<int:id>",views.cartview.as_view())
]