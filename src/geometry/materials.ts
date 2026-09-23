import * as THREE from "three";

/** Loco palette — keys inspired by study doctrine; values are original. */
export type PaletteKey =
  | "shell"
  | "trim"
  | "iron"
  | "steel"
  | "cab"
  | "glass"
  | "dark"
  | "roof"
  | "casing"
  | "olive"
  | "shroudBlue"
  | "wood"
  | "rail";

export type Palette = Record<PaletteKey, THREE.MeshStandardMaterial>;

export function createPalette(): Palette {
  const mk = (
    color: number,
    roughness: number,
    metalness: number,
    extra?: Partial<THREE.MeshStandardMaterialParameters>,
  ) =>
    new THREE.MeshStandardMaterial({
      color,
      roughness,
      metalness,
      ...extra,
    });

  return {
    shell: mk(0x9a9da4, 0.62, 0.22),
    trim: mk(0xcdcabf, 0.28, 0.75),
    // Mid iron tire/frame — above crushed black, below cream so spokes separate
    iron: mk(0x5f5c55, 0.68, 0.1, { emissive: 0x1a1917, emissiveIntensity: 0.18 }),
    // Bright steel spokes/rods — high contrast vs iron tire and pedestal
    steel: mk(0xd8d4ca, 0.4, 0.15, { emissive: 0x3c3a36, emissiveIntensity: 0.32 }),
    cab: mk(0x4a5540, 0.72, 0.14),
    glass: mk(0x7f97a4, 0.22, 0.4, { transparent: true, opacity: 0.4 }),
    dark: mk(0x4a4742, 0.75, 0.08, { emissive: 0x161514, emissiveIntensity: 0.1 }),
    roof: mk(0x33322f, 0.78, 0.2),
    casing: mk(0x4c545d, 0.5, 0.35),
    olive: mk(0x3a3c3f, 0.78, 0.18),
    shroudBlue: mk(0x5a6570, 0.52, 0.28),
    wood: mk(0xb3a892, 0.9, 0.05),
    rail: mk(0x8a8781, 0.45, 0.45),
  };
}

let shared: Palette | null = null;
export function palette(): Palette {
  if (!shared) shared = createPalette();
  return shared;
}
