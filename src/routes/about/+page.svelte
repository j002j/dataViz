<script>
    import { onMount } from "svelte";
    import panorama from "$lib/assets/panorama.jpeg";

    let translateX = $state(0);

    onMount(() => {
        const handleScroll = () => {
            const scrollY = window.scrollY;
            const maxScroll = window.innerHeight * 3;
            const progress = Math.min(Math.max(scrollY / maxScroll, 0), 1);
            translateX = progress * -40;
        };

        window.addEventListener("scroll", handleScroll, { passive: true });
        return () => window.removeEventListener("scroll", handleScroll);
    });
</script>

<div class="pin-spacer h-[300vh] relative">
    <div
        class="sticky top-0 h-screen w-full overflow-hidden flex items-center justify-center"
    >
        <div
            class="parallax-bg absolute top-0 left-0 w-[200%] h-full bg-cover bg-left-center will-change-transform"
            style="transform: translateX({translateX}%); background-image: url({panorama})"
        ></div>
        <div
            class="hero-overlay absolute inset-0 bg-gradient-to-b from-black/30 via-transparent to-[#111]"
        ></div>
        <a
            href="/"
            class="title absolute top-6 left-6 z-10 font-mono text-[#2fff3e] text-base font-bold tracking-widest"
        >
            STARTERKIT
        </a>
    </div>
</div>

<section
    class="relative z-10 bg-[#111] text-[#2fff3d] px-8 py-24 md:px-24 lg:px-48 min-h-screen font-sans"
>
    <h2
        class="text-center font-mono text-4xl md:text-5xl font-black uppercase tracking-tighter mb-16"
    >
        Data Driven Memes
    </h2>

    <div class="max-w-3xl mx-auto border-l border-[#2fff3d]/30 pl-8">
        <p class="text-lg md:text-xl leading-relaxed font-light opacity-90">
            This Project is a data visualization and analysis project that uses
            real-world street imagery to explore cultural fashion patterns
            across cities and time worldwide.
            <br /><br />
            Inspired by "Starterpack" memes, we create data-driven visual archetypes
            by applying computer vision to detect clothing attributes and grouping
            them into the most common outfits typical for specific neighborhoods.
        </p>

        <div class="mt-12">
            <p class="font-mono uppercase tracking-widest text-sm mb-4">
                Technical Core:
            </p>
            <ul class="list-disc pl-5 space-y-4 font-mono text-sm md:text-base">
                <li class="hover:text-white transition-colors">
                    Computer vision on open-source street images
                </li>
                <li class="hover:text-white transition-colors">
                    Relational database modeling to organize images, categories,
                    and clothing subtypes
                </li>
                <li class="hover:text-white transition-colors">
                    Data-driven storytelling via visual fashion trend analysis
                </li>
            </ul>
        </div>

        <div
            class="mt-10 p-6 border border-[#2fff3d] bg-[#2fff3d]/5 rounded-sm"
        >
            <h4 class="font-mono text-lg font-bold leading-snug">
                Starterkits turns everyday street fashion into structured,
                analyzable cultural data by blending meme logic, fashion
                sociology, and data science.
            </h4>
        </div>
    </div>
</section>

<style>
    :global(body) {
        margin: 0;
        background-color: #111;
    }

    /* We keep this one custom class for the bg-position since Tailwind's center-left is less specific */
    .bg-left-center {
        background-position: left center;
    }
</style>
