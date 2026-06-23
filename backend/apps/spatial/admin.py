from django.contrib.gis import admin

from .models import PointOfInterest, Zone


@admin.register(PointOfInterest)
class PointOfInterestAdmin(admin.GISModelAdmin):
    list_display = ["name", "category", "created_at"]
    list_filter = ["category"]
    search_fields = ["name", "description"]
    # Centre la carte de l'admin sur le Québec par défaut
    gis_widget_kwargs = {
        "attrs": {
            "default_lon": -73.5,
            "default_lat": 45.5,
            "default_zoom": 9,
        }
    }


@admin.register(Zone)
class ZoneAdmin(admin.GISModelAdmin):
    list_display = ["name", "zone_type", "area_m2", "created_at"]
    list_filter = ["zone_type"]
    readonly_fields = ["area_m2"]
    gis_widget_kwargs = {
        "attrs": {
            "default_lon": -73.5,
            "default_lat": 45.5,
            "default_zoom": 9,
        }
    }
