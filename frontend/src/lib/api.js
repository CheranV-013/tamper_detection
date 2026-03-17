const rawBase =
  import.meta.env.VITE_API_BASE?.trim() ||
  "https://tamper-detection-2.onrender.com";

const BASE_URL = rawBase.replace(/\/+$/, "");

export const API_BASE = `${BASE_URL}/api`;

/*
Safe GET request
Handles:
- network errors
- backend sleep (Render free tier)
- invalid responses
*/
export async function safeFetch(path, fallback = null) {
  const url = path.startsWith("http") ? path : `${API_BASE}${path}`;

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 45000);

    const res = await fetch(url, {
      signal: controller.signal
    });

    clearTimeout(timeout);

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    return await res.json();
  } catch (err) {
    console.error("API error:", url, err);
    return fallback;
  }
}

/*
POST request helper
*/
export async function postJson(path, payload = {}) {
  const url = `${API_BASE}${path}`;

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    return await res.json();
  } catch (err) {
    console.error("POST error:", url, err);
    throw err;
  }
}

/*
API wrappers
*/

export const getSummary = () =>
  safeFetch("/summary", {
    total_logs: 0,
    total_iot: 0,
    anomalies: 0,
    active_alerts: 0
  });

export const getLogs = (limit = 12) =>
  safeFetch(`/logs?limit=${limit}`, []);

export const getIoT = (limit = 12) =>
  safeFetch(`/iot?limit=${limit}`, []);

export const getAnomalies = (limit = 5) =>
  safeFetch(`/anomalies?limit=${limit}`, []);

export const getAlerts = () =>
  safeFetch("/alerts", []);

export const getSystemStatus = () =>
  safeFetch("/system-status", {});

export const getActivityChart = () =>
  safeFetch("/charts/activity", []);

export const getIoTChart = () =>
  safeFetch("/charts/iot", []);

export const getTamperChart = () =>
  safeFetch("/charts/tamper", []);

export const getAccessHourChart = () =>
  safeFetch("/charts/access-hour", []);

export const getAccessTopIps = () =>
  safeFetch("/charts/access-top-ips", []);

export const getAccessSuspicious = () =>
  safeFetch("/charts/access-suspicious", []);

export const getAccessLocations = () =>
  safeFetch("/charts/access-locations", []);

export const generateData = (logs = 20, iot = 20) =>
  postJson("/generate", { logs, iot });
