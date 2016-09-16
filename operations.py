import json

from constants import COOKIE, SCREENINGS
from gateways.graphite import GraphiteGateway

gg = GraphiteGateway(COOKIE)
dashboard = gg.get_dashboard(SCREENINGS)

THIRTY_DAYS = '-30d'

for service in dashboard.services:
    for panel in service.panels:
        data = gg.get_target(panel.compiled_target, THIRTY_DAYS,)
        print data
