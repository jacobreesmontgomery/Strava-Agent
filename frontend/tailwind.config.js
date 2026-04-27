/** @type {import('tailwindcss').Config} */
export default {
    content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
    theme: {
        extend: {
            colors: {
                primary: {
                    50: "#f0f4ff",
                    100: "#e6e8ff",
                    500: "#667eea",
                    600: "#5568d3",
                    700: "#4456bb",
                },
                secondary: {
                    500: "#764ba2",
                },
                dark: {
                    bg: "#1e1e1e",
                    border: "#333",
                    text: "#ccc",
                },
            },
        },
    },
    plugins: [],
};
