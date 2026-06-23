"""
Serializers DRF avec support GeoJSON via djangorestframework-gis.

GeoFeatureModelSerializer produit directement des FeatureCollection GeoJSON,
ce qui est le format attendu nativement par MapLibre GL / Leaflet côté React.
"""

from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers

from .models import PointOfInterest, Zone


class PointOfInterestSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = PointOfInterest
        geo_field = "location"
        fields = [
            "id",
            "name",
            "description",
            "category",
            "created_at",
            "updated_at",
        ]


class ZoneSerializer(GeoFeatureModelSerializer):
    area_m2 = serializers.FloatField(read_only=True)

    class Meta:
        model = Zone
        geo_field = "geom"
        fields = [
            "id",
            "name",
            "zone_type",
            "area_m2",
            "created_at",
        ]
