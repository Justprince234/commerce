from django.urls import path
from store import views
from .views import (
    remove_from_cart,
    reduce_quantity_item,
    add_to_cart,
    ordersummary_api_view,
    orderitem_api_view,
    CheckoutAddress_api_view,
    checkout_api_view,
)

app_name = 'store'

urlpatterns = [
    path('product/<slug:category_slug>/<slug:product_slug>/', views.ProductDetail.as_view()),
    path('product/<slug:category_slug>/', views.CategoryDetail.as_view()),
    path('products/', views.ListProductApi.as_view()),
    path('products/search/', views.search),
    # path('order-summary/', ordersummary_api_view,name='order-summary'),
    # path('add-to-cart/<str:slug>/', add_to_cart, name='add-to-cart'),
    # path('remove-from-cart/<str:slug>/', remove_from_cart, name='remove-from-cart'),
    # path('reduce-quantity-item/<str:slug>/', reduce_quantity_item, name='reduce-quantity-item'),
    # path('ordered-item/<str:slug>/', orderitem_api_view, name='ordered-item'),
    # path('checkout/<str:slug>/',checkout_api_view, name='checkout'),
    # path('checkout-address/<str:slug>/', CheckoutAddress_api_view, name='checkout-address'),
]