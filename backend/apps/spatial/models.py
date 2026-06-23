"""
Modèles spatiaux GeoDjango.

Deux exemples sont fournis :
- PointOfInterest : géométrie ponctuelle (PointField)
- Zone : géométrie polygonale (PolygonField), avec calcul d'aire

Adapte/renomme selon ton domaine métier (parcelles, capteurs, relevés, etc.)
"""

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point


class PointOfInterest(models.Model):
    """Exemple de modèle ponctuel : un point d'intérêt géolocalisé."""

    name = models.CharField("nom", max_length=255)
    description = models.TextField("description", blank=True)
    category = models.CharField("catégorie", max_length=100, blank=True)
    location = models.PointField("localisation", srid=4326, geography=True)
    created_at = models.DateTimeField("créé le", auto_now_add=True)
    updated_at = models.DateTimeField("mis à jour le", auto_now=True)

    class Meta:
        verbose_name = "point d'intérêt"
        verbose_name_plural = "points d'intérêt"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return self.name


class Zone(models.Model):
    """Exemple de modèle surfacique : une zone (parcelle, secteur, etc.)."""

    name = models.CharField("nom", max_length=255)
    zone_type = models.CharField("type de zone", max_length=100, blank=True)
    geom = models.PolygonField("géométrie", srid=4326)
    area_m2 = models.FloatField("aire (m²)", null=True, blank=True, editable=False)
    created_at = models.DateTimeField("créé le", auto_now_add=True)

    class Meta:
        verbose_name = "zone"
        verbose_name_plural = "zones"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        # Calcul automatique de l'aire en transformant en projection métrique (3857)
        # avant de sauvegarder. Pour une précision optimale au Québec, utilise
        # plutôt un SRID local type MTM ou UTM (ex: EPSG:32198 / NAD83 Québec Lambert).
        if self.geom:
            geom_transformed = self.geom.transform(3857, clone=True)
            self.area_m2 = geom_transformed.area
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
