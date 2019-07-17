import datetime
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
        diff_id = options['diff_id'][0]

        build_params = []
        links = []
        try:
            polygons = OsmDiffBuffer.objects.filter(
                diff_id=diff_id
            )
        except OsmDiffBuffer.DoesNotExist:
            raise CommandError('No OsmDiffBuffer objects for diff_id=%s' % diff_id)
        
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
                    the_geom__intersects=polygon.the_geom
                )
            except OsmDiff.DoesNotExist:
                raise CommandError('No OsmDiff objects for diff_id=%s' % diff_id)
            map_context = {
                'document_title': f'OSM Diff {diff_id} - {today}',
                'page_title': f'OSM Diff {diff_id}:{j} Processed {today}',
                'diff_id': diff_id,
                'map_x': polygon.the_geom.centroid.x,
                'map_y': polygon.the_geom.centroid.y,
                'milepoint_geojson': serialize('geojson', routes).replace(r'\"', "'"),
                'ways_geojson': serialize('geojson', ways).replace(r'\"', "'"),
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
                    './map_{j:03d}.html'.format(j=j),
                    'Diff {diff_id}:{j:03d}'.format(diff_id=diff_id, j=j)
                ]
            )
            build_params.append([map_context, 'osm_sniffer/map.html', output_path])
            self.stdout.write(f'Processed {i} of {feature_count} polygons.')
            i += 1

        for build_param in build_params:
            build_param[0]['links'] = links

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
        index_filepath = os.path.abspath(os.path.join(
            os.path.dirname(build_param[-1]),
            '..',
            'index.html'
        ))
        # self.stdout.write(index_context)
        # self.stdout.write(index_filepath)
        views.render_to_file(index_context, 'osm_sniffer/index.html', index_filepath)

        favicon_filepath = os.path.abspath(os.path.join(
            os.path.dirname(index_filepath),
            '..',
            '..',
            'osm_sniffer',
            'static',
            'favicon.ico'
        ))
        shutil.copyfile(
            favicon_filepath,
            os.path.join(os.path.dirname(index_filepath), 'favicon.ico')
        )
    
        end_time = datetime.datetime.now()
        self.stdout.write(self.style.SUCCESS(
            f'Processing completed in {end_time-start_time}\n' +
            f'Build folder: {os.path.dirname(index_filepath)}'
        ))
    # def render_to_file(self, context, template, filepath):
    #     diff_id = context['diff_id']
    #     html_string = render_to_string(template, context=context)

    #     if not os.path.isdir(os.path.dirname(filepath)):
    #         os.makedirs(os.path.dirname(filepath))

    #     with open(filepath, 'w') as file_:
    #         file_.write(html_string)
        
    #     return True