from django.urls import path
from Mboa_ecom.views import index, detail_view, commander_view, confirmation_view

urlpatterns = [
    path('', index, name='home'),
    path('<int:my_id>', detail_view, name='product_detail'),
    path('commander', commander_view, name='commander'),
    path('confirmation', confirmation_view, name= 'confirmation'),
]
