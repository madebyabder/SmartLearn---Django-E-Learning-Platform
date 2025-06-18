from django.urls import path
from . import views

app_name = 'admin_app'
urlpatterns = [

    
    path('users/', views.list_users, name='list_users'),
    path('add_users/', views.add_user, name='add_users'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('update_user/<int:user_id>/', views.update_user, name='update_user'),
    
    
     path('supervision/', views.supervision_dashboard, name='supervision_dashboard'),
    
   
   path('calendar/', views.calendar_events, name='calendar_events'),
    path('event/<int:event_id>/toggle-status/', views.toggle_event_status, name='toggle_event_status'),
     path('event/<int:event_id>/ajax-toggle-status/', views.ajax_toggle_event_status, name='ajax_toggle_event_status'),

     
     path('add-event/', views.add_event, name='add_event'),
     path('event/<int:event_id>/details/', views.event_details, name='event_details'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete_event'),


    path('add-videoconference/', views.add_videoconference, name='add_videoconference'),
    path('cancel-videoconference/<int:event_id>/', views.cancel_videoconference, name='cancel_videoconference'),
    path('modify-videoconference/<int:event_id>/', views.modify_videoconference, name='modify_videoconference'), 
    path('schedule-videoconference/', views.schedule_videoconference, name='schedule_videoconference'),

]
