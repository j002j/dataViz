<script>
    import { onMount } from "svelte";
    import panorama from "$lib/assets/panorama_people.jpg";

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
            style="transform: translateX({translateX}%); background-image: url('{panorama}');"
        ></div>
        <div
            class="hero-overlay absolute inset-0 bg-gradient-to-b from-black/30 via-transparent to-[#111]"
        ></div>
        <!-- Uncomment if you want the title back -->
        <!-- <a href="/" class="title absolute top-6 left-6 z-10 font-mono text-[#2fff3e] text-base font-bold tracking-widest">
            STARTERKIT
        </a> -->
    </div>
</div>

<section
    class="relative z-10 bg-[#111] text-[#2fff3d] px-8 py-24 md:px-24 lg:px-48 min-h-screen font-sans"
>
    <h2
        class="text-center font-bold text-4xl md:text-5xl font-black uppercase tracking-normal mb-16"
    >
        Data Driven Memes
    </h2>

    <div class="max-w-3xl mx-auto pl-8">
        <p
            class="text-lg md:text-xl leading-relaxed font-light opacity-90 mb-8"
        >
            STARTERKIT is an experiment in turning street style into data you
            can actually explore. We are inspired by the viral starter kit memes
            that capture the essence of subcultures in a single image. Every dot
            represents either a single item (in the item view) or a combination
            of items (in the outfit view). Instead of browsing through feeds,
            you click through real street images to explore outfits in large
            German cities over time.
        </p>

        <p
            class="text-lg md:text-xl leading-relaxed font-light opacity-90 mb-8"
        >
            With the aid of computer vision, street photos are broken down into
            structured information. We are asking the following questions:
        </p>
        <ul
            class="list-disc pl-12 space-y-2 font-light text-xl md:text-base mb-8"
        >
            <li class="hover:italic transition-colors">
                which items people are wearing?
            </li>
            <li class="hover:italic transition-colors">
                what colours they choose?
            </li>
            <li class="hover:italic transition-colors">
                how these elements combine into outfits?
            </li>
        </ul>

        <p
            class="text-lg md:text-xl leading-relaxed font-light opacity-90 mb-8"
        >
            These details such as colour, item category or timestamp, are
            embedded into a shared "style space" (the point cloud), so visually
            and semantically similar looks sit close together.
        </p>

        <p
            class="text-lg md:text-xl leading-relaxed font-light opacity-90 mb-8"
        >
            On the site, you can:
        </p>
        <ul
            class="list-disc pl-12 space-y-2 font-light text-xl md:text-base mb-8"
        >
            <li class="hover:italic transition-colors">
                Hover over points to see the original outfit image appear.
            </li>
            <li class="hover:italic transition-colors">
                Switch between outfits and single items to change the level of
                detail.s
            </li>
            <li class="hover:italic transition-colors">
                Filter by attributes (such as item type, colour or time) and
                watch the point cloud reshape in real time.
            </li>
        </ul>

        <p
            class="text-lg md:text-xl leading-relaxed font-light opacity-90 mb-8"
        >
            Instead of providing fixed answers, the site lets you explore on
            your own terms. What do you notice?
        </p>

        <div
            class="mt-10 p-6 border border-[#2fff3d] bg-[#2fff3d]/5 rounded-sm"
        >
            <h4 class="font-light text-lg md:text-xl">
                This project sits somewhere between <i
                    >fashion research, data visualisation and interactive art</i
                >. STARTERKIT is a prototype for how we might understand
                (fashion) culture through data without losing sight of the
                people, either as visitors exploring the website or as an image
                reference behind each dot.
            </h4>
        </div>
    </div>
</section>

<style>
    :global(body) {
        margin: 0;
        background-color: #111;
    }

    .bg-left-center {
        background-position: left center;
    }
</style>
