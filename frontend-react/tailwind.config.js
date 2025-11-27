/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                cyber: {
                    green: '#00ff9d',
                    teal: '#00f0ff',
                    dark: '#050510',
                    glass: 'rgba(255, 255, 255, 0.05)',
                }
            },
            fontFamily: {
                mono: ['"Space Mono"', 'monospace'],
                sans: ['Inter', 'sans-serif'],
            },
            animation: {
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            }
        },
    },
    plugins: [],
}
