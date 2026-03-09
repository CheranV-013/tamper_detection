import React from "react";

export default function AccessLogsTable({ rows }) {
  return (
    <div className="glass rounded-2xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Access Logs</h3>
        <span className="text-xs text-slate-400">Visitor metadata</span>
      </div>
      <div className="overflow-auto scrollbar-thin">
        <table className="min-w-full text-sm">
          <thead className="table-head text-slate-300">
            <tr>
              <th className="text-left px-3 py-2">Timestamp</th>
              <th className="text-left px-3 py-2">IP</th>
              <th className="text-left px-3 py-2">Endpoint</th>
              <th className="text-left px-3 py-2">Device</th>
              <th className="text-left px-3 py-2">Risk</th>
              <th className="text-left px-3 py-2">Location</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(row => (
              <tr key={row.id} className="border-b border-slate-800/50">
                <td className="px-3 py-2 text-slate-400">{row.timestamp}</td>
                <td className="px-3 py-2">{row.ip_address}</td>
                <td className="px-3 py-2">{row.endpoint}</td>
                <td className="px-3 py-2 text-slate-400">{row.user_agent}</td>
                <td className={`px-3 py-2 ${row.risk_score >= 70 ? "text-danger" : "text-slate-100"}`}>
                  {row.risk_score.toFixed ? row.risk_score.toFixed(1) : row.risk_score}
                </td>
                <td className="px-3 py-2 text-slate-300">{row.location}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
