import React from "react";

export default function SummaryCards({ items }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
      {items.map((item, idx) => {
        const Icon = item.icon;
        return (
          <div key={idx} className="glass rounded-2xl p-5 flex items-center gap-4">
            <div className="p-3 rounded-xl bg-accent/20 text-accent">
              <Icon size={22} />
            </div>
            <div>
              <p className="text-slate-400 text-sm">{item.label}</p>
              <p className="text-2xl font-semibold">{item.value}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
