# Set up Django scripting environment
import os
import sys
project_path = r'D:\OpenStreetMap\osmdiff_viewer'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osmdiff_viewer.settings')
sys.path.append(project_path)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# start script
import datetime
import subprocess
import time

from django.contrib.gis.db.models import Collect
from django.core.serializers import serialize
from django.shortcuts import render
from django.template.loader import render_to_string

from osm_sniffer.models import OsmDiff, OsmDiffBuffer, MilepointRoute
# from osm_sniffer.views import save_string_render
diff_id = 310
today = datetime.date.today()

# download_params = [
#     'python',
#     r'D:\OpenStreetMap\osmdiff_viewer\scripts\download_and_process_osc.py',
#     str(diff_id)
# ]
# print('\nCalling download script')
# print(' '.join(download_params))
# time.sleep(1.5)
# subprocess.call(download_params)

# load_params = [
#     'python',
#      r'D:\OpenStreetMap\osmdiff_viewer\scripts\load_diffs.py',
#     str(diff_id)
# ]
# print('\nCalling load script')
# print(' '.join(load_params))
# time.sleep(1.5)
# subprocess.call(load_params)

# Build the map views
def render_to_file(context, template, filepath):
    print(f'TEMPLATE: {template}')
    diff_id = context['diff_id']
    # context = {
    #     'processing_date': datetime.date.today(),
    #     'diff_id': diff_id,
    #     'links': [['./test.html', 'Dead link'], ['https://google.com', 'Google']],
    #     'document_title': 'OSM Sniff Index for ' + str(diff_id),
    #     'page_title': 'OSM Sniff Results for ' + str(diff_id) + ' on ' + str(datetime.date.today()),
    # }
    html_string = render_to_string(template, context=context)

    # output_path = os.path.abspath(os.path.join(
    #     os.path.dirname(__file__),
    #     '..',
    #     'dist',
    #     f'{today}_{diff_id}',
    #     'index.html'
    # ))

    if not os.path.isdir(filepath):
        os.makedirs(filepath)
    with open(filepath, 'w') as file_:
        file_.write(html_string)

    return context

build_params = []
links = []
polygons = OsmDiffBuffer.objects.filter(
    diff_id=diff_id
)
for i, polygon in enumerate(polygons[:2]):
    routes = MilepointRoute.objects.filter(
        the_geom__intersects=polygon.the_geom
    )
    ways = OsmDiff.objects.filter(
        type=OsmDiff.WAY
    ).filter(
        the_geom__intersects=polygon.the_geom
    )
    map_context = {
        'document_title': f'OSM Diff {diff_id} - {today}',
        'page_title': f'OSM Diff {diff_id} Processed {today}',
        'diff_id': diff_id,
        'map_x': polygon.the_geom.centroid.x,
        'map_y': polygon.the_geom.centroid.y,
        'milepoint_geojson': serialize('geojson', routes).replace(r'\"', "'"),
        'ways_geojson': serialize('geojson', ways).replace(r'\"', "'"),
    }

    output_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        'dist',
        f'{today}_{diff_id}',
        'maps',
        f'map_{i}.html'
    ))
    if not os.path.isdir(os.path.dirname(output_path)):
        print(f'Creating: {os.path.dirname(output_path)}')
        os.makedirs(os.path.dirname(output_path))
    links.append([f'./map_{i}.html', f'Diff {diff_id}:{i}'])
    # template_path = os.path.abspath(os.path.join(
    #     os.path.dirname(__file__),
    #     '..',
    #     'osm_sniffer',
    #     'templates',
    #     'osm_sniffer',
    #     'map.html'
    # ))
    build_params.append([map_context, 'osm_sniffer/map.html', output_path])
    # build_params.append([map_context, template_path, output_path])

for build_param in build_params:
    build_param[0]['links'] = links

with open('test.html', 'w') as out:
    out.write('out')
for param in build_params:
    print('saving string')
    print(param[1])
    render_to_string(*param)

index_context = {
    'processing_date': datetime.date.today(),
    'diff_id': diff_id,
    'map_x': polygon.the_geom.centroid.x,
    'map_y': polygon.the_geom.centroid.y,

}