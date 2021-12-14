from django.urls import path
from store import views
from .views import (
    remove_from_cart,
    reduce_quantity_item,
    add_to_cart,
    CheckoutAddress_api_view,
)

app_name = 'store'

urlpatterns = [
    path('product/<slug:category_slug>/<slug:product_slug>/', views.ProductDetail.as_view()),
    path('product/<slug:category_slug>/', views.CategoryDetail.as_view()),
    path('products/', views.ListProductApi.as_view()),
    path('products/search/', views.search),
    path('orders/', views.OrdersList.as_view()),
    path('membershipform/', views.MembershipFormList.as_view()),
    path('contactlist/', views.ContactList.as_view()),
    path('add-to-cart/<slug:slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug:slug>/', remove_from_cart, name='remove-from-cart'),
    path('reduce-quantity-item/<slug:slug>/', reduce_quantity_item, name='reduce-quantity-item'),
    # path('checkout/<str:slug>/',checkout_api_view, name='checkout'),
    # path('checkout-address/<str:slug>/', CheckoutAddress_api_view, name='checkout-address'),
]