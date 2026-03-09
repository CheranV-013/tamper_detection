import React from "react";
import { ShieldAlert } from "lucide-react";

const severityStyles = {
  warning: "border-yellow-400/50 text-yellow-200",
  high: "border-orange-400/50 text-orange-200",
  critical: "border-red-500/70 text-red-200"
};

export default function ThreatMonitor({ events }) {
  return (
    <div className="glass rounded-2xl p-5 space-y-4">
      <div className="flex items-center gap-2 text-slate-200 font-semibold">
        <ShieldAlert size={18} />
        Threat Monitor
      </div>
      {events.length === 0 ? (
        <p className="text-slate-400 text-sm">No active access threats.</p>
      ) : (
        <div className="space-y-3 max-h-56 overflow-auto scrollbar-thin">
          {events.map((event, idx) => (
            <div
              key={`${event.timestamp}-${idx}`}
              className={`p-3 rounded-lg border ${severityStyles[event.severity] || "border-slate-700/60 text-slate-300"}`}
            >
              <div className="text-xs uppercase tracking-wide opacity-70">{event.type}</div>
              <div className="text-sm font-medium mt-1">{event.message}</div>
              <div className="text-xs text-slate-400 mt-1">IP: {event.ip || "unknown"}</div>
              {event.endpoint && (
                <div className="text-xs text-slate-400">Endpoint: {event.endpoint}</div>
              )}
              {event.risk_score !== undefined && (
                <div className="text-xs text-slate-400">Risk score: {event.risk_score}</div>
              )}
              <div className="text-xs text-slate-400">{event.timestamp}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
