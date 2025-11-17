/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        student: {
          DEFAULT: '#DBEAFE',
          dark: '#1E3A8A'
        },
        assistant: {
          DEFAULT: '#F3F4F6',
          dark: '#1F2937'
        }
      }
    },
  },
  plugins: [],
}
