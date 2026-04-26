import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        qr: {
          bg: '#07111F',
          surface: '#0F1B2E',
          elevated: '#14243B',
          line: 'rgba(255,255,255,.08)',
          text: '#F8FAFC',
          muted: '#CBD5E1',
          blue: '#2563EB',
          cyan: '#0891B2',
          success: '#16A34A',
          warning: '#D97706',
          danger: '#DC2626',
        },
      },
      fontFamily: {
        sans: ['Inter', 'IBM Plex Sans', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        panel: '0 18px 40px rgba(2, 8, 23, 0.26)',
      },
      borderRadius: {
        xl: '14px',
      },
      maxWidth: {
        shell: '1600px',
      },
      transitionDuration: {
        150: '150ms',
        180: '180ms',
      },
      backgroundImage: {
        mesh:
          'radial-gradient(circle at top left, rgba(37,99,235,0.18), transparent 30%), radial-gradient(circle at top right, rgba(8,145,178,0.12), transparent 28%)',
      },
    },
  },
  plugins: [],
} satisfies Config
