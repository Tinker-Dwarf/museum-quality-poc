/**
 * Drawing-space helpers.
 * Scene unit = metres. Drawing coords map through scale S.
 */

/** Base drawing scale (drawing units → metres). */
export const drawingScale = 0.001;
export const S = drawingScale;

/** Map horizontal drawing coordinate → metres. */
export function X(u: number): number {
  return u * S;
}

/** Map vertical/elevation drawing coordinate → metres. */
export function Z(v: number): number {
  return v * S;
}

/** Translate a drawing X by an offset in drawing units. */
export function TX(u: number, du: number): number {
  return X(u + du);
}

/** Degrees → radians. */
export function deg(d: number): number {
  return (d * Math.PI) / 180;
}

export const pi = Math.PI;

/** Sample [start, end) into n steps (for circular detail). */
export function series(start: number, end: number, n: number): number[] {
  const out: number[] = [];
  if (n <= 0) return out;
  const step = (end - start) / n;
  for (let i = 0; i < n; i++) out.push(start + i * step);
  return out;
}

export type Pair = [number, number];
export type Triple = [number, number, number];
