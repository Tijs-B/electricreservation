from django.conf import settings


def locale_processor(request):
    return {'LANGUAGE_SETTING': settings.LANGUAGE_CODE}
