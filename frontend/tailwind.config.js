/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        cream: {
          50: "#FAF9F5",
          100: "#F5F2EB",
          200: "#EAE3D2",
        },
        indigo: {
          50: "#F0F4F8",
          600: "#2A3B5C",
          800: "#1A263F",
          900: "#101827",
        },
        maroon: {
          100: "#FADBD8",
          600: "#800020", // Burgundy / Maroon
          700: "#600018",
          800: "#4A0010",
        },
        gold: {
          300: "#F1D280",
          500: "#D4AF37", // Pure Gold
          600: "#B8962E",
        },
        sand: {
          100: "#F9F6F0",
          200: "#F1EAD7",
          300: "#E6D7B8",
        },
        slate: {
          850: "#1E2530",
          900: "#0F172A",
        }
      },
      fontFamily: {
        serif: ["var(--font-playfair)", "serif"],
        sans: ["var(--font-inter)", "sans-serif"],
      },
      boxShadow: {
        'premium': '0 10px 40px -10px rgba(42, 59, 92, 0.08), 0 1px 1px rgba(0, 0, 0, 0.01)',
        'gold-glow': '0 0 20px rgba(212, 175, 55, 0.15)',
        'maroon-glow': '0 0 20px rgba(128, 0, 32, 0.1)',
      }
    },
  },
  plugins: [],
}

