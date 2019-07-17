# Set up Django scripting environment
import os
import sys
project_path = r'D:\OpenStreetMap\osmdiff_viewer'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osmdiff_viewer.settings')
sys.path.append(project_path)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


# Begin script
import datetime
import json

from django.contrib.gis.gdal import DataSource, OGRGeometry
from django.utils.timezone import make_aware
from shapely.geometry import LineString
from shapely.ops import cascaded_union

from osm_sniffer.models import OsmDiff, OsmDiffBuffer

diff_id = sys.argv[-1]

start_time = datetime.datetime.now()
print(f'\nExecuting script:   {os.path.abspath(__file__)}')
print(f'Execution start at: {start_time}')

model_layer_mapping = {
    'osm_id': 'id',
    'tags': 'tags',
    'meta': 'meta',
    'tainted': 'tainted',
    'type': 'type',
    # 'diff_id': 'diff_id',
}

geojson_path = r'D:\OpenStreetMap\diff_data\{diff_id}\{diff_id}.geojson'.format(diff_id=diff_id)
# diff_id = int(os.path.basename(geojson_path).split('.')[0])

print(f'\nReading input data from the following file:\n {geojson_path}\n')
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
            print(f'Processed {i} of {feature_count} features\r', end='')
        if i == feature_count:
            print(f'Processed {i} of {feature_count} features\r', end='')
        i += 1
    except Exception as exc:
        print(f'\n\nFailed on feautre {i} of {feature_count}')
        print(feature_data)
        print(exc)
        print('')
        i += 1

print('\nCreating buffer polygons of the newly generated ways and saving to database')
ways = OsmDiff.objects.filter(
    type=OsmDiff.WAY
).filter(
    diff_id=diff_id
)
print(len(ways))

polys = [
    LineString(way.the_geom).buffer(0.01) for way in ways
]
multi_polys = cascaded_union(polys)

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
        print(f'Processed {i} of {feature_count} features\r', end='')
    if i == feature_count:
        print(f'Processed {i} of {feature_count} features\r', end='')
    i += 1

end_time = datetime.datetime.now()
print(f'\n\nExecution complete at:  {end_time}')
print(f'Execution run time:     {end_time-start_time}')
