// <!--Real - data form pipline.db: point cloud is now implemented as a force - directed graph system-- >
//     <script>
//   import { onMount } from "svelte";
// import { Graph } from "@cosmos.gl/graph";

// let containerElement;
// let graph;
// let rawData = [];
// let selectedPoint = null;

// // STRATEGIES: GRAPH LAYOUT
// //dummy data from cosmos.gl example
// const createDummyGrid = () => {
//     console.log("Creating Dummy Data...");
//     const gridSize = 50; // Smaller grid for faster testing
//     const pointCount = gridSize * gridSize;
//     const positions = new Float32Array(pointCount * 2);

//     for (let i = 0; i < pointCount; i++) {
//         const x = i % gridSize;
//         const y = Math.floor(i / gridSize);

//         // We use 0.0 to 1.0 range for basic coordinates,
//         // or larger if fitView handles it.
//         positions[i * 2] = (x - gridSize / 2) * 20;
//         positions[i * 2 + 1] = (y - gridSize / 2) * 20;
//     }

//     return { positions, links: new Float32Array([]) };
// };

// //data accoring to ID
// const getIDGridLayout = (data) => {
//     console.log("Applying ID Grid Layout...");
//     const pointCount = data.length;
//     const positions = new Float32Array(pointCount * 2);
//     const links = [];

//     // Define how wide the grid should be
//     const columns = Math.floor(Math.sqrt(pointCount)); // Square-ish grid
//     const spacing = 20; // Distance between points

//     for (let i = 0; i < pointCount; i++) {
//         const col = i % columns;
//         const row = Math.floor(i / columns);

//         // Set Position based on Grid Index
//         positions[i * 2] = (col - columns / 2) * spacing;
//         //positions[i * 2 + 1] = (row - pointCount / columns / 2) * spacing;
//         positions[i * 2 + 1] = (row - pointCount / columns / 2) * spacing;

//         // HORIZONTAL LINKS (Right Neighbor)
//         const right = i + 1;
//         // Only link if the next point is in the same row
//         if (right < pointCount && Math.floor(right / columns) === row) {
//             links.push(i, right);
//         }

//         // VERTICAL LINKS (Bottom Neighbor)
//         const bottom = i + columns;
//         if (bottom < pointCount) {
//             links.push(i, bottom);
//         }
//     }

//     return {
//         positions,
//         links: new Float32Array(links),
//     };
// };

// onMount(async () => {
//     try {
//         console.log("Checking container...", containerElement);
//         console.log("start fetch");
//         const response = await fetch("http://localhost:5000/test/point");
//         if (!response.ok) {
//             throw new Error("server repsonse: ${response.status}");
//         } else {
//             console.log("server repsonse: ${response.status}");
//         }

//         rawData = await response.json();
//         if (rawData.length === 0) {
//             console.warn("Datenbank ist leer.");
//             return;
//         } else {
//             console.log("Data loaded sucsessfully:", rawData.length);
//         }

//         // Initialize graph
//         graph = new Graph(containerElement, {
//             backgroundColor: "#111827",
//             pointDefaultSize: 6,
//             pointDefaultColor: "#3B82F6",
//             linkDefaultColor: "#4B5563",
//             linkDefaultAlpha: 0.3,
//             fitViewOnInit: false,
//             enableDrag: true,
//             onClick: (index) => {
//                 if (index !== undefined && index !== null) {
//                     selectedPoint = rawData[index];
//                     console.log("Metadata for clicked point:", selectedPoint);
//                 } else {
//                     selectedPoint = null; //close when background clicked
//                 }
//             },
//         });

//         if (graph) {
//             console.log("Graph instance created successfully");
//         }

//         // GET and display DUMMY DATA
//         // const { positions, colors, links } = createDummyGrid();
//         // console.log("Sample Positions (first 2 points):", positions.slice(0, 4));
//         // graph.setPointPositions(positions);
//         // //graph.setPointColors(colors);
//         // graph.setLinks(links);

//         // display points accoringto ID Layout
//         const layout = getIDGridLayout(rawData);
//         graph.setPointPositions(layout.positions);
//         graph.setLinks(layout.links);

//         // FORCE INITIAL RENDER
//         graph.render();
//         setTimeout(() => {
//             console.log("Attempting to FitView and Start...");
//             graph.fitView(0);
//             graph.start();
//             graph.render();
//             console.log("Points in graph buffer:", layout.positions.length / 2);
//         }, 500);
//     } catch (err) {
//         console.error("Initialization error:", err);
//     }

