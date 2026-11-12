from django.urls import path
from . import views
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Homepage
    path('', views.index, name='index'),

    path('logout/', views.logout_view, name='logout'),
    path('admin/', lambda request: redirect('login_admin')), 
    
    # Login URLs
    
    path('login/user/', views.login_user, name='login_user'),
    path('login/owner/', views.login_owner, name='login_owner'),
    path('login/admin/', views.login_admin, name='login_admin'),


    path('owner/approve/<int:owner_id>/', views.approve_owner, name='approve_owner'),
    path('owner/reject/<int:owner_id>/', views.reject_owner, name='reject_owner'),
    path('approve-turf/<int:turf_id>/', views.approve_turf, name='approve_turf'),
    path('reject-turf/<int:turf_id>/', views.reject_turf, name='reject_turf'),
    path('turf/<str:status>/<int:turf_id>/', views.approve_turf, name='approve_turf'),


    # Registration URLs
    path('register/user/', views.user_register, name='register_user'),
    path('register/owner/', views.owner_register, name='register_owner'),

    # Dashboard URLs
    path('dashboard/user/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/owner/', views.owner_dashboard, name='owner_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),

    path('home/', views.home, name='home'),
    path('search/', views.search_turf, name='search_turf'),

    path('about/', views.about, name='about'),
    
    
    path('contact/', views.contact, name='contact'),


    
   path('login/', views.login_user, name='login'),
   path('owner/logout/', views.logout_owner, name='logout_owner'),
   path('dashboard/admin/logout/', views.logout_admin, name='logout_admin'),

   #path('book-now/', views.book_now, name='book_now'),
   path('booking-history/', views.booking_history, name='booking_history'),
    #path('booking-refund/<int:booking_id>/', views.request_refund, name='request_refund'),
    path('approve-refund/<int:booking_id>/', views.approve_refund, name='approve_refund'),

    
   path('request-refund/<int:booking_id>/', views.request_refund, name='request_refund'),
     
   path('book-now/<int:turf_id>/', views.book_now, name='book_now'),
   path('payment/<int:booking_id>/', views.payment, name='payment'),
   path('payment/confirm/', views.confirm_payment, name='confirm_payment'),
   path('booking-confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),


   path('job/', views.job, name='job'),
   path('jobs/', views.job_list, name='job'),
   path('apply-job/', views.apply_job, name='apply_job'),
 

    path('add-turf/', views.add_turf, name='add_turf'),
    path('post-job/', views.post_job, name='post_job'),

    path('manage-turf/', views.manage_turf, name='manage_turf'),
    path('edit-turf/<int:turf_id>/', views.edit_turf, name='edit_turf'),
    path('add-slot/<int:turf_id>/', views.add_slot, name='add_slot'),
    path('delete-turf/<int:turf_id>/', views.delete_turf, name='delete_turf'),

    
   path('review/', views.review, name='review'),
   

   path('owner/reviews/', views.owner_reviews, name='owner_reviews'),

   path('owner/<int:owner_id>/booking-history/', views.owner_booking_history, name='owner_booking_history'),   

]


