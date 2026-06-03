import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#0F172A',
          soft: '#1E293B',
          accent: '#1E40AF',
          muted: '#475569',
        },
        surface: {
          DEFAULT: '#FFFFFF',
          subtle: '#F8FAFC',
          border: '#E2E8F0',
        },
        risk: {
          high: {
            bg: '#FEF2F2',
            text: '#991B1B',
            border: '#FECACA',
          },
          medium: {
            bg: '#FFFBEB',
            text: '#92400E',
            border: '#FDE68A',
          },
          low: {
            bg: '#EFF6FF',
            text: '#1E40AF',
            border: '#BFDBFE',
          },
        },
      },
      fontFamily: {
        sans: [
          'Pretendard Variable',
          '-apple-system',
          'Apple SD Gothic Neo',
          'sans-serif',
        ],
      },
      boxShadow: {
        card: '0 18px 45px rgba(15, 23, 42, 0.06)',
      },
    },
  },
  plugins: [],
};

export default config;
