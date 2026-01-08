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
                    DEFAULT: '#667eea',
                    dark: '#5a67d8',
                },
                secondary: {
                    DEFAULT: '#764ba2',
                    dark: '#667eea',
                },
                background: {
                    DEFAULT: '#ffffff',
                    dark: '#0f172a',
                },
            },
            borderRadius: {
                'xl': '1rem',
                '2xl': '1.5rem',
            },
        },
    },
    plugins: [],
}
