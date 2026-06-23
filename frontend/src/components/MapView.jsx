import { useEffect, useState, useCallback } from "react";
import Map, { Source, Layer, Popup, NavigationControl } from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";

import { fetchPoints, fetchZones } from "../api/spatial";

// Style de fond gratuit, sans clé API (tuiles vectorielles OSM via demotiles / MapTiler démo)
// En production, remplace par ton propre style (MapTiler, Stadia Maps, ou un style.json self-hosted).
const MAP_STYLE = "https://demotiles.maplibre.org/style.json";

const INITIAL_VIEW_STATE = {
  longitude: -73.5183,
  latitude: 45.5312, // Longueuil, QC
  zoom: 10,
};

const pointLayerStyle = {
  id: "points-layer",
  type: "circle",
  paint: {
    "circle-radius": 6,
    "circle-color": "#2563eb",
    "circle-stroke-width": 1.5,
    "circle-stroke-color": "#ffffff",
  },
};

const zoneFillLayerStyle = {
  id: "zones-fill-layer",
  type: "fill",
  paint: {
    "fill-color": "#16a34a",
    "fill-opacity": 0.15,
  },
};

const zoneLineLayerStyle = {
  id: "zones-line-layer",
  type: "line",
  paint: {
    "line-color": "#16a34a",
    "line-width": 2,
  },
};

export default function MapView() {
  const [pointsGeoJSON, setPointsGeoJSON] = useState(null);
  const [zonesGeoJSON, setZonesGeoJSON] = useState(null);
  const [selectedFeature, setSelectedFeature] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [points, zones] = await Promise.all([fetchPoints(), fetchZones()]);
      setPointsGeoJSON(points);
      setZonesGeoJSON(zones);
    } catch (err) {
      console.error(err);
      setError(
        "Impossible de charger les données depuis l'API. Vérifie que le backend tourne bien."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleMapClick = (event) => {
    const feature = event.features && event.features[0];
    if (feature) {
      setSelectedFeature({
        longitude: event.lngLat.lng,
        latitude: event.lngLat.lat,
        properties: feature.properties,
      });
    } else {
      setSelectedFeature(null);
    }
  };

  return (
    <div style={{ position: "relative", width: "100%", height: "100vh" }}>
      {loading && <StatusBanner text="Chargement des données géospatiales..." />}
      {error && <StatusBanner text={error} isError />}

      <Map
        initialViewState={INITIAL_VIEW_STATE}
        mapStyle={MAP_STYLE}
        interactiveLayerIds={["points-layer", "zones-fill-layer"]}
        onClick={handleMapClick}
        style={{ width: "100%", height: "100%" }}
      >
        <NavigationControl position="top-right" />

        {zonesGeoJSON && (
          <Source id="zones-source" type="geojson" data={zonesGeoJSON}>
            <Layer {...zoneFillLayerStyle} />
            <Layer {...zoneLineLayerStyle} />
          </Source>
        )}

        {pointsGeoJSON && (
          <Source id="points-source" type="geojson" data={pointsGeoJSON}>
            <Layer {...pointLayerStyle} />
          </Source>
        )}

        {selectedFeature && (
          <Popup
            longitude={selectedFeature.longitude}
            latitude={selectedFeature.latitude}
            onClose={() => setSelectedFeature(null)}
            closeOnClick={false}
          >
            <FeaturePopupContent properties={selectedFeature.properties} />
          </Popup>
        )}
      </Map>
    </div>
  );
}

function FeaturePopupContent({ properties }) {
  if (!properties) return null;
  return (
    <div style={{ fontSize: "0.85rem" }}>
      {properties.name && <strong>{properties.name}</strong>}
      {properties.description && <p style={{ margin: "4px 0" }}>{properties.description}</p>}
      {properties.category && <div>Catégorie : {properties.category}</div>}
      {properties.area_m2 && <div>Aire : {Math.round(properties.area_m2)} m²</div>}
    </div>
  );
}

function StatusBanner({ text, isError }) {
  return (
    <div
      style={{
        position: "absolute",
        top: 10,
        left: "50%",
        transform: "translateX(-50%)",
        zIndex: 10,
        padding: "8px 16px",
        borderRadius: 6,
        background: isError ? "#fee2e2" : "#dbeafe",
        color: isError ? "#991b1b" : "#1e3a8a",
        fontSize: "0.85rem",
        boxShadow: "0 1px 3px rgba(0,0,0,0.15)",
      }}
    >
      {text}
    </div>
  );
}
