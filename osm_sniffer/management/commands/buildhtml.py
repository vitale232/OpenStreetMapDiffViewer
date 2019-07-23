import datetime
import json
import os
import shutil
import subprocess
import time

from django.contrib.gis.db.models import Collect
from django.core.management.base import BaseCommand, CommandError
from django.core.serializers import serialize
from django.shortcuts import render
from django.template.loader import render_to_string

from osm_sniffer.models import OsmDiff, OsmDiffBuffer, MilepointRoute
import osm_sniffer.views as views


class Command(BaseCommand):
    help = 'Builds static HTML of an OSM diff_id'

    def add_arguments(self, parser):
        parser.add_argument('diff_id', nargs='+', type=int)
    
    def handle(self, *args, **options):
        today = datetime.date.today()
        start_time = datetime.datetime.now()

        if len(options['diff_id']) > 1:
            raise CommandError('Only process one diff_id. You provided %s' % len(options['diff_id']))
        diff_id = int(options['diff_id'][0])

        try:
            polygons = OsmDiffBuffer.objects.filter(
                diff_id=diff_id
            )
        except OsmDiffBuffer.DoesNotExist:
            raise CommandError('No OsmDiffBuffer objects for diff_id=%s' % diff_id)
        
        build_params = []
        links = []
        feature_count = len(polygons)
        i = 1
        for j, polygon in enumerate(polygons):
            try:
                routes = MilepointRoute.objects.filter(
                    the_geom__intersects=polygon.the_geom
                ).filter(
                    to_date__isnull=True
                )
            except MilePointRoute.DoesNotExist:
                raise CommandError('No MilepointRoute objects intersect the polygon')
            try:
                ways = OsmDiff.objects.filter(
                    type=OsmDiff.WAY
                ).filter(
                    diff_id=diff_id
                ).filter(
                    the_geom__intersects=polygon.the_geom
                )
            except OsmDiff.DoesNotExist:
                raise CommandError('No OsmDiff objects for diff_id=%s' % diff_id)

            map_context = {
                'document_title': f'OSM Diff {diff_id}:{j:03d} - {today}',
                'page_title': f'OSM Diff {diff_id}:{j:03d} | Processed {today}',
                'diff_id': diff_id,
                'map_x': polygon.the_geom.centroid.x,
                'map_y': polygon.the_geom.centroid.y,
                'milepoint_geojson': serialize('geojson', routes).replace(r'\"', "'"),
                'ways_geojson': serialize('geojson', ways).replace(r'\"', "'"),
                'data_dict': json.dumps(MilepointRoute.MILEPOINT_CHOICES),
            }
            output_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                '..',
                '..',
                '..',
                'dist',
                f'{today}_{diff_id}',
                'maps',
                'map_{j:03d}.html'.format(j=j)
            ))

            links.append(
                [
                    f'./map_{j:03d}.html',
                    f'Diff {diff_id}:{j:03d}'
                ]
            )
            build_params.append([map_context, 'osm_sniffer/map.html', output_path])
            self.stdout.write(f'Processed {i} of {feature_count} polygons.')
            i += 1

        for i, build_param in enumerate(build_params):
            try:
                previous_link = links[i-1][0]
            except IndexError:
                previous_link = None
            try:
                next_link = links[i+1][0]
            except IndexError:
                next_link = None
            build_param[0]['links'] = links
            build_param[0]['next_link'] = next_link
            build_param[0]['previous_link'] = previous_link

        build_count = len(build_params)
        i = 1
        for param in build_params:
            views.render_to_file(*param)
            self.stdout.write(f'Created {i} of {build_count} HTML files.')
            i += 1
        
        index_links = [[link[0].replace('./map_', './maps/map_'), link[1]] for link in links]
        index_context = map_context
        index_context['links'] = index_links
        index_context['page_title'] = f'OSM Diff {diff_id} Processed {today}'
        index_context['processing_date'] = str(today)
        index_context['explanation_image'] = os.path.abspath(os.path.join(
            os.path.dirname(build_param[-1]),
            '..',
            'static',
            'explanation_image.png'
        ))
        index_context['unbuilt_road'] = os.path.abspath(os.path.join(
            os.path.dirname(build_param[-1]),
            '..',
            'static',
            'unbuilt_road.png'
        ))
        if not os.path.isdir(os.path.dirname(index_context['explanation_image'])):
            os.makedirs(os.path.dirname(index_context['explanation_image']))
        index_filepath = os.path.abspath(os.path.join(
            os.path.dirname(build_param[-1]),
            '..',
            'index.html'
        ))

        views.render_to_file(index_context, 'osm_sniffer/index.html', index_filepath)

        favicon_filepath = os.path.abspath(os.path.join(
            os.path.dirname(index_filepath),
            '..',
            '..',
            'osm_sniffer',
            'static',
            'favicon.ico'
        ))
        explanation_image_filepath = os.path.abspath(os.path.join(
            os.path.dirname(favicon_filepath),
            'explanation_image.png'
        ))
        shutil.copyfile(
            favicon_filepath,
            os.path.join(os.path.dirname(index_filepath), 'static', 'favicon.ico')
        )
        shutil.copyfile(
            explanation_image_filepath,
            index_context['explanation_image']
        )
        shutil.copyfile(
            os.path.join(
                os.path.dirname(explanation_image_filepath),
                os.path.basename(index_context['unbuilt_road'])
            ),
            index_context['unbuilt_road']
        )
    
        end_time = datetime.datetime.now()
        self.stdout.write(self.style.SUCCESS(
            f'Processing completed in {end_time-start_time}\n' +
            f'Build folder: {os.path.dirname(index_filepath)}'
        ))
