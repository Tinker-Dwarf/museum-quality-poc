# Museum Quality POC

Vite + TypeScript + Three.js museum face: **Ouray** (Silverton R.R. No. 102) and **Commodore Vanderbilt** (New York Central) on light pedestals with short track segments in a cream museum void.

Procedural Part-style geometry only — **no GLB loader**.

## Prove commands

```bash
npm install
npm run build
npm run dev          # http://localhost:5174
npm run capture      # writes artifacts/codie-p1/default-camera.png
```

## Hard checks (P1)

1. Cream / soft-gray museum void + soft shadows
2. Two light pedestals + **short** track only (no long floor rails)
3. Rear: streamlined Commodore Vanderbilt (dark blue-gray, NEW YORK CENTRAL tender)
4. Front: Ouray traditional (stack / domes / cowcatcher, SILVERTON R.R. NO. 102)
5. **Full wheelsets on both** — drivers + pilot / lead trucks visible
6. MeshStandardMaterial (solid lit), no flat foam
7. Default camera: high three-quarter (still-matched)
8. Evidence: `artifacts/codie-p1/default-camera.png` + `NOTE.md`

## License

MIT
