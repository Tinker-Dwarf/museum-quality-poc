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
    shell: mk(0x9a9da4, 0.62, 0.28), // light matte gray boiler (still)
    trim: mk(0xcdcabf, 0.26, 0.9), // polished silver/nickel read for bell/domes
    iron: mk(0x33322f, 0.72, 0.4), // charcoal cast iron (stack/smokebox)
    steel: mk(0x8b8983, 0.44, 0.6),
    cab: mk(0x4a5540, 0.72, 0.14), // muted olive-grey cab
    glass: mk(0x7f97a4, 0.22, 0.4, { transparent: true, opacity: 0.4 }),
    dark: mk(0x1d1c1a, 0.86, 0.14),
    roof: mk(0x33322f, 0.78, 0.2),
    casing: mk(0x4c545d, 0.5, 0.4),
    olive: mk(0x3a3c3f, 0.78, 0.18), // charcoal cab/tender (still match; key kept)
    shroudBlue: mk(0x5a6570, 0.48, 0.38), // dark blue-gray shroud (still)
    wood: mk(0xb3a892, 0.9, 0.05), // bleached tie wood
    rail: mk(0x8a8781, 0.42, 0.6),
  };
}

/** Shared singleton for the studio session. */
let shared: Palette | null = null;
export function palette(): Palette {
  if (!shared) shared = createPalette();
  return shared;
}
