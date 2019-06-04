from django.urls import path

from . import views
from . import raspi_config_views

app_name='reservation'
urlpatterns = [
    path('', views.index, name='index'),

    path('calendar/<int:pk>/', views.CalendarCar.as_view(), name='calendar_car'),
    path('calendar/<int:pk>/config/', views.CarConfig.as_view(), name='calendar_car_config'),

    path('user_settings/', views.UserSettings.as_view(), name='user_settings'),

    path('reservation/<int:pk>/', views.ReservationDetail.as_view(), name='reservation'),
    path('reservation/<int:pk>/delete/', views.ReservationDelete.as_view(), name='reservation_delete'),
    path('car/<int:car_id>/reservation/add/', views.ReservationAdd.as_view(), name='reservation_add'),

    path('charging_reservation/<int:pk>/', views.ChargingReservationDetail.as_view(),
         name='charging_reservation'),
    path('charging_reservation/<int:pk>/delete/', views.ChargingReservationDelete.as_view(),
         name='charging_reservation_delete'),
    path('car/<int:car_id>/charging_reservation/add/', views.ChargingReservationAdd.as_view(),
         name='charging_reservation_add'),

    path('api/car/<int:pk>/reservations/', views.APIReservationsList.as_view(), name='api_car_reservations'),
    path('api/car/<int:pk>/charging_reservations/', views.APIChargingReservationsList.as_view(),
         name='api_car_charging_reservations'),
    path('api/car/<int:pk>/distance_left/', views.DistanceLeft.as_view(), name='api_car_distance_left'),


    path('raspi-config/', raspi_config_views.RaspiConfig.as_view(), name='raspi_config'),
    path('raspi-config/set-audio-jack/', raspi_config_views.SetAudioJack.as_view(), name='raspi_config_set_audio_jack'),
    path('raspi-config/set-audio-hdmi/', raspi_config_views.SetAudioHDMI.as_view(), name='raspi_config_set_audio_hdmi'),

]
