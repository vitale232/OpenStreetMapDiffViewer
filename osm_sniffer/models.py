from django.db import models
import django.contrib.gis.db.models as gis_models
from django.contrib.postgres.fields import HStoreField


class OsmDiffBuffer(models.Model):
    def __str__(self):
        return str(self.id)
    
    diff_id = models.IntegerField()
    created_date = models.DateField(auto_now_add=True)
    the_geom = gis_models.PolygonField()


class OsmDiff(models.Model):
    def __str__(self):
        return str(self.osm_id)
    
    diff_id = models.IntegerField()
    osm_id = models.BigIntegerField()
    tags = HStoreField()
    meta = HStoreField()
    tainted = models.BooleanField()

    WAY = 0
    NODE = 1
    RELATION = 3
    UNDEFINED = 10
    TYPE_CHOICES = (
        (WAY, 'Way'),
        (NODE, 'Node'),
        (RELATION, 'Relation'),
        (UNDEFINED, 'Undefined'),
    )
    type = models.IntegerField(choices=TYPE_CHOICES, default=UNDEFINED)

    created_date = models.DateField(auto_now_add=True)
    the_geom = gis_models.GeometryField(srid=4326)


class MilepointRoute(models.Model):
    def __str__(self):
        return self.route_id

    # NYSDOT Fields
    route_id = models.CharField(max_length=9, null=False)
    from_date = models.DateTimeField()
    to_date = models.DateTimeField(null=True)
    dot_id = models.CharField(max_length=6, blank=False)
    county_order = models.IntegerField()
    route_number = models.CharField(blank=True, max_length=3)
    route_suffix = models.CharField(max_length=4, blank=True)
    edited_date = models.DateTimeField(null=True)
    edited_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(null=True)
    created_by = models.CharField(max_length=100)
    global_id = models.CharField(max_length=100)
    conc_hierarchy = models.IntegerField()

    # srid=26918 indicates shapes will be stored in NAD83 UTM 18N
    # https://spatialreference.org/ref/epsg/nad83-utm-zone-18n/
    the_geom = gis_models.MultiLineStringField(srid=26918)

    # NYSDOT Fields with domains
    PRIMARY_DIRECTION_UNDIVIDED = 0
    PRIMARY_DIRECTION_DIVIDED = 1
    REVERSE_DIRECTION_INVENTORY = 2
    REVERSE_DIRECTION_NO_INVENTORY = 3
    DIRECTION_CHOICES = (
        (PRIMARY_DIRECTION_UNDIVIDED, '0 - Primary Direction with Undivided Inventory'),
        (PRIMARY_DIRECTION_DIVIDED, '1 - Primary Direction with Divided Inventory'),
        (REVERSE_DIRECTION_INVENTORY, '2 - Reverse Direction with Divided Inventory'),
        (REVERSE_DIRECTION_NO_INVENTORY, '3 - Reverse Direction with No Inventory')
    )
    direction = models.IntegerField(choices=DIRECTION_CHOICES)

    INTERSTATE_SIGNING = 0
    US_SIGNING = 1
    NY_SIGNING = 2
    SIGNING_CHOICES = (
        (INTERSTATE_SIGNING, 'I'), (US_SIGNING, 'US'), (NY_SIGNING, 'NY'),
    )
    roadway_signing = models.IntegerField(choices=SIGNING_CHOICES, null=True)

    ROAD = 1
    RAMP = 2
    ROUTE = 3
    NON_MAINLINE = 5
    ROADWAY_TYPE_CHOICES = (
        (ROAD, 'Road'), (RAMP, 'Ramp'),
        (ROUTE, 'Route'), (NON_MAINLINE, 'Non-Mainline'),
    )
    roadway_type = models.IntegerField(choices=ROADWAY_TYPE_CHOICES, default=ROAD)

    ALBANY = 1
    ALLEGANY = 2
    BRONX = 3
    BROOME = 4
    CATTARAUGUS = 5
    CAYUGA = 6
    CHAUTAUQUA = 7
    CHEMUNG = 8
    CHENANGO = 9
    CLINTON = 10
    COLUMBIA = 11
    CORTLAND = 12
    DELAWARE = 13
    DUTCHESS = 14
    ERIE = 15
    ESSEX = 16
    FRANKLIN = 17
    FULTON = 18
    GENESEE = 19
    GREENE = 20
    HAMILTON = 21
    HERKIMER = 22
    JEFFERSON = 23
    KINGS = 24
    LEWIS = 25
    LIVINGSTON = 26
    MADISON = 27
    MONROE = 28
    MONTGOMERY = 29
    NASSAU = 30
    NEW_YORK = 31
    NIAGARA = 32
    ONEIDA = 33
    ONONDAGA = 34
    ONTARIO = 35
    ORANGE = 36
    ORLEANS = 37
    OSWEGO = 38
    OTSEGO = 39
    PUTNAM = 40
    QUEENS = 41
    RENSSELAER = 42
    RICHMOND = 43
    ROCKLAND = 44
    ST_LAWRENCE = 45
    SARATOGA = 46
    SCHENECTADY = 47
    SCHOHARIE = 48
    SCHUYLER = 49
    SENECA = 50
    STEUBEN = 51
    SUFFOLK = 52
    SULLIVAN = 53
    TIOGA = 54
    TOMPKINS = 55
    ULSTER = 56
    WARREN = 57
    WASHINGTON = 58
    WAYNE = 59
    WESTCHESTER = 60
    WYOMING = 61
    YATES = 62
    COUNTY_CHOICES = (
        (ALBANY, 'Albany'), (ALLEGANY, 'Allegany'), (BRONX, 'Bronx'),
        (BROOME, 'Broome'), (CATTARAUGUS, 'Cattaraugus'), (CAYUGA, 'Cayuga'),
        (CHAUTAUQUA, 'Chautauqua'), (CHEMUNG, 'Chemung'), (CHENANGO, 'Chenango'),
        (CLINTON, 'Clinton'), (COLUMBIA, 'Columbia'), (CORTLAND, 'Cortland'),
        (DELAWARE, 'Delaware'), (DUTCHESS, 'Dutchess'), (ERIE, 'Erie'),
        (ESSEX, 'Essex'), (FRANKLIN, 'Franklin'), (FULTON, 'Fulton'),
        (GENESEE, 'Genesee'), (GREENE, 'Greene'), (HAMILTON, 'Hamilton'),
        (HERKIMER, 'Herkimer'), (JEFFERSON, 'Jefferson'), (KINGS, 'Kings'),
        (LEWIS, 'Lewis'), (LIVINGSTON, 'Livingston'), (MADISON, 'Madison'),
        (MONROE, 'Monroe'), (MONTGOMERY, 'Montgomery'), (NASSAU, 'Nassau'),
        (NEW_YORK, 'New York'), (NIAGARA, 'Niagara'), (ONEIDA, 'Oneida'),
        (ONONDAGA, 'Onondaga'), (ONTARIO, 'Ontario'), (ORANGE, 'Orange'),
        (ORLEANS, 'Orleans'), (OSWEGO, 'Oswego'), (OTSEGO, 'Otsego'),
        (PUTNAM, 'Putnam'), (QUEENS, 'Queens'), (RENSSELAER, 'Rensselaer'),
        (RICHMOND, 'Richmond'), (ROCKLAND, 'Rockland'), (ST_LAWRENCE, 'St Lawrence'),
        (SARATOGA, 'Saratoga'), (SCHENECTADY, 'Schenectady'), (SCHOHARIE, 'Schoharie'),
        (SCHUYLER, 'Schuyler'), (SENECA, 'Seneca'), (STEUBEN, 'Steuben'),
        (SUFFOLK, 'Suffolk'), (SULLIVAN, 'Sullivan'), (TIOGA, 'Tioga'),
        (TOMPKINS, 'Tompkins'), (ULSTER, 'Ulster'), (WARREN, 'Warren'),
        (WASHINGTON, 'Washington'), (WAYNE, 'Wayne'), (WESTCHESTER, 'Westchester'),
        (WYOMING, 'Wyoming'), (YATES, 'Yates'),
    )
    county = models.IntegerField(choices=COUNTY_CHOICES)

    ALTERNATE = 1
    BUSINESS_ROUTE = 2
    BYPASS = 3
    SPUR = 4
    LOOP = 5
    PROPOSED = 6
    TEMPORARY = 7
    TRUCK_ROUTE = 8
    NONE_OF_THE_ABOVE = 9
    NO_QUALIFIER = 10
    ROUTE_QUALIFIER_CHOICES = (
        (ALTERNATE, 'Alternate'), (BUSINESS_ROUTE, 'Business Route'),
        (BYPASS, 'Bypass'), (SPUR, 'Spur'), (LOOP, 'Loop'),
        (PROPOSED, 'Proposed'), (TEMPORARY, 'Temporary'),
        (TRUCK_ROUTE, 'Truck Route'), (NONE_OF_THE_ABOVE, 'None of the Above'),
        (NO_QUALIFIER, 'No Qualifier'),
    )
    route_qualifier = models.IntegerField(choices=ROUTE_QUALIFIER_CHOICES, default=NO_QUALIFIER)

    WELCOME_CENTER = 1
    REST_AREA = 2
    PARKING_AREA = 3
    SCENIC_AREA = 4
    SLIP_RAMP = 5
    ROUNDABOUT = 6
    NONE = None
    ROADWAY_FEATURE_CHOICES = (
        (WELCOME_CENTER, 'Welcome Center'), (REST_AREA, 'Rest Area (With Restrooms)'),
        (PARKING_AREA, 'Parking Area (Without Restrooms'), (SCENIC_AREA, 'Scenic Area'),
        (SLIP_RAMP, 'Slip Ramp'), (ROUNDABOUT, 'Roundabout'), (NONE, 'None'),
    )
    roadway_feature = models.IntegerField(choices=ROADWAY_FEATURE_CHOICES, null=True)

    PARKWAY = 'Yes'
    NO_PARKWAY = 'No'
    PARKWAY_CHOICES = (
        (PARKWAY, 'Parkway'),
        (NO_PARKWAY, 'Not a Parkway'),
    )
    parkway_flag = models.CharField(choices=PARKWAY_CHOICES, default=NO_PARKWAY, max_length=3)

    # Django Model specific fields
    model_created_date = models.DateTimeField(auto_now_add=True)
    model_edited_date = models.DateTimeField(auto_now=True)

    def shape_length(self):
        return self.the_geom.length
