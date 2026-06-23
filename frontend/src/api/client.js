import axios from "axios";

// L'URL de base est injectée par Vite via les variables d'env (préfixe VITE_)
const baseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});
