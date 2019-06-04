from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, RedirectView

from reservation import audio


class RaspiConfig(LoginRequiredMixin, TemplateView):
    template_name = 'reservation/raspi_config.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_audio_output'] = audio.get_current_audio_output()
        return context


class SetAudioJack(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('reservation:raspi_config')

    def get(self, *args, **kwargs):
        audio.set_audio_output_jack()
        return super().get(*args, **kwargs)


class SetAudioHDMI(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('reservation:raspi_config')

    def get(self, *args, **kwargs):
        audio.set_audio_output_hdmi()
        return super().get(*args, **kwargs)
