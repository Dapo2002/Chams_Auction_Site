from django.urls import path
from . import views

urlpatterns = [
    path('', views.auction_list, name='auction_list'),
    path('asset/<int:pk>/', views.auction_detail, name='auction_detail'),
    path('register/', views.register, name='register')
]
