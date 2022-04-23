from django.urls import path
from store import views
from .views import (
    CountryListView,
    OrderDetailView,
    OrderItemDeleteView,
    BraintreeConfigView,
    OrderQuantityUpdateView
)

app_name = 'store'

urlpatterns = [
    path('categories/', views.ListCategory.as_view(), name='categories'),
    path('categories/<int:pk>/', views.DetailCategory.as_view(), name='singlecategory'),

    path('products/', views.ListProduct.as_view(), name='products'),
    path('products/<int:pk>/', views.DetailProduct.as_view(), name='singleproduct'),

    path('carts/', views.CartView.as_view(), name='allcarts'),
    path('carts/<int:pk>/', views.DetailCart.as_view(), name='cartdetail'),

    path('products/search/', views.search),
    path('countries/', CountryListView.as_view(), name='country-list'),
    path('order-summary/', OrderDetailView.as_view(), name='order-summary'),
    path('order-items/<pk>/delete/',
        OrderItemDeleteView.as_view(), name='order-item-delete'),
    path('update-quantity/',
        OrderQuantityUpdateView.as_view(), name='order-item-update-quantity'),
    path('braintree-config/', BraintreeConfigView.as_view(), name='stripe-config'),
    path('membershipform/', views.MembershipFormList.as_view()),
    path('contactlist/', views.ContactList.as_view()),
    # path('cart-item/', CartView.as_view(), name='cart-item'),
    # path('carts/', views.ListCart.as_view(), name='carts'),
    path('checkout/', views.checkout, name='checkout')
]