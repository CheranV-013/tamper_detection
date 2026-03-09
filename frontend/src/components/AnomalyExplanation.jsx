import React from "react";
import { Brain } from "lucide-react";

export default function AnomalyExplanation({ anomalies }) {
  return (
    <div className="glass rounded-2xl p-5 space-y-4">
      <div className="flex items-center gap-2 text-slate-200 font-semibold">
        <Brain size={18} />
        AI Anomaly Explanation
      </div>
      {anomalies.length === 0 ? (
        <p className="text-slate-400 text-sm">No anomalies detected yet.</p>
      ) : (
        <div className="space-y-3">
          {anomalies.map(item => (
            <div key={item.id} className="p-3 rounded-lg bg-muted/60 border border-slate-700/60">
              <p className="text-sm text-slate-200">{item.description}</p>
              <div className="text-xs text-slate-400 mt-1">
                Score: {item.anomaly_score.toFixed(3)} • {item.timestamp}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
