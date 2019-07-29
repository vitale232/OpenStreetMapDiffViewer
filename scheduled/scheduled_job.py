# Set up Django scripting environment
import os
import sys
project_path = r'D:\OpenStreetMap\osmdiff_viewer'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osmdiff_viewer.settings')
sys.path.append(project_path)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Begin script
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
os.chdir(BASE_DIR)

import datetime
import json
import logging
import gzip
import requests
import subprocess
import sys

from bs4 import BeautifulSoup
from django.db.models import Max
from django.contrib.gis.gdal import DataSource, OGRGeometry
from django.utils.timezone import make_aware
from shapely.geometry import LineString
from shapely.ops import cascaded_union


from osm_sniffer.models import OsmDiff, OsmDiffBuffer
# from get_diff_number import get_diff_number


def get_diff_ids_download_and_load_data(BASE_DIR=BASE_DIR):
    start_time = datetime.datetime.now()
    log_dir = os.path.abspath(os.path.join(
        BASE_DIR,
        '..',
        'dist',
        'logs',
    ))
    log_path = os.path.join(
        log_dir,
        '{year:04d}-{month:02d}-{day:02d}_{hour:02d}{min:02d}{sec:02d}.log'.format(
            year=start_time.year, month=start_time.month, day=start_time.day,
            hour=start_time.hour, min=start_time.minute, sec=start_time.second
        )
    )
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    logger = initialize_logger(log_path, logging.DEBUG)
    diff_ids = get_diff_number(logger=logger)

    for diff_id in diff_ids:
        logger.info(f'Working on Diff ID: {diff_id}')
        logger.info('\n\n')
        logger.info(f'Downloading Diff ID: {diff_id}')
        download_process_diff(diff_id, logger=logger)
        
        logger.info('\n\n')
        logger.info(f'Loading into database - Diff ID: {diff_id}')
        load_osm_diff(diff_id, logger=logger)

        logger.info('\n\n')
        logger.info(f'Building HTML for diff ID: {diff_id}')
        build_html(diff_id, logger=logger)
        
    return logger


def get_diff_number(logger=None):
    if not logger:
        logger = initialize_logger()
    server_url = 'https://download.geofabrik.de/north-america/us/new-york-updates/000/002/'

    logger.info(f'\nSending get request to url: {server_url}')
    page = requests.get(server_url, verify=False)
    logger.debug(page)

    if page.status_code != 200:
        logger.error('ERROR: Something went wrong with the request')

    soup = BeautifulSoup(page.content,  'html.parser')
    table = soup.find('table')
    logging.debug('HTML table from the server:\n' + table.prettify())

    osc_data = []
    for data in table.find_all('a'):
        try:
            if data['href'].endswith('.osc.gz'): 
                osc_data.append(data['href'])
        except KeyError:
            pass

    remote_diff_ids = [int(diff.split('.')[0]) for diff in osc_data]
    logger.debug(f'REMOTE DIFF IDS: {remote_diff_ids}')

    max_local_diff_query = OsmDiff.objects.aggregate(Max('diff_id'))
    max_local_diff_id = max_local_diff_query['diff_id__max']
    if max_local_diff_id is None:
        logger.info('No diffs exist in the database.')
        answer = input('Do you want to download all existing diffs? [y/N]')
        
        if answer.lower() not in ['yes', 'y']:
            raise SystemExit('User specificed system exit!')
        
        max_local_diff_id = 0

    logger.info(f'Finding Diff IDs on Remote that are > {max_local_diff_id}')

    to_download_diff_ids = [diff_id for diff_id in remote_diff_ids if diff_id > max_local_diff_id]
    
    logger.info(f'Diff IDs to download: {to_download_diff_ids}')
    
    if len(to_download_diff_ids) < 1:
        logger.error('There are no new diffs to process. Exiting.')
        input('\nProcessing completed with no changes. Press [ENTER] to exit.')

    return to_download_diff_ids

def download_process_diff(diff_id, logger=None):
    if not logger:
        logger = initialize_logger()
    start_time = datetime.datetime.now()

    logger.info(f'Executing script: {os.path.abspath(__file__)}')
    logger.info(f'Start time: {start_time}')

    download_url = f'https://download.geofabrik.de/north-america/us/new-york-updates/000/002/{diff_id}.osc.gz'

    filename = os.path.basename(download_url)
    download_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            'diff_data',
            filename.split('.')[0],
            filename
        )
    )
    if not os.path.isdir(os.path.dirname(download_path)):
        os.makedirs(os.path.dirname(download_path))

    logger.info(f'Downloading OSM Diff file from:\n {download_url}')
    logger.debug(f'Saving file to:\n {download_path}')
    response = requests.get(download_url, verify=False)

    if response.status_code == 200:
        with open(download_path, 'wb') as download:
            download.write(response.content)

    logger.info('Download successful')
    logger.info(f'Unzipping downloaded gzip file:\n {download_path}')

    with gzip.open(download_path, 'rb') as gzip_file:
        osc_contents = gzip_file.read()

    osc_filepath = download_path[:-3]
    with open(osc_filepath, 'w', encoding=sys.stdout.encoding) as osc_file:
        osc_file.write(osc_contents.decode(sys.stdout.encoding))

    logger.info('Processing downloaded data using OSM tools')
    logger.debug(f'Converting .osc to .o5m')

    o5m_path = os.path.join(
        os.path.dirname(download_path),
        os.path.basename(download_path).split('.')[0] + '.o5m'
    )
    convert_params = [
        r'D:\Program_Files\osmconvert\osmconvert64-0.8.8p.exe',
        download_path,
        f'-o={o5m_path}'
    ]
    
    logger.debug(' Command: {}'.format(' '.join(convert_params)))
    subprocess.call(convert_params)
    logger.debug('Conversion successful')

    logger.debug(f'Filtering on "highway" tag and saving as OSM file')
    osm_path = o5m_path.replace('.o5m', '.osm')
    filter_params = [
        r'D:\Program_Files\osmfilter\osmfilter.exe',
        o5m_path,
        '--keep=highway=',
        '--drop=highway=service highway=footway highway=pedestrian highway=path highway=track highway=steps highway=cycleway highway=bridleway',
        '-o={}'.format(osm_path),
        '--verbose'
    ]
    logger.debug(' Command: {}'.format(' '.join(filter_params)))
    subprocess.call(filter_params)
    logger.debug('Filtering successful')

    logger.debug(f'\nConverting OSM File to geoJSON')
    geojson_path = osm_path.replace('.osm', '.geojson')
    geojson_params = [
        'osmtogeojson',
        '-e',
        '-n',
        osm_path
    ]
    logger.debug(' Command: {}'.format(' '.join(geojson_params)))

    with open(geojson_path, 'w') as geojson_file:
        subprocess.call(geojson_params, stdout=geojson_file, stderr=geojson_file, shell=True)
    logger.debug('Conversion successful')

    end_time = datetime.datetime.now()
    logger.info(f'Completed at: {end_time}')
    logger.info(f'Execution time: {end_time-start_time}')
    
    return osm_path

