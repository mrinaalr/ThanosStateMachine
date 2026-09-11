import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// GitHub Pages project site: https://mrinaalr.github.io/ThanosStateMachine/
export default defineConfig({
  plugins: [react()],
  base: '/ThanosStateMachine/',
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
