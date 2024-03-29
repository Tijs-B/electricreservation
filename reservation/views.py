import datetime

import dateutil.parser
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import UpdateView, CreateView, DeleteView, TemplateView, FormView
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.utils.translation import gettext as _
from rest_framework import generics

from reservation.forms import ReservationDetailForm, ReservationAddForm, ChargingReservationAddForm, \
    ChargingReservationDetailForm, UserConfigForm
from reservation.models import Car, Reservation, ChargingReservation
from reservation.serializers import ReservationSerializer, ChargingReservationSerializer


def index(request):
    if request.user.is_authenticated:
        return redirect('reservation:calendar_car', pk=request.user.profile.get_chosen_car().id)
    else:
        return redirect('login')


class UserSettings(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = 'reservation/user_settings.html'
    form_class = UserConfigForm
    success_message = _('User settings saved successfully.')

    def get_success_url(self):
        return reverse('reservation:calendar_car', kwargs={'pk': self.request.user.profile.get_chosen_car().id})

    def get_initial(self):
        initial = super().get_initial()
        initial['email'] = self.request.user.email
        initial['phone_number'] = self.request.user.profile.phone_number
        initial['calendar_color'] = self.request.user.profile.calendar_color
        return initial

    def form_valid(self, form):
        self.request.user.email = form.cleaned_data['email']
        self.request.user.save()

        self.request.user.profile.phone_number = form.cleaned_data['phone_number']
        self.request.user.profile.calendar_color = form.cleaned_data['calendar_color']
        self.request.user.profile.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['color_choices'] = ['#0275d8', '#5cb85c', '#5bc0de', '#f0ad4e', '#d9534f']
        return context


class CalendarCar(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Car
    template_name = 'reservation/calendar.html'

    def test_func(self):
        return self.get_object() in self.request.user.car_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_cars'] = self.request.user.car_set.all()
        return context

    def get(self, *args, **kwargs):
        response = super().get(*args, **kwargs)
        self.request.user.profile.last_car = self.get_object()
        self.request.user.profile.save()
        return response


class CarConfig(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    template_name = 'reservation/car_config.html'
    model = Car
    fields = ('name', 'summer_driving_range', 'winter_driving_range', 'charging_time')
    success_message = _('Car saved successfully.')

    def get_success_url(self):
        return reverse('reservation:calendar_car', kwargs={'pk': self.kwargs['pk']})

    def test_func(self):
        return self.request.user.car_set.filter(pk=self.kwargs['pk']).exists()


class ReservationDetail(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    template_name = 'reservation/reservation_detail.html'
    model = Reservation
    form_class = ReservationDetailForm
    success_message = _('Reservation saved successfully.')

    def test_func(self):
        car_id = self.get_object().car.id
        return self.request.user.car_set.filter(pk=car_id).exists()

    def get_success_url(self):
        return reverse('reservation:calendar_car', kwargs={'pk': self.get_object().car.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['car'] = self.get_object().car
        kwargs['owner'] = self.get_object().owner
        kwargs['id'] = self.get_object().id
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['car'] = self.get_object().car
        context['reservation_type'] = 'reservation'
        return context


class ReservationDelete(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Reservation
    success_message = _('Reservation deleted successfully.')

    def test_func(self):
        car_id = self.get_object().car.id
        return self.request.user.car_set.filter(pk=car_id).exists()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(ReservationDelete, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('reservation:calendar_car', kwargs={'pk': self.get_object().car.id})


class ReservationAdd(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    template_name = 'reservation/reservation_detail.html'
    model = Reservation
    form_class = ReservationAddForm
    success_message = _('Reservation saved successfully.')

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.car = Car.objects.get(pk=self.kwargs['car_id'])

    def test_func(self):
        return self.request.user.car_set.filter(pk=self.car.id).exists()

    def get_initial(self):
        initial = super().get_initial()

        if 'time' in self.request.GET:
            start_time = datetime.datetime.fromtimestamp(int(self.request.GET['time']))
        else:
            start_time = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)

        end_time = start_time + datetime.timedelta(hours=1)
        initial['start_time'] = start_time
        initial['end_time'] = end_time
        return initial

    def get_success_url(self):
        return reverse('reservation:calendar_car', kwargs={'pk': self.car.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['car'] = self.car
        kwargs['owner'] = self.request.user
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['car'] = Car.objects.get(pk=self.kwargs['car_id'])
        context['reservation_type'] = 'reservation'
        return context


class ChargingReservationDetail(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    template_name = 'reservation/reservation_detail.html'
    model = ChargingReservation
    form_class = ChargingReservationDetailForm
    success_message = _('Reservation saved successfully.')

    def test_func(self):
        car_id = self.get_object().car.id
        return self.request.user.car_set.filter(pk=car_id).exists()

    def get_success_url(self):
        return reverse('reservation:calendar_car', kwargs={'pk': self.get_object().car.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['car'] = self.get_object().car
        kwargs['id'] = self.get_object().id
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reservation_type'] = 'charging_reservation'
        context['car'] = self.get_object().car
        return context


class ChargingReservationDelete(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = ChargingReservation
    success_message = _('Reservation deleted successfully.')

    def test_func(self):
        car_id = self.get_object().car.id
        return self.request.user.car_set.filter(pk=car_id).exists()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(ChargingReservationDelete, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('reservation:calendar_car', kwargs={'pk': self.get_object().car.id})


class ChargingReservationAdd(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    template_name = 'reservation/reservation_detail.html'
    model = ChargingReservation
    form_class = ChargingReservationAddForm
    success_message = _('Reservation saved successfully.')

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.car = Car.objects.get(pk=self.kwargs['car_id'])

    def test_func(self):
        return self.request.user.car_set.filter(pk=self.car.id).exists()

    def get_initial(self):
        initial = super().get_initial()

        if 'time' in self.request.GET:
            start_time = datetime.datetime.fromtimestamp(int(self.request.GET['time']))
        else:
            start_time = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)

        end_time = start_time + datetime.timedelta(hours=self.car.charging_time)
        initial['start_time'] = start_time
        initial['end_time'] = end_time
        return initial

    def get_success_url(self):
        return reverse('reservation:calendar_car', kwargs={'pk': self.car.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['car'] = self.car
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['car'] = self.car
        context['reservation_type'] = 'charging_reservation'
        return context


class DistanceLeft(LoginRequiredMixin, UserPassesTestMixin, SingleObjectMixin, View):
    model = Car

    def test_func(self):
        car_id = self.get_object().id
        return self.request.user.car_set.filter(pk=car_id).exists()

    def get(self, request, *args, **kwargs):
        if 'time' in request.GET:
            time = datetime.datetime.fromtimestamp(int(request.GET['time']))
        else:
            time = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
        return JsonResponse({
            'distance_left': self.get_object().get_distance_left(time),
            'driving_range': self.get_object().get_driving_range(time)
        })


class APIReservationsList(LoginRequiredMixin, UserPassesTestMixin, generics.ListAPIView):
    serializer_class = ReservationSerializer

    def test_func(self):
        return self.request.user in Car.objects.get(pk=self.kwargs['pk']).users.all()

    def get_queryset(self):
        start_time = dateutil.parser.parse(self.request.GET['start'])
        end_time = dateutil.parser.parse(self.request.GET['end'])
        return Reservation.objects. \
            filter(Q(car__id=self.kwargs['pk']) &
                   (Q(start_time__range=(start_time, end_time)) | Q(end_time__range=(start_time, end_time))))


class APIChargingReservationsList(LoginRequiredMixin, UserPassesTestMixin, generics.ListAPIView):
    serializer_class = ChargingReservationSerializer

    def test_func(self):
        return self.request.user in Car.objects.get(pk=self.kwargs['pk']).users.all()

    def get_queryset(self):
        start_time = dateutil.parser.parse(self.request.GET['start'])
        end_time = dateutil.parser.parse(self.request.GET['end'])
        return ChargingReservation.objects. \
            filter(Q(car__id=self.kwargs['pk']) &
                   (Q(start_time__range=(start_time, end_time)) | Q(end_time__range=(start_time, end_time))))
