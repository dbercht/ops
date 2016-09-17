import json

from constants import COOKIE, SCREENINGS
from gateways.graphite import GraphiteGateway

from functions import avg, total

VARIABLES = {
    'granularity': '5min',
    'dc': '{sjc1,dca1}',
}

NOW = 'now'
DAYS = 'd'
SEVEN_DAYS = -7
THIRTY_DAYS = -30
from_delta = -7

gg = GraphiteGateway(COOKIE)

def get_dashboard(dashboard_name, variables, from_delta, until_delta, period):
    dashboard = gg.get_dashboard(
        dashboard_name,
        variables,
        from_delta,
        until_delta=until_delta,
        period=period,
    )
    print '{}: {} - {}'.format(dashboard.title, dashboard.from_time(), dashboard.until_time())
    for service in dashboard.services:
        print "{}:".format(service.title)
        for panel in service.panels:
            target = gg.get_target(
                panel.compiled_target,
                from_=dashboard.from_time(),
                until=dashboard.until_time(),
            )
            if target is False:
                print panel.compiled_target
                print "  {}: {}".format(panel.title, panel.value)
                continue
            datapoints = target[0]['datapoints']
            panel.calculate_value(datapoints)
            print "  {}: {}".format(panel.title, panel.value)
        return dashboard
    return dashboard

now = get_dashboard(SCREENINGS, VARIABLES, from_delta, None, DAYS)
last = get_dashboard(SCREENINGS, VARIABLES, from_delta*2, from_delta, DAYS)
service_panel_now_then = {}
for service in now.services:
    service_panel_now_then[service.title] = {}
    for panel in service.panels:
        service_panel_now_then[service.title][panel.title]= {
            'raw': [panel.value]
        }

for service in last.services:
    for panel in service.panels:
        service_panel_now_then[service.title][panel.title]['raw'].append(panel.value)
        this_week = service_panel_now_then[service.title][panel.title]['raw'][0]
        last_week = panel.value
        try:
            delta = this_week - last_week
            percent = ((this_week - last_week) / last_week ) * 100
            service_panel_now_then[service.title][panel.title]['parsed'] = {
                'delta': delta,
                'percent': percent,
            }
        except Exception as e:
            print 'exception'
            print e

print service_panel_now_then
