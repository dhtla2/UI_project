/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'main-bg': '#f5f7fa',
        'card-bg': '#fff',
        'primary': '#3b7ddd',
        'gray': '#bfc9d9',
        'sidebar-bg': '#25304a',
        'sidebar-active': '#3b7ddd',
        'sidebar-text': '#fff',
        'success': '#28a745',
        'danger': '#dc3545',
        'warning': '#ffc107',
        'info': '#17a2b8',
      },
      fontFamily: {
        'main': ['Noto Sans KR', 'Pretendard', 'Segoe UI', 'Arial', 'sans-serif'],
      },
      borderRadius: {
        'card': '16px',
      },
      boxShadow: {
        'card': '0 2px 8px rgba(60,80,120,0.08)',
      }
    },
  },
  plugins: [],
} 