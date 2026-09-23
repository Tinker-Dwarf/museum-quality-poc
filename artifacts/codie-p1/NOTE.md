# Codie P1.1 — museum-quality-poc evidence (re-seat INGOT-102)

## Verify FAIL cited
- RUN_ID: `20260923T013913Z`
- Report: `artifacts/verify-p1/20260923T013913Z/VERIFY-REPORT.md`
- Hard FAIL criterion **1**: wheelsets not readable at default camera (value crush + CV skirt occlusion). Lathe pack CLEAR — untouched.

## Build
```bash
npm install
npm run build   # tsc && vite build — PASS
npm run capture # → artifacts/codie-p1/default-camera.png
```

## Screenshot
- Path: `artifacts/codie-p1/default-camera.png`
- Absolute: `/workspace/projects/museum-quality-poc/artifacts/codie-p1/default-camera.png`
- Capture: `npm run capture` (Vite + Playwright Chromium 1440×900, default camera)
- Steam: **off** by default

## Wheelset checklist (after P1.1 fix — both locos)
### Ouray (front)
- [x] Open-spoke drivers (4 axles × both sides) readable at default camera — steel spokes vs iron tires
- [x] Leading pony/pilot truck (open-spoke small wheels at cowcatcher) high-contrast vs pedestal/cream
- [x] Tender trucks (2 axles, both sides)
- [x] Coupling / main rods + crankpins visible (outboard, lifted steel)

### Commodore Vanderbilt (rear)
- [x] Leading truck — 2 pilot axles × both sides
- [x] Three large drivers with open spokes + counterweights **popping in deep skirt cutouts**
- [x] Trailing truck — 2 axles × both sides
- [x] Tender wheels (4 axles / both sides)
- [x] Coupling + main rods + cylinder blocks (outboard toward cutouts)
- [x] Side lettering full **COMMODORE VANDERBILT** (no OMMODORE clip)

## Fix summary (museum face / procedural only — no GLB)
1. Lifted `iron` / `dark` / `steel` + soft emissive; lowered metalness so fill/rim lifts undercarriage (no env-map crush).
2. Studio: stronger camera-side fill, bounce, undercarriage lights, wheel kick; exposure 1.35; slightly lower default camera for wheel-face read.
3. CV: deep scalloped skirt cutouts (`yBay≈1.85`); dual-side drivers flush to skirt; thinner motion mass behind bays.
4. Ouray: dual-side open-spoke drivers outside running boards/cylinders; open-spoke pony; thicker spokes/rods.
5. Steam default off (`createStudio` + chrome).
6. Pedestals + short tracks + cream void `#f4f1ea` retained.

## No GLB
- Confirmed: no `GLTFLoader` / `.glb` / `.gltf` imports under `src/`
- Geometry is procedural Part-style Three.js primitives only

## Lathe pack
- **CLEAR** — no edits under `artifacts/lathe-p1/`
