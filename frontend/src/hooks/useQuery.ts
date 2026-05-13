import { useState } from "react";
import axios from "axios";
import { useAppStore } from "../store";

// ✅ This reads NEXT_PUBLIC_API_URL from Vercel env vars
// Falls back to localhost for local development
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000, // 30s — important for Render free tier cold starts
});

export function useQuery() {
  const [loading, setLoading] = useState(false);
  const { setMetrics, addToHistory } = useAppStore();

  const submitQuery = async (query: string) => {
    setLoading(true);
    try {
      const res = await api.post("/api/query", { query });
      addToHistory(res.data);
      return res.data;
    } catch (err: any) {
      const message =
        err.response?.data?.detail ||
        err.message ||
        "Request failed";
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  const loadMetrics = async () => {
    try {
      const res = await api.get("/api/metrics");
      setMetrics(res.data);
    } catch (err) {
      console.error("Failed to load metrics:", err);
    }
  };

  const simulateAttack = async (attackType: string, query: string) => {
    setLoading(true);
    try {
      const res = await api.post("/api/attacks/simulate", {
        attack_type: attackType,
        query,
      });
      addToHistory(res.data);
      return res.data;
    } catch (err: any) {
      const message =
        err.response?.data?.detail ||
        err.message ||
        "Attack simulation failed";
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  return { submitQuery, loadMetrics, simulateAttack, loading };
}