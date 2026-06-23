# Geo Stack — React + GeoDjango + PostGIS

Stack de référence pour une application géospatiale :

- **`frontend/`** — React + Vite + MapLibre GL (via `react-map-gl`)
- **`backend/`** — Django + GeoDjango + Django REST Framework + `djangorestframework-gis`
- **PostGIS** — base de données spatiale (PostgreSQL + extension PostGIS)
- **Docker Compose** — orchestre les 3 services

## Démarrage rapide

```bash
# 1. Copier les fichiers d'environnement
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 2. Lancer toute la stack
docker compose up --build

# 3. Dans un autre terminal : appliquer les migrations et créer un compte admin
docker compose exec backend python manage.py makemigrations spatial
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser

# 4. (optionnel) Générer des données de démonstration autour de Longueuil
docker compose exec backend python manage.py seed_demo_data --count 20
```

Services disponibles ensuite :

| Service   | URL                              |
|-----------|-----------------------------------|
| Frontend  | http://localhost:5173            |
| API DRF   | http://localhost:8000/api/v1/    |
| Admin     | http://localhost:8000/admin/     |
| PostGIS   | localhost:5432                   |

## Structure du projet

```
geo-stack/
├── docker-compose.yml
├── backend/
│   ├── config/             # settings, urls, wsgi
│   ├── apps/spatial/       # app GeoDjango : models, serializers, views, urls
│   │   ├── models.py       # PointOfInterest (PointField), Zone (PolygonField)
│   │   ├── serializers.py  # GeoFeatureModelSerializer -> GeoJSON natif
│   │   ├── views.py        # ViewSets DRF + filtres spatiaux (bbox, rayon)
│   │   └── management/commands/seed_demo_data.py
│   ├── requirements.txt
│   └── Dockerfile
└── frontend/
    ├── src/
    │   ├── api/             # client axios + fonctions d'appel API
    │   └── components/MapView.jsx   # carte MapLibre consommant le GeoJSON
    ├── package.json
    └── Dockerfile
```

## Points d'API disponibles

- `GET /api/v1/points/` — liste des points (GeoJSON FeatureCollection)
  - `?bbox=minx,miny,maxx,maxy` — filtre par zone visible sur la carte
  - `?lat=...&lng=...&radius_km=...` — filtre par rayon
  - `?category=...`
- `GET /api/v1/points/nearby/?lat=...&lng=...&radius_km=...` — triés par distance
- `POST /api/v1/points/` — créer un point (payload GeoJSON Feature)
- `GET /api/v1/zones/` — liste des zones polygonales
  - `?bbox=...` — zones qui intersectent la bbox
  - `?contains_lat=...&contains_lng=...` — zone(s) contenant ce point

## Notes importantes

- **Précision des surfaces** : le calcul d'aire dans `Zone.save()` utilise la
  projection Web Mercator (EPSG:3857) par défaut, qui déforme les surfaces.
  Pour des calculs précis au Québec, remplace par un SRID local comme
  **EPSG:32198** (NAD83 / Québec Lambert) ou l'UTM correspondant à ta zone.
- **Fond de carte** : le style MapLibre utilisé par défaut
  (`demotiles.maplibre.org`) est minimal et sert uniquement à la démo. Pour
  la prod, héberge ton propre style (ex: via MapTiler, Stadia Maps, ou un
  style.json self-hosted avec tes propres tuiles vectorielles).
- **CORS** : les origines autorisées sont définies dans `backend/.env`
  (`CORS_ALLOWED_ORIGINS`). Ajoute l'URL de prod du frontend avant déploiement.
- **Migrations** : la première migration (`makemigrations spatial`) n'est pas
  pré-générée volontairement, pour que les modèles restent faciles à adapter
  à ton domaine métier avant de figer le schéma.
