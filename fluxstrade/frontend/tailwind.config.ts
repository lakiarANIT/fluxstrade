import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#14213d",
        mint: "#2ec4b6",
        coral: "#ff6b6b"
      },
      boxShadow: {
        soft: "0 18px 45px rgba(20, 33, 61, 0.12)"
      }
    }
  },
  plugins: []
};

export default config;
