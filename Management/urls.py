from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/cat/new/', views.create_category, name='create_category'),
    path('events/new/', views.create_event, name='create_event'),
    path('events/edit/<int:event_id>/', views.edit_event, name='event_edit'),
    path('events/media/<int:event_id>/',views.media_list,name='media_list'),
    path('events/media/new/<int:event_id>/', views.upload_media, name='upload_media'),
    path('events/metrics/<int:event_id>/',views.event_metrics,name='metric_list'),
    path('events/announcements/<int:event_id>/',views.announcement_list,name='announcement_list'),
    path('events/announcements/new/<int:event_id>/', views.create_announcement, name='create_announcement'),
    path('register/<int:event_id>/', views.register_for_event, name='register_for_event'),
    path('events/<int:event_id>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/event/<int:event_id>/', views.admin_event_detail, name='admin_event_detail'),
    path('contact/', views.contact_us, name='contact'),
]
