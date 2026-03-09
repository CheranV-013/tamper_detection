export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"] ,
  theme: {
    extend: {
      colors: {
        base: "#0f172a",
        accent: "#3b82f6",
        success: "#22c55e",
        danger: "#ef4444",
        panel: "#111827",
        muted: "#1f2937"
      },
      boxShadow: {
        glow: "0 0 20px rgba(59, 130, 246, 0.35)"
      }
    }
  },
  plugins: []
};