//     return () => {
//         if (graph) {
//             console.log("Cleaning up graph");
//             graph.destroy();
//         }
//     };
// });
// </script>

//     < !--{ #if selectedPoint }
//     < div class="metadata-popup" >
//         <button class="close-btn" on: click = {() => (selectedPoint = null)}>×</button>

//             < h2 > Fashion Item Details < /h2>
//                 < hr />

//                 <div class="info-grid" >
//                     <p><strong>ID: </strong> {selectedPoint.id}</p >
//                         <p><strong>City ID: </strong> {selectedPoint.city_id}</p >
//                             <p><strong>Captured: </strong> {selectedPoint.captured_at}</p >
//                                 <p>
//                                 <strong>Coordinate: </strong>
// { selectedPoint.location || "N/A" }
// </p>
//     < /div>

//     < div class="image-placeholder" >
//         <p>Image ID: { selectedPoint.original_image_id } </p>
//             < /div>
//             < /div>
// {
//     /if} -->

//         < div
//     bind: this = { containerElement }
//     class="w-full h-screen bg-gray-900"
//     style = "min-height: 100vh; width: 100vw; display: block;"
//         > </div>

//         < !--scriptwith various point displays commeneted out-- >
//             <!-- <script>
//     import { onMount } from "svelte";
//     import { Graph } from "@cosmos.gl/graph";

//     let containerElement;
//     let graph;

//     onMount(async () => {
//         try {
//             //POINT DATA: load data from flask
//             console.log("start fetch");
//             const response = await fetch("http://localhost:5000/test/point");
//             if (!response.ok) {
//                 throw new Error(`Server antwortet mit Status: ${response.status}`);
//             } else {
//                 console.log(`Server antwortet mit Status: ${response.status}`);
//             }

//             const data = await response.json();
//             console.log("Data loaded sucsessfully:", data);
//             const pointCount = data.length; //amount dots needed

//             if (pointCount === 0) {
//                 console.warn("Datatset is empty or cannot get data");
//                 return;
//             }

//             // 2. POSITION ANS INITIALIZE POINTS
//             const pointPositions = new Float32Array(pointCount * 2); //[x0, y0, x1, y1, ...]
//             const linksArray = [];

//             //adust loop depending on how to display points
//             for (let i = 0; i < pointCount; i++) {
//                 // random poistion then physics push them in the roght proistion.
//                 pointPositions[i * 2] = (Math.random() - 0.5) * 5; //[x-position]
//                 pointPositions[i * 2 + 1] = (Math.random() - 0.5) * 5;

//                 if (!pointPositions[i * 2] & !pointPositions[i * 2 + 1]) {
//                     console.log("array for X and Y WITH data");
//                 }

//                 //LINKS BASED ON SAME CITY: messy: better to cluster
//                 // for (let j = i + 1; j < pointCount; j++) {
//                 //   if (data[i].city === data[j].city) {
//                 //     linksArray.push(i, j);
//                 //   }
//                 // }

//                 //LINKS BASED ON ID
//                 const right = i + 1;
//                 const bottom = i + pointCount; //rihctige zuordnung???

//                 const row = Math.floor(i / pointCount); // row in which the point is
//                 const rightRow = Math.floor(right / pointCount); //row of right neighbour

//                 // create horizontal link: i-neighbor, if in the same row
//                 if (rightRow === row) {
//                     linksArray.push(i, right);
//                 }

//                 // Vertical neighbor link
//                 if (bottom < pointCount) {
//                     linksArray.push(i, bottom);
//                 }
//             }

//             // CLUSTER BASED ON CITY: needs links to pull into cluster
//             // 1. Identify Unique Cities and assign them a "Home Base"
//             // const uniqueCities = [...new Set(data.map((d) => d.city_id))];
//             // const cityCenters = {};
//             // uniqueCities.forEach((cityId, index) => {
//             //   // Arrange city centers in a circle so they don't overlap
//             //   const angle = (index / uniqueCities.length) * Math.PI * 2;
//             //   const radius = 500; // Distance between clusters
//             //   cityCenters[cityId] = {
//             //     x: Math.cos(angle) * radius,
//             //     y: Math.sin(angle) * radius,
//             //   };
//             // });

