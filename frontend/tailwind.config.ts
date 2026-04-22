import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#171717",
        paper: "#f7f3ea",
        vellum: "#fffaf0",
        rule: "#2f6f73",
        verdict: "#8d2431",
        gold: "#bb8a2c",
        slate: "#394150"
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        serif: ["Georgia", "ui-serif", "serif"]
      }
    }
  },
  plugins: []
};

export default config;
