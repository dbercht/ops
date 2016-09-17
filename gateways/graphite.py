import json
import urllib

from entities.dashboard import DashboardMapper
from requests import get, post


DASHBOARD_URL = 'https://graphite.uberinternal.com/grafana2/api/dashboards/db/{dashboard}'
TARGET_URL = 'https://graphite.uberinternal.com/grafana2/api/datasources/proxy/5/render'
TARGET_M3_URL = 'https://graphite.uberinternal.com/grafana2/api/datasources/proxy/7/render'

JSON = 'json'
MAX_POINTS = 1000

class GraphiteGateway(object):
    def __init__(self, cookie):
        self._headers = {
            'Cookie': cookie,
            #  'Content-Type': 'application/x-www-form-urlencoded'
        }

    def get_target(self, target, from_, until, format_=JSON, max_data_points=MAX_POINTS):
        data={
            'target': target,
            'from': from_,
            'until': until,
            'format': format_,
            'max_data_points': max_data_points,
        }
        #  super hacky. ideally pass in a target request object and encapsualte this answer
        if 'sentry-service ' in target:
            r = get(
                TARGET_M3_URL,
                headers=self._headers,
                params=data
            )
        else:
            r = post(
                TARGET_URL,
                headers=self._headers,
                data=data
            )
        try:
            return r.json()
        except ValueError:
            return False

    def get_dashboard(self, dashboard, variables, from_delta, until_delta=None, period='days'):
        r = get(
            DASHBOARD_URL.format(dashboard=dashboard),
            headers=self._headers,
        )
        return DashboardMapper.to_entity(r.json(), variables, from_delta,  until_delta, period)
