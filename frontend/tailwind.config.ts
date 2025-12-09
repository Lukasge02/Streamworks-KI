import type { Config } from "tailwindcss";

const config: Config = {
    content: [
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                // Arvato Systems Brand Colors
                arvato: {
                    blue: '#0082D9',
                    'blue-dark': '#006BB3',
                    'blue-light': '#33A0E6',
                    gray: '#4F4F4F',
                    'gray-light': '#6B6B6B',
                    'gray-dark': '#3D3D3D',
                },
                primary: {
                    50: '#E6F4FF',
                    100: '#BAE0FF',
                    200: '#8DCBFF',
                    300: '#60B6FF',
                    400: '#33A1FF',
                    500: '#0082D9', // Arvato Main Blue
                    600: '#006BB3',
                    700: '#00548D',
                    800: '#003D66',
                    900: '#002640',
                },
                accent: {
                    50: '#E6FFF7',
                    100: '#B3FFE8',
                    200: '#80FFD9',
                    300: '#4DFFCA',
                    400: '#1AFFBB',
                    500: '#00D4AA', // Teal Accent
                    600: '#00B391',
                    700: '#009278',
                    800: '#00715F',
                    900: '#005046',
                },
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
            },
            boxShadow: {
                'soft': '0 2px 8px rgba(0, 0, 0, 0.08)',
                'medium': '0 4px 16px rgba(0, 0, 0, 0.12)',
                'glow': '0 0 20px rgba(0, 130, 217, 0.25)',
                'glow-accent': '0 0 20px rgba(0, 212, 170, 0.25)',
            },
            animation: {
                'border-beam': 'border-beam calc(var(--duration)*1s) infinite linear',
                'shine': 'shine var(--duration) infinite linear',
                'pulse-soft': 'pulse-soft 2s ease-in-out infinite',
                'float': 'float 3s ease-in-out infinite',
                'fade-in': 'fade-in 0.5s ease-out',
                'slide-up': 'slide-up 0.5s ease-out',
            },
            keyframes: {
                'border-beam': {
                    '100%': { 'offset-distance': '100%' },
                },
                'shine': {
                    '0%': { 'background-position': '0% 0%' },
                    '50%': { 'background-position': '100% 100%' },
                    '100%': { 'background-position': '0% 0%' },
                },
                'pulse-soft': {
                    '0%, 100%': { opacity: '1' },
                    '50%': { opacity: '0.7' },
                },
                'float': {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-8px)' },
                },
                'fade-in': {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                'slide-up': {
                    '0%': { opacity: '0', transform: 'translateY(10px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
            },
            borderRadius: {
                'xl': '12px',
                '2xl': '16px',
                '3xl': '24px',
            },
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
    ],
};

export default config;
