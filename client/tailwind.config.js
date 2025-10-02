/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#3B82F6',
        'primary-dark': '#2563EB',
        'white': '#FFFFFF',
        'neutral-100': '#F9FAFB',
        'neutral-200': '#F3F4F6',
        'neutral-300': '#E5E7EB',
        'neutral-700': '#374151',
        'neutral-900': '#111827',
      },
    },
  },
  plugins: [],
}
