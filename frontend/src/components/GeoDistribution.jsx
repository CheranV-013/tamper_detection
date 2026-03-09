import React from "react";
import { Globe } from "lucide-react";

export default function GeoDistribution({ locations }) {
  return (
    <div className="glass rounded-2xl p-5 space-y-4">
      <div className="flex items-center gap-2 text-slate-200 font-semibold">
        <Globe size={18} />
        Geolocation Snapshot
      </div>
      {locations.length === 0 ? (
        <p className="text-slate-400 text-sm">No access locations yet.</p>
      ) : (
        <div className="space-y-3">
          {locations.map((loc, idx) => (
            <div key={`${loc.name}-${idx}`} className="flex items-center justify-between text-sm">
              <span className="text-slate-300">{loc.name}</span>
              <span className="text-slate-100 font-medium">{loc.count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
