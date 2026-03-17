import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import adapter from '@sveltejs/adapter-auto';

export default defineConfig({
    plugins: [
        tailwindcss(),
        sveltekit(),
    ],
    optimizeDeps: {
        exclude: ['embedding-atlas', 'svelte-range-slider-pips']
    },
    server: {
        watch: {
            ignored: ['**/data/**']
        }
    }
});