//             // for (let i = 0; i < pointCount; i++) {
//             //   const item = data[i];
//             //   const center = cityCenters[item.city_id];

//             //   // Start points near their city center + some randomness
//             //   pointPositions[i * 2] = center.x + (Math.random() - 0.5) * 50;
//             //   pointPositions[i * 2 + 1] = center.y + (Math.random() - 0.5) * 50;

//             //   // OPTIONAL: Link every point to a "Lead Point" of that city
//             //   // This is more performant than linking everything to everything.
//             //   // Find the first index of this city in the data
//             //   const firstIndexOfCity = data.findIndex(
//             //     (d) => d.city_id === item.city_id,
//             //   );
//             //   if (i !== firstIndexOfCity) {
//             //     linksArray.push(i, firstIndexOfCity);
//             //   }
//             // }

//             const links = new Float32Array(linksArray);

//             // 3. GRAPH CONFIG: render physics
//             graph = new Graph(containerElement, {
//                 backgroundColor: "#111827",
//                 simulationGravity: 0.7, // gravity: Etwas weniger Schwerkraft, damit es sich ausbreitet
//                 simulationRepulsion: 0.5, // repreleling force Punkte stoßen sich ab
//                 simulationDecay: 1000, // friction: Geschwindigkeit des Stillstands
//                 fitViewOnInit: false,
//                 pointDefaultSize: 4,
//                 pointDefaultColor: "#3B82F6",
//                 linkDefaultWidth: 0.5,
//                 simulationLinkDistance: 12,
//                 simulationLinkSpring: 2,
//                 enableDrag: true, //Enable Interactivity
//                 onClick: (index) => { },
//             });

//             if (!graph) {
//                 console.log("graph NICHT erstellt");
//             } else {
//                 console.log("graph WURDE erstellt");
//             }

//             // 4. HAND DATEN OVER TO COSMOS
//             //graph.setPointShapes(pointPositions);
//             graph.setPointPositions(pointPositions);
//             graph.setLinks(links);
//             graph.fitView(0); // setting camera view

//             graph.start(); // Startet die Physik
//             graph.render();
//             //console.log("Points im Graph:", graph.points?.length); //0 = no points: noting to see

//             //timeout to not logg to earyl (=undefined)
//             setTimeout(() => {
//                 console.log("Kamera angepasst und Simulation gestartet");
//                 console.log("Amount of points displayed:", pointPositions.length / 2);
//                 //console.log("Amount of links displayed:", graph.linksArray.length);
//                 console.log(
//                     "Amount Links:",
//                     graph.getPointCount?.() || "method unknown",
//                 );
//             }, 600);
//         } catch (err) {
//             console.error("error when loading the data:", err);
//         }
//         return () => {
//             if (graph) graph.destroy();
//         };
//     });
//     </script> -->

//         < !-- < div bind: this = { containerElement } class="w-full h-screen" > </div> -->

//             < !-- < div
//     bind: this = { containerElement }
//     class="w-full h-[600px] rounded-lg border border-gray-800"
//         > </div> -->

//         < !--dummy - data: point cloud is now implemented as a force - directed graph system-- >
//             <!-- <script>
//     import { onMount } from "svelte";
//     import { Graph } from "@cosmos.gl/graph";

//     let containerElement;

//     onMount(() => {
//         const gridSize = 100;
//         const pointCount = gridSize * gridSize; //10.000 dots needed

//         // --------------------------------------------------
//         // POINT DATA
//         // --------------------------------------------------
//         const pointPositions = new Float32Array(pointCount * 2); //*2 as each point needs x,y values: i[0]=x0 i[1]=y0....
//         const linksArray = []; // each link has 2 pints

//         // i = point index
//         for (let i = 0; i < pointCount; i++) {
//             //offset form (0,0) so points don't overlap
//             pointPositions[i * 2] = (Math.random() - 0.5) * 5; //[x-position]
//             pointPositions[i * 2 + 1] = (Math.random() - 0.5) * 5; // [y-position]

//             const right = i + 1;
//             const bottom = i + gridSize;

//             const row = Math.floor(i / gridSize); // row in which the point is
//             const rightRow = Math.floor(right / gridSize); //row of right neighbour

//             // create horizontal link: i-neighbor, if in the same row
//             if (rightRow === row) {
//                 linksArray.push(i, right);
//             }

