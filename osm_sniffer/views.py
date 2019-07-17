import datetime
import os

from django.contrib.gis.db.models import Collect
from django.core.serializers import serialize
from django.shortcuts import render
from django.template.loader import render_to_string

from .models import OsmDiff, OsmDiffBuffer, MilepointRoute


def render_to_file(context, template, filepath):
    diff_id = context['diff_id']
    html_string = render_to_string(template, context=context)

    if not os.path.isdir(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))

    with open(filepath, 'w') as file_:
        file_.write(html_string)
    
    return True

def map_view(request, diff_id):
    polygons = OsmDiffBuffer.objects.filter(
        diff_id=diff_id
    )
    routes = MilepointRoute.objects.filter(
        the_geom__intersects=polygons[0].the_geom
    )
    ways = OsmDiff.objects.filter(
        type=OsmDiff.WAY
    ).filter(
        diff_id=diff_id
    )

    context = {
        'document_title': 'Test Title',
        'page_title': f'OSM Diff: {diff_id} from https://download.geofabrik.de/north-america/us/new-york.html',        
        'map_x': polygons[0].the_geom.centroid.x,
        'map_y': polygons[0].the_geom.centroid.y,
        'links': [['./test.html', 'Dead link'], ['https://google.com', 'Google']],
        'milepoint_geojson': serialize('geojson', routes).replace(r'\"', "'"),
        'ways_geojson': serialize('geojson', ways).replace(r'\"', "'"),
    }
    return render(request, 'osm_sniffer/map.html', context)

def index(request, diff_id):
    context = {
        'processing_date': datetime.date.today(),
        'diff_id': diff_id,
        'links': [['./test.html', 'Dead link'], ['https://google.com', 'Google']],
        'document_title': 'OSM Sniff Index for ' + str(diff_id),
        'page_title': 'OSM Sniff Results for ' + str(diff_id) + ' on ' + str(datetime.date.today()),
    }
    return render(request, 'osm_sniffer/index.html', context)

def string_map(context):
    diff_id = context['diff_id']
