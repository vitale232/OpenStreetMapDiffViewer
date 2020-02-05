# Set up Django scripting environment
import os
import sys
project_path = r'D:\OpenStreetMap\OpenStreetMapDiffViewer'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osmdiff_viewer.settings')
sys.path.append(project_path)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Begin script
import logging

from bs4 import BeautifulSoup
from django.db.models import Max
import pandas as pd
import requests

from osm_sniffer.models import OsmDiff


def get_diff_number(logger=None):
    print(logger)
    server_url = 'https://download.geofabrik.de/north-america/us/new-york-updates/000/002/s'
    if logger:
        logger.info(f'\nSending get request to url: {server_url}')
    page = requests.get(server_url, verify=False)
    if logger:
        logger.debug(page)
    if page.status_code != 200:
        logger.error('ERROR: Something went wrong with the request')

    soup = BeautifulSoup(page.content,  'html.parser')
    table = soup.find('table')

    osc_data = []
    for data in table.find_all('a'):
        try:
            if data['href'].endswith('.osc.gz'): 
                osc_data.append(data['href'])
        except KeyError:
            pass

    remote_diff_ids = [int(diff.split('.')[0]) for diff in osc_data]

    max_local_diff_query = OsmDiff.objects.aggregate(Max('diff_id'))
    max_local_diff_id = max_local_diff_query['diff_id__max']

    to_download_diff_ids = [diff_id for diff_id in remote_diff_ids if diff_id > max_local_diff_id]

    return to_download_diff_ids


if __name__ == '__main__':
    get_diff_number()
