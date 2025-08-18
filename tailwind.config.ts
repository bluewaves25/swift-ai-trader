/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        chart: {
          "1": "hsl(var(--chart-1))",
          "2": "hsl(var(--chart-2))",
          "3": "hsl(var(--chart-3))",
          "4": "hsl(var(--chart-4))",
          "5": "hsl(var(--chart-5))",
        },
        sidebar: {
          DEFAULT: "hsl(var(--sidebar))",
          foreground: "hsl(var(--sidebar-foreground))",
        },
      },
      fontSize: {
        body: [
          '14px',
          {
            lineHeight: '1.6',
            letterSpacing: '0',
          },
        ],
        'body-md': [
          '16px',
          {
            lineHeight: '1.7',
            letterSpacing: '0',
          },
        ],
        'body-lg': [
          '18px',
          {
            lineHeight: '1.7',
            letterSpacing: '0',
          },
        ],
        h1: [
          '24px',
          {
            lineHeight: '1.2',
            letterSpacing: '-0.01em',
          },
        ],
        'h1-md': [
          '32px',
          {
            lineHeight: '1.15',
            letterSpacing: '-0.01em',
          },
        ],
        'h1-lg': [
          '40px',
          {
            lineHeight: '1.1',
            letterSpacing: '-0.01em',
          },
        ],
        h2: [
          '20px',
          {
            lineHeight: '1.25',
            letterSpacing: '-0.01em',
          },
        ],
        'h2-md': [
          '24px',
          {
            lineHeight: '1.2',
            letterSpacing: '-0.01em',
          },
        ],
        'h2-lg': [
          '32px',
          {
            lineHeight: '1.15',
            letterSpacing: '-0.01em',
          },
        ],
        h3: [
          '18px',
          {
            lineHeight: '1.3',
            letterSpacing: '-0.01em',
          },
        ],
        'h3-md': [
          '20px',
          {
            lineHeight: '1.25',
            letterSpacing: '-0.01em',
          },
        ],
        'h3-lg': [
          '24px',
          {
            lineHeight: '1.2',
            letterSpacing: '-0.01em',
          },
        ],
        button: [
          '14px',
          {
            lineHeight: '1.5',
            letterSpacing: '0',
            fontWeight: '500',
          },
        ],
        'button-md': [
          '16px',
          {
            lineHeight: '1.5',
            letterSpacing: '0',
            fontWeight: '500',
          },
        ],
        caption: [
          '12px',
          {
            lineHeight: '1.4',
            letterSpacing: '0',
          },
        ],
        'caption-md': [
          '14px',
          {
            lineHeight: '1.4',
            letterSpacing: '0',
          },
        ],
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};