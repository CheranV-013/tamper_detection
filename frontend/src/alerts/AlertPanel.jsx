import React from "react";
import { Siren } from "lucide-react";

export default function AlertPanel({ alerts }) {
  return (
    <div className="glass rounded-2xl p-5 space-y-4">
      <div className="flex items-center gap-2 text-slate-200 font-semibold">
        <Siren size={18} />
        Tamper Alert Panel
      </div>
      {alerts.length === 0 ? (
        <p className="text-slate-400 text-sm">No active alerts.</p>
      ) : (
        <div className="space-y-3">
          {alerts.map(alert => (
            <div key={alert.id} className="p-4 rounded-xl bg-danger/15 border border-danger/40 animate-pulse">
              <p className="text-sm font-semibold text-danger">{alert.alert_message}</p>
              <div className="text-xs text-slate-300 mt-1">{alert.timestamp}</div>
              <div className="text-xs text-slate-400 mt-1">Severity: high</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
