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

from django.contrib.gis.gdal import DataSource, OGRGeometry
from django.utils.timezone import make_aware

from osm_sniffer.models import MilepointRoute


start_time = datetime.datetime.now()
print(f'\nExecuting script:   {os.path.abspath(__file__)}')
print(f'Execution start at: {start_time}')

model_layer_mapping = {
    'route_id': 'ROUTE_ID',
    'from_date': 'FROM_DATE',
    'to_date': 'TO_DATE',
    'dot_id': 'DOT_ID',
    'county_order': 'COUNTY_ORDER',
    'route_number': 'ROUTE_NUMBER',
    'route_suffix': 'ROUTE_SUFFIX',
    'edited_date': 'EDITED_DATE',
    'edited_by': 'EDITED_BY',
    'created_date': 'CREATED_DATE',
    'created_by': 'CREATED_BY',
    'global_id': 'GLOBALID',
    'conc_hierarchy': 'CONC_HIERARCHY',
    'direction': 'DIRECTION',
    'roadway_signing': 'SIGNING',
    'roadway_type': 'ROADWAY_TYPE',
    'county': 'COUNTY',
    'route_qualifier': 'ROUTE_QUALIFIER',
    'roadway_feature': 'ROADWAY_FEATURE',
    'parkway_flag': 'PARKWAY_FLAG',
}
# milepoint_layer_mapping = dict(
#     (value, key) for key, value in model_layer_mapping.items()
# )

geojson_path = r'D:\OpenStreetMap\Milepoint\milepoint.geojson'
geojson_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    'Milepoint',
    'milepoint.geojson'
))

print(f'\nReading input data from the following file:\n {geojson_path}\n')
data_source = DataSource(geojson_path)
layer = data_source[0]

feature_count = len(layer)
i = 0
for feature in layer:
    try:
        feature_data = {
            key: feature.get(value) for (key, value) in model_layer_mapping.items()
        }

        # Use OGRGeometry to strip z-values from polyline vertices
        geometry = OGRGeometry(feature.geom.ewkt)
        geometry.coord_dim = 2
        feature_data['the_geom'] = geometry.ewkt

        # Convert parkway_flag from NYSDOT domain to osm_sniffer domain
        if feature_data['parkway_flag'] == 'Y':
            feature_data['parkway_flag'] = MilepointRoute.PARKWAY
        else:
            feature_data['parkway_flag'] = MilepointRoute.NO_PARKWAY
        
        # Add osm_diff.settings.TIME_ZONE stamp to from/to dates

        if feature_data['from_date']:
            feature_data['from_date'] = make_aware(feature_data['from_date'])
        else:
            print(f'\n\nNO FROM_DATE: Failed on feautre {i} of {feature_count}')
            print(feature_data)
            print('')
            continue
        if feature_data['to_date']:
            feature_data['to_date'] = make_aware(feature_data['to_date'])
        if feature_data['edited_date']:
            feature_data['edited_date'] = make_aware(feature_data['edited_date'])
        if feature_data['created_date']:
            feature_data['created_date'] = make_aware(feature_data['created_date'])

        route = MilepointRoute(**feature_data)
        route.save()

        if i % 100 == 0:
            print(f'Processed {i} of {feature_count} features\r', end='')
        if i == feature_count:
            print(f'Processed {i} of {feature_count} features\r', end='')
        i += 1
    except:
        print(f'\n\nFailed on feautre {i} of {feature_count}')
        print(feature_data)
        print('')

end_time = datetime.datetime.now()
print(f'\n\nExecution complete at:  {end_time}')
print(f'Execution run time:     {end_time-start_time}')
