from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import FormView, UpdateView, DetailView
from rest_framework.views import APIView
from rest_framework import generics

from reservation.forms import CarConfigForm
from reservation.models import Car, Reservation
from reservation.serializers import CarSerializer, ReservationSerializer


def index(request):
    if request.user.is_authenticated:
        return redirect('reservation:calendar')
    else:
        return redirect('login')


@login_required
def calendar(request):
    default_car = Car.objects.filter(users__in=[request.user]).first()
    return redirect('reservation:calendar_car', car_id=default_car.id)


# class CalendarCar(LoginRequiredMixin, UserPassesTestMixin, DetailView):
#     model = Car
#     template_name = 'reservation/calendar.html'
#
#     def test_func(self):
#         return self.request.user.car_set.filter(pk=self.kwargs['pk']).exists()
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         print(context)
#         context['cars'] = self.request.user.car_set.all()


@login_required
def calendar_car(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    if not request.user.car_set.filter(pk=car_id).exists():
        raise Http404()

    context = {
        'current_car': car,
        'cars': request.user.car_set.all()
    }

    return render(request, 'reservation/calendar.html', context)


class CarConfig(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'reservation/car_config.html'
    form_class = CarConfigForm

    def get_success_url(self):
        return reverse('reservation:calendar_car', kwargs={'car_id':self.kwargs['pk']})

    def test_func(self):
        return self.request.user.car_set.filter(pk=self.kwargs['pk']).exists()

    def get_queryset(self):
        return Car.objects.all()


class ReservationDetail(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    def test_func(self):
        car_id = self.get_object().car.id
        return self.request.user.car_set.filter(pk=car_id).exists()

    template_name = 'reservation/reservation_detail.html'
    form_class =


class APIReservationsList(LoginRequiredMixin, generics.ListAPIView):
    serializer_class = ReservationSerializer

    def get_queryset(self):
        return Reservation.objects.filter(car__id=self.kwargs['pk'])

