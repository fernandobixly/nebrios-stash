import logging


from oauth2utils import slugify, get_request_value

logging.basicConfig(filename='nebrios_stash.log', level=logging.DEBUG)

def example(request):
    response = HttpResponse("Testing 1 2 3")
    logging.debug("Response body: %s", response.content)
    return response
