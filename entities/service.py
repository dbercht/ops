from schematics.models import Model
from schematics.types import StringType


class ServiceMapper():
    @classmethod
    def to_entity(cls, service):
        return Service({
            service['title'],
        })


class Service(Model):
    title = StringType()
