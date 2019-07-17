import datetime
import gzip
import os
import subprocess
import sys

import requests


diff_id = sys.argv[-1]

download_flag = True

start_time = datetime.datetime.now()

print(f'\nExecuting script: {os.path.abspath(__file__)}')
print(f'Start time: {start_time}')

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

if download_flag:
    print(f'\nDownloading OSM Diff file from:\n {download_url}')
    print(f'\nSaving file to:\n {download_path}')

    response = requests.get(download_url, verify=False)

    if response.status_code == 200:
        with open(download_path, 'wb') as download:
            download.write(response.content)
    print('Download successful')

print(f'\nUnzipping downloaded gzip file:\n {download_path}')
with gzip.open(download_path, 'rb') as gzip_file:
    osc_contents = gzip_file.read()

osc_filepath = download_path[:-3]
with open(osc_filepath, 'w', encoding=sys.stdout.encoding) as osc_file:
    osc_file.write(osc_contents.decode(sys.stdout.encoding))

print(f'\nConverting .osc to .o5m')
o5m_path = os.path.join(
    os.path.dirname(download_path),
    os.path.basename(download_path).split('.')[0] + '.o5m'
)
convert_params = [
    r'D:\Program_Files\osmconvert\osmconvert64-0.8.8p.exe',
    download_path,
    f'-o={o5m_path}'
]
print(' Command: {}'.format(' '.join(convert_params)))
subprocess.call(convert_params)
print('Conversion successful')

print(f'\nFiltering on "highway" tag and saving as OSM file')
osm_path = o5m_path.replace('.o5m', '.osm')
filter_params = [
    r'D:\Program_Files\osmfilter\osmfilter.exe',
    o5m_path,
    '--keep=highway=',
    '--drop=highway=service highway=footway highway=pedestrian highway=path highway=track highway=steps',
    '-o={}'.format(osm_path),
    '--verbose'
]
print(' Command: {}'.format(' '.join(filter_params)))
subprocess.call(filter_params)
print('Filtering successful')

print(f'\nConverting OSM File to geoJSON')
geojson_path = osm_path.replace('.osm', '.geojson')
geojson_params = [
    'osmtogeojson',
    '-e',
    '-n',
    osm_path
]
print(' Command: {}'.format(' '.join(geojson_params)))
with open(geojson_path, 'w') as geojson_file:
    subprocess.call(geojson_params, stdout=geojson_file, stderr=geojson_file, shell=True)
print('Conversion successful')

end_time = datetime.datetime.now()
print(f'\nCompleted at: {end_time}')
print(f'Execution time: {end_time-start_time}')
