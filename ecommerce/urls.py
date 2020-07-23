from django.urls import path
from .views import *


urlpatterns = [
    path('category/<id>', CategoryView.as_view(), name='category'),
    path('brand/<id>', BrandView.as_view(), name='brand'),
    path('product/<id>', ProductView.as_view(), name='product'),
    path('cart', cart_action, name='cart'),
    path('cart/view', CartView.as_view(), name='cart_view'),
    path('checkout', CheckoutView.as_view(), name='checkout'),
    path('search', SearchView.as_view(), name='search')

]