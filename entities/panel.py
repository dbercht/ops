import re
from enum import Enum

from collections import defaultdict
from toposort import toposort_flatten

from schematics.models import Model
from schematics.types import DecimalType, StringType
from schematics.types.compound import ListType, ModelType

from functions import avg, total


class Value(Enum):
    AVG = 'avg'
    TOTAL = 'total'


class TargetMapper():

    @classmethod
    def to_entity(cls, target):
        return Target({
            'ref': target['refId'],
            'value': target['target'],
        })


class PanelMapper():

    @classmethod
    def to_entity(cls, panel, variables):
        panel = Panel({
            'title': panel['title'],
            'value_name': panel['valueName'],
            'targets': [
                TargetMapper.to_entity(target) for target in panel['targets']
            ],
        })
        panel.compiled_target = panel.compile_target(variables)
        return panel


class Target(Model):
    ref = StringType()
    value = StringType()


class Panel(Model):
    title = StringType()
    targets = ListType(ModelType(Target))
    value_name = StringType()
    compiled_target = StringType()
    value = DecimalType()

    def calculate_value(self, datapoints):
        if self.value_name == Value.AVG.value:
            self.value = avg(datapoints)
        elif self.value_name == Value.TOTAL.value:
            self.value = total(datapoints)
        else:
            raise Exception("Invalid value_name %s" % self.value_name)

    def _find_refs_in_target(self, target_value):
        pattern = re.compile("(#[A-Z])")
        return set(pattern.findall(target_value))

    def _get_refs(self):
        return {'#' + target.ref: target for target in self.targets}

    def _topo_sort_targets(self):
        refs = self._get_refs()

        dependencies = defaultdict(set)
        for ref, target in refs.iteritems():
            target_value = target.value
            found_refs = self._find_refs_in_target(target_value)
            if found_refs:
                dependencies[ref] = found_refs
        return [refs[ref] for ref in toposort_flatten(dependencies)]

    def compile_target(self, variables):
        #  default to first target
        target = self.targets[0]

        refs = self._get_refs()

        # Targets are sorted according to their dependencies
        # First target has least dependencies
        # Last target is the ref with all dependencies
        for target in self._topo_sort_targets():
            target_value = target.value
            found_refs = self._find_refs_in_target(target_value)

            for found_ref in found_refs:
                target_value = re.sub(
                    found_ref,
                    refs[found_ref].value,
                    target_value,
                )

            target.value = target_value

        #  Replace granularity to 5min
        for var, value in variables.iteritems():
            target.value = target.value.replace('$' + var, value)

        return target.value
