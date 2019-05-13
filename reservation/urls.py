from django.urls import path

from . import views

app_name='reservation'
urlpatterns = [
    path('', views.index, name='index'),

    path('calendar/', views.calendar, name='calendar'),
    path('calendar/<int:pk>/', views.CalendarCar.as_view(), name='calendar_car'),
    path('calendar/<int:pk>/config/', views.CarConfig.as_view(), name='calendar_car_config'),

    path('reservation/<int:pk>/', views.ReservationDetail.as_view(), name='reservation'),
    path('reservation/<int:pk>/delete/', views.ReservationDelete.as_view(), name='reservation_delete'),
    path('car/<int:car_id>/reservation/add/', views.ReservationAdd.as_view(), name='reservation_add'),
    path('car/<int:car_id>/charging_reservation/add/', views.ChargingReservationAdd.as_view(),
         name='charging_reservation_add'),

    path('api/car/<int:pk>/reservations/', views.APIReservationsList.as_view(), name='api_car_reservations'),
    path('api/car/<int:pk>/charging_reservations/', views.APIChargingReservationsList.as_view(),
         name='api_car_charging_reservations'),
]
