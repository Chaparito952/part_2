from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('order/create/', views.create_order, name='create_order'),
    path('order/<int:pk>/delete/', views.delete_order, name='delete_order'),
]
