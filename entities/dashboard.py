import re
from collections import defaultdict

from schematics.models import Model
from schematics.types import StringType
from schematics.types.compound import ListType, ModelType


class TargetMapper():
    @classmethod
    def to_entity(cls, target):
        return Target({
            'ref': target['refId'],
            'value': target['target'],
        })


class PanelMapper():
    @classmethod
    def to_entity(cls, panel):
        panel = Panel({
            'title': panel['title'],
            'value_name': panel['valueName'],
            'targets': [
                TargetMapper.to_entity(target) for target in panel['targets']
            ],
        })
        panel.compiled_target = panel.compile_target()
        return panel
    

class ServiceMapper():
    @classmethod
    def to_entity(cls, service):
        return Service({
            'title': service['title'],
            'panels': [
                PanelMapper.to_entity(panel) for panel in service['panels']
            ]
        })

class DashboardMapper():
    @classmethod
    def to_entity(cls, response):
        dashboard = response['dashboard']
        return Dashboard({
            'title': response['dashboard']['title'],
            'services': [
                ServiceMapper.to_entity(service)
                for service in dashboard['rows']
            ]
        })


class Target(Model):
    ref = StringType()
    value = StringType()


class Panel(Model):
    title = StringType()
    targets = ListType(ModelType(Target))
    value_name = StringType()
    compiled_target = StringType()

    def compile_target(self):
        #  if just one, assume it's clean and return that
        if len(self.targets) == 1:
            return self.targets[0].value

        refs = {'#' + target.ref: target for target in self.targets}

        #  if multiple, assume they compile into a single one
        compiled_target = None
        pattern = re.compile("(#[A-Z])")

        for ref, target in refs.iteritems():
            target_value = target.value
            found_refs = set(pattern.findall(target_value))

            if not found_refs:
                continue

            for found_ref in found_refs:
                target_value = re.sub(found_ref, refs[found_ref].value, target_value)

            target.value = target_value
            break
        else:
            raise RuntimeError()

        #  Replace granularity to 5min
        return target.value.replace('$granularity', '5min')

class Service(Model):
    title = StringType()
    panels = ListType(ModelType(Panel))


class Dashboard(Model):
    title = StringType()
    services = ListType(ModelType(Service))
