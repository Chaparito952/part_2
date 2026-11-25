from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('order/create/', views.create_order, name='create_order'),
    path('order/<int:pk>/delete/', views.delete_order, name='delete_order'),

    # Разделы администратора
    path('manage/', views.admin_dashboard, name='admin_dashboard'),
    path('manage/order/<int:pk>/in-progress/', views.set_order_in_progress, name='set_order_in_progress'),
    path('manage/order/<int:pk>/done/', views.set_order_done, name='set_order_done'),
    path('manage/category/add/', views.add_category, name='add_category'),
    path('manage/category/<int:pk>/delete/', views.delete_category, name='delete_category'),
]
