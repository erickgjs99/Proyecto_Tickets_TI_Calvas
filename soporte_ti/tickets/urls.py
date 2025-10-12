from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # URLs de autenticación
    path('login/', auth_views.LoginView.as_view(template_name='tickets/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='tickets/logged_out.html'), name='logout'),
    
    # URLs de tickets
    path('', views.user_dashboard, name='user_dashboard'),
    path('create/', views.create_ticket, name='create_ticket'),
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('ticket/<int:ticket_id>/pdf/', views.generate_ticket_pdf, name='generate_ticket_pdf'),
    
    # URLs de administración de tickets
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/ticket/<int:ticket_id>/update/', views.update_ticket, name='update_ticket'),
    path('admin/ticket/<int:ticket_id>/delete/', views.delete_ticket, name='delete_ticket'),
    
    # URLs de gestión de usuarios
    path('admin/users/', views.user_list, name='user_list'),
    path('admin/users/create/', views.user_create, name='user_create'),
    path('admin/users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('admin/users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
]