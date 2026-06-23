"""
ViewSets DRF avec opérations spatiales courantes :
- filtrage par rayon (distance) autour d'un point
- filtrage par bbox (bounding box), utile pour ne charger que les
  entités visibles dans le viewport de la carte React
"""

from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.measure import D  # Distance
from django.contrib.gis.db.models.functions import Distance
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import PointOfInterest, Zone
from .serializers import PointOfInterestSerializer, ZoneSerializer


def parse_bbox(bbox_str):
    """
    Convertit une chaîne 'minx,miny,maxx,maxy' (format standard envoyé par
    les libs cartographiques JS) en objet Polygon GEOS.
    """
    try:
        minx, miny, maxx, maxy = map(float, bbox_str.split(","))
    except (ValueError, AttributeError):
        return None
    return Polygon.from_bbox((minx, miny, maxx, maxy))


class PointOfInterestViewSet(viewsets.ModelViewSet):
    """
    CRUD complet sur les points d'intérêt + filtrage spatial.

    Query params supportés :
    - ?bbox=minx,miny,maxx,maxy  -> ne retourne que les points dans la bbox
    - ?lat=...&lng=...&radius_km=...  -> points dans un rayon donné
    - ?category=...  -> filtre exact sur la catégorie
    """

    queryset = PointOfInterest.objects.all()
    serializer_class = PointOfInterestSerializer
    filterset_fields = ["category"]

    def get_queryset(self):
        qs = super().get_queryset()
        bbox_param = self.request.query_params.get("bbox")
        if bbox_param:
            bbox = parse_bbox(bbox_param)
            if bbox is not None:
                qs = qs.filter(location__within=bbox)

        lat = self.request.query_params.get("lat")
        lng = self.request.query_params.get("lng")
        radius_km = self.request.query_params.get("radius_km")
        if lat and lng and radius_km:
            center = Point(float(lng), float(lat), srid=4326)
            qs = qs.filter(location__distance_lte=(center, D(km=float(radius_km))))

        return qs

    @action(detail=False, methods=["get"])
    def nearby(self, request):
        """
        Endpoint dédié : /api/v1/points/nearby/?lat=45.5&lng=-73.5&radius_km=5
        Retourne les points triés par distance croissante.
        """
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        radius_km = request.query_params.get("radius_km", 10)

        if not (lat and lng):
            return Response({"detail": "lat et lng sont requis."}, status=400)

        center = Point(float(lng), float(lat), srid=4326)
        qs = (
            PointOfInterest.objects.filter(
                location__distance_lte=(center, D(km=float(radius_km)))
            )
            .annotate(distance=Distance("location", center))
            .order_by("distance")
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class ZoneViewSet(viewsets.ModelViewSet):
    """
    CRUD sur les zones polygonales + filtrage par intersection spatiale.

    Query params supportés :
    - ?bbox=minx,miny,maxx,maxy  -> zones qui intersectent la bbox
    - ?contains_lat=...&contains_lng=...  -> zone(s) contenant ce point
    """

    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    filterset_fields = ["zone_type"]

    def get_queryset(self):
        qs = super().get_queryset()
        bbox_param = self.request.query_params.get("bbox")
        if bbox_param:
            bbox = parse_bbox(bbox_param)
            if bbox is not None:
                qs = qs.filter(geom__intersects=bbox)

        lat = self.request.query_params.get("contains_lat")
        lng = self.request.query_params.get("contains_lng")
        if lat and lng:
            point = Point(float(lng), float(lat), srid=4326)
            qs = qs.filter(geom__contains=point)

        return qs
