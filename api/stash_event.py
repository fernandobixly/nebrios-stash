import logging

from stashutils import slugify, get_request_value

logging.basicConfig(filename='nebrios_stash.log', level=logging.DEBUG)


def create_event(request):
    service_slug = get_request_value(request, "service_slug", None)
    if service_slug is None:
        raise HttpResponseBadRequest()
    service = Process.objects.get(kind="stash_service", service_slug=service_slug)
    event = Process.objects.create(kind="stash_event", created=datetime.now(), active=True)
    event.PARENT = service
    event.service_status = get_request_value(request, "service_status", "down")
    event.details = get_request_value(request, "event_details", "")
    event.save()
    event_dict = event.as_dict()
    event_dict["event_id"] = event.PROCESS_ID
    return event_dict


def update_event(request):
    event_id = get_request_value(request, "event_id", None)
    event = Process.objects.get(kind="stash_event", PROCESS_ID=event_id)
    event.service_status = get_request_value(request, "service_status", event.service_status)
    event.details = get_request_value(request, "event_details", event.details)
    event.save()
    event_dict = event.as_dict()
    event_dict["event_id"] = event.PROCESS_ID
    return event_dict


def delete_event(request):
    event_id = get_request_value(request, "event_id", None)
    event = Process.objects.get(kind="stash_event", PROCESS_ID=event_id)
    event.active = False
    event.save()
    return True