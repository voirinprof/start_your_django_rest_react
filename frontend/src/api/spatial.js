import { apiClient } from "./client";

/**
 * Récupère les points d'intérêt, en FeatureCollection GeoJSON.
 * @param {Object} params - paramètres de requête optionnels (bbox, category, etc.)
 */
export async function fetchPoints(params = {}) {
  const { data } = await apiClient.get("/points/", { params });
  return data;
}

export async function fetchZones(params = {}) {
  const { data } = await apiClient.get("/zones/", { params });
  return data;
}

export async function createPoint(payload) {
  // payload attendu : { type: "Feature", geometry: {...}, properties: {...} }
  const { data } = await apiClient.post("/points/", payload);
  return data;
}

export async function fetchNearbyPoints(lat, lng, radiusKm = 5) {
  const { data } = await apiClient.get("/points/nearby/", {
    params: { lat, lng, radius_km: radiusKm },
  });
  return data;
}
