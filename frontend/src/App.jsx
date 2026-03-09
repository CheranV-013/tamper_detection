import React, { useEffect, useState } from "react";
import { io } from "socket.io-client";
import { ShieldCheck, Activity, AlertTriangle, Cpu } from "lucide-react";
import SummaryCards from "./components/SummaryCards.jsx";
import AlertPanel from "./alerts/AlertPanel.jsx";
import LiveEventStream from "./alerts/LiveEventStream.jsx";
import ActivityChart from "./charts/ActivityChart.jsx";
import IoTChart from "./charts/IoTChart.jsx";
import TamperChart from "./charts/TamperChart.jsx";
import StatusPanel from "./components/StatusPanel.jsx";
import LogsTable from "./tables/LogsTable.jsx";
import IoTTable from "./tables/IoTTable.jsx";
import AnomalyExplanation from "./components/AnomalyExplanation.jsx";

const API_BASE = "http://127.0.0.1:5001/api";
const SOCKET_URL = "http://127.0.0.1:5001";

export default function App() {
  const [summary, setSummary] = useState({
    total_logs: 0,
    total_iot: 0,
    anomalies: 0,
    active_alerts: 0,
    connected_users: 0
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

  const fetchAll = async () => {
    const [s, a, l, i, ac, ic, tc, st, an] = await Promise.all([
      fetch(`${API_BASE}/summary`).then(r => r.json()),
      fetch(`${API_BASE}/alerts`).then(r => r.json()),
      fetch(`${API_BASE}/logs?limit=12`).then(r => r.json()),
      fetch(`${API_BASE}/iot?limit=12`).then(r => r.json()),
      fetch(`${API_BASE}/charts/activity`).then(r => r.json()),
      fetch(`${API_BASE}/charts/iot`).then(r => r.json()),
      fetch(`${API_BASE}/charts/tamper`).then(r => r.json()),
      fetch(`${API_BASE}/system-status`).then(r => r.json()),
      fetch(`${API_BASE}/anomalies?limit=5`).then(r => r.json())
    ]);

    setSummary(s);
    setAlerts(a);
    setLogs(l);
    setIot(i);
    setActivity(ac);
    setIotChart(ic);
    setTamperChart(tc);
    setStatus(st);
    setAnomalies(an);
    setUserCount(s.connected_users || 0);
  };

  const generateData = async () => {
    await fetch(`${API_BASE}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ logs: 25, iot: 25 })
    });
  };

  useEffect(() => {
    fetchAll();
    fetch(`${API_BASE}/dashboard-access`).catch(() => {});

    const socket = io(SOCKET_URL);

    socket.on("security_event", event => {
      setSecurityEvents(prev => [event, ...prev].slice(0, 20));
      fetchAll();
    });

    socket.on("user_count", data => {
      setUserCount(data.count || 0);
    });

    return () => socket.disconnect();
  }, []);

  return (
    <div className="min-h-screen text-slate-100">
      <header className="px-8 py-6 flex items-center justify-between border-b border-slate-800/60">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-accent/15 text-accent shadow-glow">
            <ShieldCheck />
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">
              AI-Powered Tamper Detection & Security Monitoring
            </h1>
            <p className="text-slate-400 text-sm">
              SOC Dashboard • Real-time anomaly detection • IoT tamper intelligence
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
            {
              label: "Total Logs Processed",
              value: summary.total_logs,
              icon: Activity
            },
            {
              label: "Total IoT Events",
              value: summary.total_iot,
              icon: Cpu
            },
            {
              label: "Anomalies Detected",
              value: summary.anomalies,
              icon: AlertTriangle
            },
            {
              label: "Active Tamper Alerts",
              value: summary.active_alerts,
              icon: ShieldCheck
            }
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
            <LiveEventStream events={securityEvents} />
            <StatusPanel status={status} />
            <AnomalyExplanation anomalies={anomalies} />
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <LogsTable rows={logs} />
          <IoTTable rows={iot} />
        </div>
      </main>
    </div>
  );
}
