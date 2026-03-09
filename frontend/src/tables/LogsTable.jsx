import React from "react";

export default function LogsTable({ rows }) {
  return (
    <div className="glass rounded-2xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Recent Logs</h3>
        <span className="text-xs text-slate-400">System activity feed</span>
      </div>
      <div className="overflow-auto scrollbar-thin">
        <table className="min-w-full text-sm">
          <thead className="table-head text-slate-300">
            <tr>
              <th className="text-left px-3 py-2">Timestamp</th>
              <th className="text-left px-3 py-2">User</th>
              <th className="text-left px-3 py-2">Action</th>
              <th className="text-left px-3 py-2">Status</th>
              <th className="text-left px-3 py-2">IP Address</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(row => (
              <tr key={row.id} className="border-b border-slate-800/50">
                <td className="px-3 py-2 text-slate-400">{row.timestamp}</td>
                <td className="px-3 py-2">{row.user}</td>
                <td className="px-3 py-2">{row.action}</td>
                <td className={`px-3 py-2 ${row.status === "failed" ? "text-danger" : "text-success"}`}>
                  {row.status}
                </td>
                <td className="px-3 py-2 text-slate-400">{row.ip_address}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
