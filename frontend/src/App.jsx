import React, { useEffect, useState } from "react";
import { io } from "socket.io-client";
import { ShieldCheck, Activity, AlertTriangle, Cpu } from "lucide-react";
import SummaryCards from "./components/SummaryCards.jsx";
import AlertPanel from "./alerts/AlertPanel.jsx";
import LiveEventStream from "./alerts/LiveEventStream.jsx";
import ThreatMonitor from "./alerts/ThreatMonitor.jsx";
import ActivityChart from "./charts/ActivityChart.jsx";
import IoTChart from "./charts/IoTChart.jsx";
import TamperChart from "./charts/TamperChart.jsx";
import AccessHourChart from "./charts/AccessHourChart.jsx";
import TopIpChart from "./charts/TopIpChart.jsx";
import SuspiciousAccessChart from "./charts/SuspiciousAccessChart.jsx";
import StatusPanel from "./components/StatusPanel.jsx";
import GeoDistribution from "./components/GeoDistribution.jsx";
import LogsTable from "./tables/LogsTable.jsx";
import IoTTable from "./tables/IoTTable.jsx";
import AccessLogsTable from "./tables/AccessLogsTable.jsx";
import AnomalyExplanation from "./components/AnomalyExplanation.jsx";

const BASE_URL =
  import.meta.env.VITE_API_URL || "https://tamper-detection-2.onrender.com";

const API_BASE = `${BASE_URL}/api`;
const SOCKET_URL = BASE_URL;
/* SAFE FETCH HELPER */
const safeFetch = async (url) => {
  try {
    const res = await fetch(url);
    return await res.json();
  } catch (err) {
    console.error("API error:", url, err);
    return [];
  }
};

export default function App() {
  const [summary, setSummary] = useState({
    total_logs: 0,
    total_iot: 0,
    anomalies: 0,
    active_alerts: 0,
    connected_users: 0,
    access_total: 0
  });

  const [alerts, setAlerts] = useState([]);
  const [logs, setLogs] = useState([]);
  const [iot, setIot] = useState([]);
  const [activity, setActivity] = useState([]);
  const [iotChart, setIotChart] = useState([]);
  const [tamperChart, setTamperChart] = useState([]);
  const [status, setStatus] = useState({});
  const [anomalies, setAnomalies] = useState([]);
  const [securityEvents, setSecurityEvents] = useState([]);
  const [userCount, setUserCount] = useState(0);
  const [accessLogs, setAccessLogs] = useState([]);
  const [accessHour, setAccessHour] = useState([]);
  const [topIps, setTopIps] = useState([]);
  const [accessSuspicious, setAccessSuspicious] = useState([]);
  const [locations, setLocations] = useState([]);

  const fetchAll = async () => {
    console.log("Fetching from:", API_BASE);

    const [
      s, a, l, i,
      ac, ic, tc,
      st, an,
      al, ah,
      ti, as, loc
    ] = await Promise.all([
      safeFetch(`${API_BASE}/summary`),
      safeFetch(`${API_BASE}/alerts`),
      safeFetch(`${API_BASE}/logs?limit=12`),
      safeFetch(`${API_BASE}/iot?limit=12`),
      safeFetch(`${API_BASE}/charts/activity`),
      safeFetch(`${API_BASE}/charts/iot`),
      safeFetch(`${API_BASE}/charts/tamper`),
      safeFetch(`${API_BASE}/system-status`),
      safeFetch(`${API_BASE}/anomalies?limit=5`),
      safeFetch(`${API_BASE}/access-logs?limit=10`),
      safeFetch(`${API_BASE}/charts/access-hour`),
      safeFetch(`${API_BASE}/charts/access-top-ips`),
      safeFetch(`${API_BASE}/charts/access-suspicious`),
      safeFetch(`${API_BASE}/charts/access-locations`)
    ]);

    setSummary(s || {});
    setAlerts(a || []);
    setLogs(l || []);
    setIot(i || []);
    setActivity(ac || []);
    setIotChart(ic || []);
    setTamperChart(tc || []);
    setStatus(st || {});
    setAnomalies(an || []);
    setAccessLogs(al || []);
    setAccessHour(ah || []);
    setTopIps(ti || []);
    setAccessSuspicious(as || []);
    setLocations(loc || []);
    setUserCount(s?.connected_users || 0);
  };

  const generateData = async () => {
    try {
      await fetch(`${API_BASE}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ logs: 25, iot: 25 })
      });
    } catch (err) {
      console.error("Generate error:", err);
    }
  };

  useEffect(() => {
    fetchAll();

    fetch(`${API_BASE}/dashboard-access`).catch(() => {});

    const socket = io(SOCKET_URL, {
      transports: ["websocket"]
    });

    socket.on("connect", () => {
      console.log("Socket connected");
    });

    socket.on("security_event", event => {
      setSecurityEvents(prev => [event, ...prev].slice(0, 30));
      fetchAll();
    });

    socket.on("user_count", data => {
      setUserCount(data.count || 0);
    });

    return () => socket.disconnect();
  }, []);

  const threatEvents = securityEvents.filter(ev =>
    ["ACCESS_DETECTED", "SUSPICIOUS_ACCESS"].includes(ev.type)
  );

  return (
    <div className="min-h-screen text-slate-100">
      <header className="px-8 py-6 flex items-center justify-between border-b border-slate-800/60">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-accent/15 text-accent shadow-glow">
            <ShieldCheck />
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">
              AI Powered Container Tamper Detection SOC Dashboard
            </h1>
            <p className="text-slate-400 text-sm">
              SOC Dashboard • Real-time anomaly detection • Container security intelligence
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={generateData}
            className="px-4 py-2 bg-accent text-white rounded-lg shadow-glow hover:bg-blue-500 transition"
          >
            Generate Live Data
          </button>

          <div className="px-3 py-2 rounded-lg bg-muted/70 text-xs text-slate-200">
            Connected users: {userCount}
          </div>
        </div>
      </header>

      <main className="px-8 py-8 space-y-6">
        <SummaryCards
          items={[
            { label: "Total Logs Processed", value: summary.total_logs, icon: Activity },
            { label: "Total IoT Events", value: summary.total_iot, icon: Cpu },
            { label: "Anomalies Detected", value: summary.anomalies, icon: AlertTriangle },
            { label: "Active Tamper Alerts", value: summary.active_alerts, icon: ShieldCheck }
          ]}
        />

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-2 space-y-6">
            <ActivityChart data={activity} />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <IoTChart data={iotChart} />
              <TamperChart data={tamperChart} />
            </div>
          </div>

          <div className="space-y-6">
            <AlertPanel alerts={alerts} />
            <ThreatMonitor events={threatEvents} />
            <LiveEventStream events={securityEvents} />
            <StatusPanel status={status} />
            <AnomalyExplanation anomalies={anomalies} />
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <AccessHourChart data={accessHour} />
          <TopIpChart data={topIps} />
          <SuspiciousAccessChart data={accessSuspicious} />
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <GeoDistribution locations={locations} />
          <AccessLogsTable rows={accessLogs} />
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <LogsTable rows={logs} />
          <IoTTable rows={iot} />
        </div>
      </main>
    </div>
  );
}