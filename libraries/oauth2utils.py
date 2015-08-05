import re
import unidecode


def slugify(text):
    text = unidecode.unidecode(text).lower()
    return re.sub(r'\W+', '-', text)


def get_request_value(request, key, default=None):
    value = default
    if request.FORM:
        try:
            value = getattr(request.FORM, key)
            if value is None:
                value = default
        except:
            pass
    else:
        try:
            value = request.BODY.get(key, default)
        except:
            pass
    return value