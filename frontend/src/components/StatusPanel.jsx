import React from "react";
import { Radio, ShieldAlert, Server } from "lucide-react";

const Badge = ({ label, value }) => (
  <div className="flex items-center justify-between text-sm">
    <span className="text-slate-400">{label}</span>
    <span className="text-slate-100 font-medium capitalize">{value}</span>
  </div>
);

export default function StatusPanel({ status }) {
  return (
    <div className="glass rounded-2xl p-5 space-y-4">
      <div className="flex items-center gap-2 text-slate-200 font-semibold">
        <Server size={18} />
        Security Status Panel
      </div>
      <div className="space-y-3">
        <Badge label="System Health" value={status.system_health || "loading"} />
        <Badge label="Sensor Status" value={status.sensor_status || "loading"} />
        <Badge label="Network Activity" value={status.network_activity || "loading"} />
      </div>
      <div className="flex gap-3 pt-2">
        <div className="flex items-center gap-2 text-xs bg-success/15 text-success px-2 py-1 rounded-full">
          <Radio size={14} />
          Live Monitoring
        </div>
        <div className="flex items-center gap-2 text-xs bg-danger/15 text-danger px-2 py-1 rounded-full">
          <ShieldAlert size={14} />
          Tamper Watch
        </div>
      </div>
    </div>
  );
}
