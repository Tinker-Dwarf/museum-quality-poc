# Codie P1 — museum-quality-poc evidence

## Build
```bash
npm install
npm run build   # tsc && vite build — PASS
```

## Screenshot
- Path: `artifacts/codie-p1/default-camera.png`
- Absolute: `/workspace/projects/museum-quality-poc/artifacts/codie-p1/default-camera.png`
- Capture: `npm run capture` (Vite preview + Playwright Chromium, default camera)

## Wheelset checklist
### Ouray (front)
- [x] Open-spoke drivers (4 axles) under boiler/cab
- [x] Leading pony/pilot truck (small wheels at cowcatcher)
- [x] Tender trucks (2 axles, both sides)
- [x] Coupling / main rods + crankpins visible

### Commodore Vanderbilt (rear)
- [x] Leading truck — 2 pilot axles
- [x] Three large drivers with spokes + counterweights under skirt cutouts
- [x] Trailing truck — 2 axles
- [x] Tender wheels (4 axles / both sides)
- [x] Coupling + main rods + cylinder blocks

## No GLB
- Confirmed: no `GLTFLoader` / `.glb` / `.gltf` imports under `src/`
- Geometry is procedural Part-style Three.js primitives only (`Box`, `Cylinder`, `Lathe`, `Torus`, `Tube`, extruded skirts)

## Materials
- `MeshStandardMaterial` palette (shell / shroudBlue / iron / steel / dark / wood / rail)
- Cream museum void `#f4f1ea`, soft PCF shadows, NeutralToneMapping

## Still notes / gaps
- Tender lettering uses **SILVERTON R.R. NO. 102** (still clearly shows 102; brief default was 100)
- Optional chrome: Explode / Steam / eye / reset (right stack)
- Minor: procedural silhouette denser than still; steam wisps on by default
