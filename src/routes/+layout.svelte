<script>
  import "../app.css";
  let { children } = $props();
</script>

<!-- {@render children()} -->

<div class="flex flex-col min-h-screen bg-gray-100">
  <header class="bg-yellow-400 p-4">
    <h1 class="text-2xl font-black">STARTERKITS</h1>
  </header>

  <main class="flex-grow flex flex-col">
    {@render children()}
  </main>

  <footer class="bg-purple-500 p-4">
    <h6>Footer</h6>
  </footer>
</div>
