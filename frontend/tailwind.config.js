/** @type {import('tailwindcss').Config} */
export default {
	darkMode: ["class"],
	content: [
		"./index.html",
		"./src/**/*.{js,ts,jsx,tsx}",
	],
	theme: {
		extend: {
			animation: {
				'spin-slow': 'spin 3s linear infinite',
				'accordion-down': 'accordion-down 0.2s ease-out',
				'accordion-up': 'accordion-up 0.2s ease-out',
				"caret-blink": "caret-blink 1.25s ease-out infinite",
				'pulse-border': 'pulse-border 1.5s infinite ease-out',
				'pulse-border-delayed': 'pulse-border 1.5s infinite ease-out 0.75s',
				'click': 'click 0.2s ease-in-out',
			},
			borderRadius: {
				lg: 'var(--radius)',
				md: 'calc(var(--radius) - 2px)',
				sm: 'calc(var(--radius) - 4px)'
			},
			colors: {},
			keyframes: {
				"caret-blink": {
					"0%,70%,100%": { opacity: "1" },
					"20%,50%": { opacity: "0" },
				},
				'accordion-down': {
					from: {
						height: '0'
					},
					to: {
						height: 'var(--radix-accordion-content-height)'
					}
				},
				'accordion-up': {
					from: {
						height: 'var(--radix-accordion-content-height)'
					},
					to: {
						height: '0'
					}
				},
				'pulse-border': {
					'0%': { transform: 'scale(1)', opacity: '1' },
					'50%': { transform: 'scale(1.4)', opacity: '0' },
					'100%': { transform: 'scale(1)', opacity: '0' },
					'click': {
						'0%, 100%': { transform: 'scale(1)' },
						'50%': { transform: 'scale(0.95)' },
					},
				},
			}
		}
	},
	plugins: [require("tailwindcss-animate")],
}