import React from "react";

export default function IoTTable({ rows }) {
  return (
    <div className="glass rounded-2xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Recent IoT Events</h3>
        <span className="text-xs text-slate-400">Sensor telemetry</span>
      </div>
      <div className="overflow-auto scrollbar-thin">
        <table className="min-w-full text-sm">
          <thead className="table-head text-slate-300">
            <tr>
              <th className="text-left px-3 py-2">Timestamp</th>
              <th className="text-left px-3 py-2">Device</th>
              <th className="text-left px-3 py-2">Temp</th>
              <th className="text-left px-3 py-2">Vibration</th>
              <th className="text-left px-3 py-2">Motion</th>
              <th className="text-left px-3 py-2">Door</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(row => (
              <tr key={row.id} className="border-b border-slate-800/50">
                <td className="px-3 py-2 text-slate-400">{row.timestamp}</td>
                <td className="px-3 py-2">{row.device_id}</td>
                <td className="px-3 py-2">{row.temperature}</td>
                <td className={`px-3 py-2 ${row.vibration >= 2.0 ? "text-danger" : "text-slate-100"}`}>
                  {row.vibration}
                </td>
                <td className="px-3 py-2">{row.motion ? "true" : "false"}</td>
                <td className={`px-3 py-2 ${row.door === "open" ? "text-danger" : "text-slate-100"}`}>
                  {row.door}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
