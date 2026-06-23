"""
Commande utilitaire : python manage.py seed_demo_data

Génère quelques points et zones de démonstration autour de la région de
Montréal/Longueuil pour pouvoir tester rapidement la carte React.
"""

import random

from django.contrib.gis.geos import Point, Polygon
from django.core.management.base import BaseCommand

from apps.spatial.models import PointOfInterest, Zone

CENTER_LAT, CENTER_LNG = 45.5312, -73.5183  # Longueuil, QC


class Command(BaseCommand):
    help = "Génère des données géospatiales de démonstration (région de Longueuil/Montréal)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", type=int, default=15, help="Nombre de points à créer."
        )

    def handle(self, *args, **options):
        count = options["count"]
        categories = ["station", "capteur", "site_relevé", "point_controle"]

        created_points = 0
        for i in range(count):
            lat = CENTER_LAT + random.uniform(-0.05, 0.05)
            lng = CENTER_LNG + random.uniform(-0.05, 0.05)
            PointOfInterest.objects.create(
                name=f"Point démo {i + 1}",
                description="Généré automatiquement par seed_demo_data.",
                category=random.choice(categories),
                location=Point(lng, lat, srid=4326),
            )
            created_points += 1

        # Une zone polygonale simple englobant la zone de démo
        bbox_zone = Polygon.from_bbox(
            (CENTER_LNG - 0.06, CENTER_LAT - 0.06, CENTER_LNG + 0.06, CENTER_LAT + 0.06)
        )
        bbox_zone.srid = 4326
        Zone.objects.create(
            name="Zone de démonstration - Longueuil",
            zone_type="démo",
            geom=bbox_zone,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"{created_points} points et 1 zone créés autour de Longueuil."
            )
        )