def load_osm_diff(diff_id, logger=None):
    start_time = datetime.datetime.now()
    if not logger:
        logger = initialize_logger()
    
    logger.info(f'Executing script:   {os.path.abspath(__file__)}')
    logger.info(f'Execution start at: {start_time}')

    model_layer_mapping = {
        'osm_id': 'id',
        'tags': 'tags',
        'meta': 'meta',
        'tainted': 'tainted',
        'type': 'type',
    }

    geojson_path = r'D:\OpenStreetMap\diff_data\{diff_id}\{diff_id}.geojson'.format(diff_id=diff_id)
    logger.debug(f'Input geoJSON file: {geojson_path}')

    data_source = DataSource(geojson_path)
    layer = data_source[0]

    feature_count = len(layer)
    i = 1
    for feature in layer:
        try:
            feature_data = {
                key: feature.get(value) for (key, value) in model_layer_mapping.items()
            }

            # Use OGRGeometry to strip z-values from polyline vertices
            geometry = OGRGeometry(feature.geom.ewkt)
            geometry.coord_dim = 2
            feature_data['the_geom'] = geometry.ewkt
            feature_data['diff_id'] = diff_id

            if feature_data['type'] == 'way':
                feature_data['type'] = OsmDiff.WAY
            if feature_data['type'] == 'node':
                feature_data['type'] = OsmDiff.NODE
            if feature_data['type'] == 'relation':
                feature_data['type'] = OsmDiff.RELATION

            if isinstance(feature_data['tags'], str):
                feature_data['tags'] = json.loads(feature_data['tags'])
            if isinstance(feature_data['meta'], str):
                feature_data['meta'] = json.loads(feature_data['meta'])

            route = OsmDiff(**feature_data)
            route.save()

            if i % 10 == 0:
                logger.debug(f'Processed {i} of {feature_count} features')
            if i == feature_count:
                logger.debug(f'Processed {i} of {feature_count} features')
            i += 1
        except Exception as exc:
            logger.error(f'\n\nFailed on feautre {i} of {feature_count}')
            logger.error(feature_data)
            logger.exception(exc)
            i += 1

    logger.debug('\nCreating buffer polygons of the newly generated ways and saving to database')
    ways = OsmDiff.objects.filter(
        type=OsmDiff.WAY
    ).filter(
        diff_id=diff_id
    )

    polys = [
        LineString(way.the_geom).buffer(0.01) for way in ways
    ]
    multi_polys = cascaded_union(polys)
    
    logger.debug('Saving polygons to database')
    feature_count = len(multi_polys)
    i = 0
    for poly in multi_polys:
        osm_diff_buffer = OsmDiffBuffer(
            diff_id=diff_id,
            created_date=datetime.datetime.today(),
            the_geom=poly.wkt
        )
        osm_diff_buffer.save()

        if i % 10 == 0:
            logger.debug(f'Processed {i} of {feature_count} features')
        if i == feature_count:
            logger.debug(f'Processed {i} of {feature_count} features')
        i += 1

    end_time = datetime.datetime.now()
    
    logger.info(f'Execution complete at:  {end_time}')
    logger.info(f'Execution run time:     {end_time-start_time}')
    

def build_html(diff_id, logger=None):
    build_html_args = [
        'python',
        os.path.abspath(os.path.join('..', 'manage.py')),
        'buildhtml',
        str(diff_id)
    ]
    logger.info('Building HTML')
    logger.debug(' '.join(build_html_args))
    
    subprocess.call(build_html_args)


def initialize_logger(log_path=None, log_level=logging.INFO):
    log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    root_logger = logging.getLogger()

    if log_path:
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    root_logger.setLevel(level=log_level)

    return root_logger


if __name__ == '__main__':
    start_time = datetime.datetime.now()
    logger = get_diff_ids_download_and_load_data()
    logger.info(f'Scheduled job run time: {datetime.datetime.now()-start_time}')
    input('\nProcessing complete. Press [ENTER] to exit.')
