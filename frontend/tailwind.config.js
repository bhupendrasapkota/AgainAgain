/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      keyframes: {
        'quantum-particles': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' }
        },
        'particle': {
          '0%, 100%': { transform: 'scale(1)', opacity: '0.8' },
          '50%': { transform: 'scale(1.2)', opacity: '0.4' }
        },
        'quantum-stroke': {
          '0%': { 
            strokeDasharray: '0 2000',
            strokeDashoffset: '2000',
            opacity: '0'
          },
          '50%': { 
            strokeDasharray: '2000 0',
            strokeDashoffset: '0',
            opacity: '0.8'
          },
          '100%': { 
            strokeDasharray: '0 2000',
            strokeDashoffset: '-2000',
            opacity: '0'
          }
        },
        'geometric-1': {
          '0%': { transform: 'rotate(0deg) scale(1)' },
          '50%': { transform: 'rotate(180deg) scale(1.1)' },
          '100%': { transform: 'rotate(360deg) scale(1)' }
        },
        'geometric-2': {
          '0%': { transform: 'rotate(360deg) scale(1)' },
          '50%': { transform: 'rotate(180deg) scale(0.9)' },
          '100%': { transform: 'rotate(0deg) scale(1)' }
        },
        'energy-wave': {
          '0%': { 
            strokeDasharray: '0 1000',
            strokeDashoffset: '1000',
            opacity: '0'
          },
          '50%': { 
            strokeDasharray: '1000 0',
            strokeDashoffset: '0',
            opacity: '0.6'
          },
          '100%': { 
            strokeDasharray: '0 1000',
            strokeDashoffset: '-1000',
            opacity: '0'
          }
        },
        'quantum-splatters': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' }
        },
        'splatter': {
          '0%': { transform: 'scale(0)', opacity: '0' },
          '50%': { transform: 'scale(1.1)', opacity: '0.8' },
          '100%': { transform: 'scale(1)', opacity: '0.6' }
        }
      },
      animation: {
        'quantum-particles': 'quantum-particles 40s linear infinite',
        'particle': 'particle 4s ease-in-out infinite',
        'quantum-stroke': 'quantum-stroke 12s ease-in-out infinite',
        'geometric-1': 'geometric-1 16s ease-in-out infinite',
        'geometric-2': 'geometric-2 16s ease-in-out infinite reverse',
        'energy-wave': 'energy-wave 8s ease-in-out infinite',
        'quantum-splatters': 'quantum-splatters 30s linear infinite',
        'splatter': 'splatter 2s ease-out infinite'
      }
    },
  },
  plugins: [],
}; 