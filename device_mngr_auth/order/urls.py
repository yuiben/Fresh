from django.urls import path

from device_mngr_auth.order.views import (
    create_new_order,
    order_analysis,
)
order_urls = [
    path('create_new_order/', view=create_new_order, name='create_new_order'),
    path('order_analysis/', view=order_analysis, name='order_analysis'),
]
