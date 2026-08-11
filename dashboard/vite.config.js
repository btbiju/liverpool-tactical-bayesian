import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// base matches the GitHub Pages project-site path (username.github.io/liverpool-tactical-bayesian/).
// Only applied for `vite build`, so local `vite dev` still serves from /.
export default defineConfig(({ command }) => ({
  plugins: [react()],
  base: command === 'build' ? '/liverpool-tactical-bayesian/' : '/',
}))
