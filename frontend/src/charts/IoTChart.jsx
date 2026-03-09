import React from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

export default function IoTChart({ data }) {
  const labels = data.map(d => d.hour);
  const chartData = {
    labels,
    datasets: [
      {
        label: "Temperature",
        data: data.map(d => d.temperature),
        borderColor: "#22c55e",
        backgroundColor: "rgba(34, 197, 94, 0.2)",
        tension: 0.4
      },
      {
        label: "Vibration",
        data: data.map(d => d.vibration),
        borderColor: "#ef4444",
        backgroundColor: "rgba(239, 68, 68, 0.2)",
        tension: 0.4
      },
      {
        label: "Power",
        data: data.map(d => d.power),
        borderColor: "#3b82f6",
        backgroundColor: "rgba(59, 130, 246, 0.2)",
        tension: 0.4
      }
    ]
  };

  const options = {
    plugins: {
      legend: {
        labels: { color: "#e2e8f0" }
      }
    },
    scales: {
      x: { ticks: { color: "#94a3b8" }, grid: { color: "#1f2937" } },
      y: { ticks: { color: "#94a3b8" }, grid: { color: "#1f2937" } }
    }
  };

  return (
    <div className="glass rounded-2xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">IoT Sensor Monitoring</h3>
        <span className="text-xs text-slate-400">Temp • Vibration • Power</span>
      </div>
      <Line data={chartData} options={options} height={220} />
    </div>
  );
}
