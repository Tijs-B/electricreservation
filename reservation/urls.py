from django.urls import path

from . import views

app_name='reservation'
urlpatterns = [
    path('', views.index, name='index'),

    path('calendar/', views.calendar, name='calendar'),
    path('calendar/<int:car_id>/', views.calendar_car, name='calendar_car'),
    path('calendar/<int:pk>/config/', views.CarConfig.as_view(), name='calendar_car_config'),

    path('reservation/<int:pk>/', views.ReservationDetail.as_view(), name='reservation'),

    path('api/car/<int:pk>/reservations/', views.APIReservationsList.as_view(), name='api_car_reservations')
]