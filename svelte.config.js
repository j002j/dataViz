// svelte.config.js

import adapter from '@sveltejs/adapter-auto';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
    // 1. Preprocessor: Definiert, wie Svelte-Komponenten vor der Kompilierung verarbeitet werden.
    // Wir verwenden vitePreprocess, das TypeScript und PostCSS (für Tailwind) unterstützt.
    preprocess: vitePreprocess(),

    // 2. Kit Konfiguration: Definiert das Verhalten von SvelteKit
    kit: {
        // Der Adapter ist dafür zuständig, das SvelteKit-Projekt für die Deployment-Umgebung anzupassen.
        // `adapter-auto` ist der Standard, der versucht, die Umgebung automatisch zu erkennen (Vercel, Netlify, Node.js, etc.).
        adapter: adapter()
    }
};

export default config;