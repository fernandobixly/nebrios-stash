

def get_process(PROCESS=None, PROCESS_ID=None, PARENT=None, kind=None):
        if PROCESS is not None:
            return PROCESS, False
        elif PROCESS_ID is not None:
            return Process.objects.get(PROCESS_ID=PROCESS_ID, kind=kind), False
        else:
            if isinstance(PARENT, NebriOSModel):
                PARENT = PARENT.process()
            return Process.objects.create(kind=kind, PARENT=PARENT), True


def cleanup_search_kwargs(cls, kwargs):
    for key, value in kwargs.items():
        if isinstance(value, NebriOSModel):
            if key == "PARENT":
                kwargs[key] = value.process()
            else:
                del kwargs[key]
                kwargs["%s_id"] = value.process().PROCESS_ID
        return kwargs


class NebriOSField(object):

    def __init__(self, default=None, required=False):
        self.default = default
        self.required = required

    def default_value(self):
        if callable(self.default):
            return (self.default)()
        else:
            return self.default


class NebriOSReference(NebriOSField):

    def __init__(self, model_class, default=None, required=False):
        super(NebriOSReference, self).__init__(default=default, required=required)
        self.model_class = model_class


def make_reference_get(model_class, field_name):
    def getter(self):
        value = self.__getitem__('%s_id' % field_name)
        if value is None:
            return None
        return model_class(PROCESS_ID=value)
    return getter


def make_reference_set(model_class, field_name):
    def setter(self, value):
        if value is None:
            self.__setitem__('%s_id' % field_name, None)
            return None
        if not isinstance(value, model_class):
            raise Exception("%s not a valid %s for field %s", value, model_class.__name__, field_name)
        if not isinstance(value.PROCESS_ID, int) and not isinstance(value.PROCESS_ID, long):
            value.save()
        self.__setitem__('%s_id' % field_name, value.PROCESS_ID)
        return value
    return setter


def make_get(field_name):
    def getter(self):
        return self.__getitem__(field_name)
    return getter


def make_set(field_name):
    def setter(self, value):
        return self.__setitem__(field_name, value)
    return setter


class NebriOSModelMetaClass(type):

    def __new__(cls, name, base, attrs):
        fields = {}
        for key, value in attrs.iteritems():
            if isinstance(value, NebriOSField):
                fields[key] = value
                if isinstance(value, NebriOSReference):
                    attrs[key] = property(make_reference_get(value.model_class, key),
                                          make_reference_set(value.model_class, key))
                else:
                    attrs[key] = property(make_get(key), make_set(key))
        attrs['__FIELDS__'] = fields
        if 'kind' not in attrs:
            attrs['kind'] = name.lower()
        return type.__new__(cls, name, base, attrs)


class NebriOSModel(object):

    __metaclass__ = NebriOSModelMetaClass

    kind = None

    def __init__(self, PROCESS=None, PROCESS_ID=None, PARENT=None, **kwargs):
        if self.__class__.kind is None:
            raise Exception('Model kind is None')
        self.__dict__['PROCESS'], created = get_process(PROCESS=PROCESS, PROCESS_ID=PROCESS_ID, PARENT=PARENT,
                                                        kind=self.__class__.kind)
        self.__setitem__('kind', self.__class__.kind)
        if created:
            for key, field in self.__class__.__FIELDS__.iteritems():
                self.__setitem__(key, field.default_value())
        for key, value in kwargs.iteritems():
            self.__setitem__(key, value)

    def process(self):
        return self.__dict__['PROCESS']

    def __setattr__(self, key, value):
        return self.process().__setattr__(key, value)

    def __getattr__(self, item):
        return self.process().__getattr__(item)

    def __setitem__(self, key, value):
        return self.process().__setitem__(key, value)

    def __getitem__(self, item):
        return self.process().__getitem__(item)

    def save(self):
        for key, field in self.__class__.__FIELDS__.iteritems():
            if field.required and (not self.__getitem__(key)):
                raise Exception("Field %s is required" % key)
        return self.process().save()

    @classmethod
    def get(cls, **kwargs):
        kwargs['kind'] = cls.kind
        kwargs = cleanup_search_kwargs(cls, kwargs)
        p = Process.objects.get(**kwargs)
        return cls(PROCESS=p)

    @classmethod
    def filter(cls, **kwargs):
        kwargs['kind'] = cls.kind
        kwargs = cleanup_search_kwargs(cls, kwargs)
        q = Process.objects.filter(**kwargs)
        return [cls(PROCESS=p) for p in q]

    def __str__(self):
        return "<%s id %s>" % (self.__class__.__name__, self.process().PROCESS_ID)

    def __repr__(self):
        return str(self)