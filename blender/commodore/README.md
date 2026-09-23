# Commodore Vanderbilt — Blender → GLB sidecar

Parallel path to the museum POC. The Vite app in `/src` stays procedural (no GLB loader). This folder is for bots that author Blender Python and for the home box that runs Blender.

## Build + export

```bash
cd blender/commodore
blender --background --python build_commodore.py -- --out commodore.glb
```

Needs Blender 4.x / 5.x with the bundled glTF exporter.

## View (standalone, not the Vite museum)

```bash
python3 -m http.server 8080
```

Open `http://localhost:8080` — `preview.html` loads `./commodore.glb` with Three.js `GLTFLoader`.

Validate first if the page is blank: https://gltf-viewer.donmccurdy.com/

## Contract for bots

1. Edit `build_commodore.py`. Do not run Blender from a Grok seat that has no Blender.
2. Export: `export_format='GLB'`, `export_yup=True`, apply transforms, no cameras/lights in the file.
3. Locomotive: 1934 NYC 4-6-4 Hudson streamliner (Commodore Vanderbilt). Shop block-out, not a measured drawing.
