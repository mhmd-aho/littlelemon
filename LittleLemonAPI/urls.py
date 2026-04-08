from django.urls import path
from . import views
urlpatterns = [
    path('menu/', views.MenuItemsView.as_view()),
    path('menu/<int:pk>/', views.SingleMenuItemView.as_view()),
    path('groups/manager/users', views.manager),
    path('groups/delivery/users', views.delivery),
    path('cart/menu-items/', views.CartView.as_view()),
    path('orders/', views.OrderView.as_view()),
    path('orders/<int:pk>/', views.OrderDetailView.as_view()),
    
]