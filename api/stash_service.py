import logging

from stashutils import slugify, get_request_value

logging.basicConfig(filename='nebrios_stash.log', level=logging.DEBUG)


def create_service(request):
    service_name = get_request_value(request, "service_name")
    if service_name is None:
        raise HttpResponseBadRequest()
    ping = get_request_value(request, "ping", default=False)
    service_slug = slugify(service_name)
    service, created = Process.objects.get_or_create(kind="stash_service", service_slug=service_slug)
    if created:
        service.last_actor = request.user
        service.service_name = service_name
        service.ping = ping
        service.active = True
        service.save()
    load_card('update-stash-service-card', pid=service.PROCESS_ID, user=request.user)
    return service.as_dict()


def update_service(request):
    service_slug = get_request_value(request, "service_slug", None)
    if service_slug is None:
        raise HttpResponseBadRequest()
    service_name = get_request_value(request, "service_name", "")
    if service_name is None or service_name == "":
        raise HttpResponseBadRequest()
    ping = get_request_value(request, "ping", False)
    service = Process.objects.get(kind="stash_service", service_slug=service_slug)
    service.service_name = service_name
    service.ping = ping
    service.active = True
    service.save()
    return service.as_dict()


def delete_service(request):
    service_slug = get_request_value(request, "service_slug", None)
    if service_slug is None:
        raise HttpResponseBadRequest()
    service = Process.objects.get(kind="stash_service", service_slug=service_slug)
    service.active = False
    service.save()
    return True