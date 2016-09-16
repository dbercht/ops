import json
import urllib

from entities.dashboard import DashboardMapper
from requests import get, post


DASHBOARD_URL = 'https://graphite.uberinternal.com/grafana2/api/dashboards/db/{dashboard}'
TARGET_URL = 'https://graphite.uberinternal.com/grafana2/api/datasources/proxy/5/render'

NOW = 'now'
JSON = 'json'
MAX_POINTS = 1000

class GraphiteGateway(object):
    def __init__(self, cookie):
        self._headers = {
            'Cookie': cookie,
            #  'Content-Type': 'application/x-www-form-urlencoded'
        }

    def get_target(self, target, from_, until=NOW, format_=JSON, max_data_points=MAX_POINTS):
        data={
            'target': target,
            'from': from_,
            'until': until,
            'format': format_,
            'max_data_points': max_data_points,
        }
        print data
        r = post(
            TARGET_URL,
            headers=self._headers,
            data=data
        )
        return r.text

    def get_dashboard(self, dashboard):
        r = get(
            DASHBOARD_URL.format(dashboard=dashboard),
            headers=self._headers,
        )
        return DashboardMapper.to_entity(r.json())
