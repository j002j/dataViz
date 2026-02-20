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
        exclude: ['embedding-atlas']
    }
    // server: {
    //     fs: {
    //         // Erlaubt Vite den Zugriff auf den gesamten Workspace
    //         allow: ['..']
    //     }
    // }
});