//             // Vertical neighbor link
//             if (bottom < pointCount) {
//                 linksArray.push(i, bottom);
//             }
//         }

//         const links = new Float32Array(linksArray);

//         // --------------------------------------------------
//         // GRAPH + PHYSICS CONFIGURATION
//         // --------------------------------------------------
//         const graph = new Graph(containerElement, {
//             backgroundColor: "#111827",
//             spaceSize: 4000,

//             // 1. ADD GRAVITY
//             // This pulls the center of mass back to (0,0)
//             simulationGravity: 0.7,

//             // 2. ADJUST REPELLING FORCE
//             // High repulsion can sometimes "explode" the graph outward
//             simulationRepulsion: 0.2,

//             // 3. FRICTION (DECAY)
//             // Higher friction (lower decay value) stops the "drifting" motion faster.
//             // smaller simulationDecay value = simulation settles faster
//             simulationDecay: 1000,
//             fitViewOnInit: false, // for setting camera view below

//             pointDefaultSize: 3,
//             linkDefaultWidth: 0.5,
//             simulationLinkDistance: 12,
//             simulationLinkSpring: 2,
//             enableDrag: true,
//         });

//         // --------------------------------------------------
//         // APPLY DATA & START RENDERING
//         // --------------------------------------------------
//         graph.setPointPositions(pointPositions);
//         graph.setLinks(links);
//         graph.fitView(0); // setting camera view
//         graph.start(0.1);
//         graph.render();

//         //for debugging: view some points in console
//         for (let i = 0; i < 10; i++) {
//             console.log(
//                 `Punkt ${i}:`,
//                 pointPositions[i * 2],
//                 pointPositions[i * 2 + 1],
//             );
//         }

//         // --------------------------------------------------
//         // CLEANUP
//         // --------------------------------------------------
//         return () => {
//             graph.destroy();
//         };
//     });
//     </script>

//         < div
//     bind: this = { containerElement }
//     class="w-full h-[600px] rounded-lg border border-gray-800"
//         > </div> -->

//         < !--dumy - data: code below with a deterministic geometric layout-- >
//             <!-- <script>
//     import { onMount } from "svelte";
//     import { Graph } from "@cosmos.gl/graph";

//     let containerElement;

//     onMount(() => {
//         const gridSize = 100;
//         const pointCount = gridSize * gridSize;

//         // v2 uses Float32Arrays for high performance
//         const pointPositions = new Float32Array(pointCount * 2);
//         const pointColors = new Float32Array(pointCount * 4); // RGBA

//         for (let i = 0; i < pointCount; i++) {
//             const x = i % gridSize;
//             const y = Math.floor(i / gridSize);

//             // Positions (normalized between -500 and 500 for a clear view)
//             pointPositions[i * 2] = (x - gridSize / 2) * 10;
//             pointPositions[i * 2 + 1] = (y - gridSize / 2) * 10;

//             // Colors (RGBA: 0 to 1)
//             pointColors[i * 4] = 0.3; // Red
//             pointColors[i * 4 + 1] = 0.4; // Green
//             pointColors[i * 4 + 2] = 0.9; // Blue
//             pointColors[i * 4 + 3] = 1.0; // Alpha
//         }

//         const config = {
//             backgroundColor: "#111827", // Dark gray
//             pointDefaultSize: 4,
//         };

//         // v2 initializes on a DIV, not a Canvas
//         const graph = new Graph(containerElement, config);

//         graph.setPointPositions(pointPositions);
//         graph.setPointColors(pointColors);

//         // Manually trigger the first render
//         graph.render();

//         return () => {
//             graph.destroy(); // Clean up on component unmount
//         };
//     });
//     </script>

//         < div
//     bind: this = { containerElement }
//     class="w-full h-[600px] rounded-lg border border-gray-800"
//         > </div> -->

//         < !-- <style>
//   : global(body) {
//         margin: 0;
//         padding: 0;
//         overflow: hidden;
//     }
//     </style> -->

//         < !-- <style>
//             .canvas - container {
//         width: 100 %;
//         height: 100vh;
//         background: #111827;
//     }

//   .metadata - popup {
//         position: absolute;
//         top: 20px;
//         right: 20px;
//         width: 280px;
//         padding: 1rem;
//         background: white;
//         color: #333;
//         border - radius: 8px;
//         z - index: 100; /* Stays on top of the graph */
//         box - shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
//     }
//     </style> -->
