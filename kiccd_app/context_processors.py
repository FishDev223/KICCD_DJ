from django.conf import settings


def mapbox_token(request):
    return {'MAPBOX_TOKEN': settings.MAPBOX_TOKEN}
