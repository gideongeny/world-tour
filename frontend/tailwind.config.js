/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                primary: {
                    DEFAULT: '#EA863A', // Magical Kenya Jaffa
                    dark: '#D97529',
                },
                secondary: {
                    DEFAULT: '#2F5233', // Acacia Green
                    dark: '#1E3822',
                },
                accent: {
                    DEFAULT: '#CE1126', // Maasai Red
                },
                background: {
                    DEFAULT: '#F9F7F2', // Warm Savannah
                    dark: '#1A1816',
                },
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                serif: ['Playfair Display', 'serif'],
            },
            borderRadius: {
                'xl': '1rem',
                '2xl': '1.5rem',
            },
        },
    },
    plugins: [],
}
