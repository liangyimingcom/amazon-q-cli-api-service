/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // 启用基于 class 的暗色模式
  theme: {
    extend: {
      colors: {
        // 自定义颜色变量，提高主题一致性
        primary: {
          50: '#eff6ff',
          500: '#1677ff',
          600: '#1366d9',
          700: '#1048a3',
        }
      }
    },
  },
  plugins: [],
}