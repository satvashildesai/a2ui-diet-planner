/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["DM Sans", "system-ui", "sans-serif"],
        serif: ["Playfair Display", "Georgia", "serif"],
      },
      colors: {
        saffron: {
          50: "#FFF4EE",
          100: "#FFE8D6",
          500: "#FF6B1A",
          600: "#E55A00",
        },
        turmeric: {
          50: "#FFF8E7",
          400: "#F5C842",
          500: "#F5A623",
        },
        cardamom: {
          600: "#2D4A3E",
          700: "#1E3329",
        },
      },
    },
  },
  plugins: [],
};
