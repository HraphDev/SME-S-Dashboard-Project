from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from inventory import views as inventory_views
from users import views as users_views
from django.conf.urls.static import static 
from django.conf import settings  
urlpatterns = [
    path('', lambda request: redirect('login/', permanent=True)),
    path('admin/', admin.site.urls),
    path('login/', users_views.login_view, name='login'),
    path('logout/', users_views.logout_view, name='logout'),
    path('dashboard/', users_views.dashboard_view, name='dashboard'),
    path('password_reset/', users_views.password_reset_view, name='password_reset'),
    path('invite-user/', users_views.invite_user_view, name='invite_user'),
    path('accept-invitation/<uuid:token>/', users_views.accept_invitation_view, name='accept_invitation'),
    path('profile/settings/', users_views.profile_settings_view, name='profile_settings'),
    path('set-password/<uuid:token>/', users_views.set_password_view, name='set_password'),
    path('messages/', users_views.inbox, name='inbox'),
    path('password_reset/', users_views.password_reset_view, name='password_reset'),
    path('password_reset/done/', users_views.PasswordResetDoneView.as_view(
        template_name='dashboard/users/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', users_views.PasswordResetConfirmView.as_view(
        template_name='dashboard/users/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', users_views.PasswordResetCompleteView.as_view(
        template_name='dashboard/users/password_reset_complete.html'
    ), name='password_reset_complete'),

    
    # Users
    path('users/', users_views.user_list, name='user_list'),
    path('users/<int:pk>/edit/', users_views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', users_views.user_delete, name='user_delete'),

     # Categories
    path('categories/', inventory_views.category_list, name='category_list'),
    path('categories/add/', inventory_views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', inventory_views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', inventory_views.category_delete, name='category_delete'),
    path('categories/<int:pk>/', inventory_views.category_detail, name='category_detail'),
    # Products
    path('products/', inventory_views.product_list, name='product_list'),
    path('products/add/', inventory_views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', inventory_views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', inventory_views.product_delete, name='product_delete'),
    path('products/<int:product_id>/movements/', inventory_views.product_movement_history, name='product_movement_history'),
    path('products/<int:pk>/', inventory_views.product_detail, name='product_detail'),

    #mvmnt
    path('movements/', inventory_views.movement_list, name='movement_list'),
    path('products/add/', inventory_views.product_create, name='product_create'),
   
    path('movements/add/', inventory_views.movement_create, name='movement_create'),
    path('movements/<int:pk>/edit/', inventory_views.movement_update, name='movement_update'),
    path('movements/<int:pk>/delete/', inventory_views.movement_delete, name='movement_delete'),

    path('export/pdf/',  inventory_views.export_products_pdf, name='export_products_pdf'),
    path('export/csv/', inventory_views.export_products_csv, name='export_products_csv'),
 
    path('alerts/', inventory_views.stock_alerts, name='stock_alerts'),
    path('import/', inventory_views.bulk_import, name='import_csv'),
    path('suppliers/', inventory_views.supplier_list, name='supplier_list'),
    path('suppliers/add/', inventory_views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/', inventory_views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:pk>/edit/', inventory_views.supplier_update, name='supplier_update'),
    path('suppliers/<int:pk>/delete/', inventory_views.supplier_delete, name='supplier_delete'),

    # Messages
    path('reports/', inventory_views.report_list, name='report_list'),
    path('products/delete_all/', inventory_views.delete_all_products, name='delete_all_products'),
    path('categories/delete_all/', inventory_views.delete_all_categories, name='delete_all_categories'),
    path('movements/delete_all/', inventory_views.delete_all_movements, name='delete_all_movements'),
    path('suppliers/delete_all/', inventory_views.delete_all_suppliers, name='delete_all_suppliers'),
    path('reports/export_pdf/', inventory_views.export_reports_pdf, name='export_reports_pdf'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
