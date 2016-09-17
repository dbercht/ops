from schematics.models import Model
from schematics.types import BooleanType, DecimalType, StringType
from schematics.types.compound import DictType, ListType, ModelType

from .panel import Panel, PanelMapper


class ServiceMapper():
    @classmethod
    def to_entity(cls, service, variables):
        return Service({
            'title': service['title'],
            'panels': [
                PanelMapper.to_entity(panel, variables)
                for panel in service['panels']
            ]
        })


class DashboardMapper():
    @classmethod
    def to_entity(
        cls,
        response,
        variables,
        from_delta,
        until_delta=None,
        period=None,
    ):
        dashboard = response['dashboard']
        required_variables = [
            v['name'] for v in dashboard['templating']['list']
        ]
        cls._validate_variables(required_variables, variables)
        return Dashboard({
            'title': response['dashboard']['title'],
            'variables': variables,
            'services': [
                ServiceMapper.to_entity(service, variables=variables)
                for service in dashboard['rows']
            ],
            'from_': GraphiteTime({
                'delta': from_delta,
                'period': period
            }),
            'until_': GraphiteTime({
                'now': True if not until_delta else False,
                'delta': until_delta,
                'period': period
            })
        })

    @classmethod
    def _validate_variables(cls, required_variables, variables):
        missing_vars = set(required_variables) - set(variables.keys())
        if missing_vars:
            raise Exception(
                'Missing variables: {}'.format(', '.join(list(missing_vars)))
            )
        return variables


class Service(Model):
    title = StringType()
    panels = ListType(ModelType(Panel))


class GraphiteTime(Model):
    now = BooleanType()
    delta = DecimalType()
    period = StringType()

    def get_time(self):
        if self.now:
            return 'now'
        return '{}{}'.format(self.delta, self.period)

class Dashboard(Model):
    title = StringType()
    services = ListType(ModelType(Service))
    variables = DictType(StringType)
    from_ = ModelType(GraphiteTime)
    until_ = ModelType(GraphiteTime)

    def until_time(self):
        return self.until_.get_time()

    def from_time(self):
        return self.from_.get_time()
