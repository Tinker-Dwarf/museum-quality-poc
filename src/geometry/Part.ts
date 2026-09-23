import * as THREE from "three";
import type { Palette, PaletteKey } from "./materials";
import { pi } from "./parameters";

export type Vec2 = [number, number];

/**
 * Named Group builder — Part helper.
 * Procedural primitives (lathe/box/cyl/pipe/plate/torus/text).
 * finish(root) attaches the group.
 */
export class Part {
  readonly group: THREE.Group;
  readonly name: string;
  private mats: Palette;
  private shadow = true;

  constructor(name: string, mats: Palette) {
    this.name = name;
    this.mats = mats;
    this.group = new THREE.Group();
    this.group.name = name;
  }

  section(label: string): Part {
    const child = new Part(`${this.name}/${label}`, this.mats);
    this.group.add(child.group);
    return child;
  }

  private mat(key: PaletteKey): THREE.MeshStandardMaterial {
    return this.mats[key];
  }

  private mesh(
    geo: THREE.BufferGeometry,
    key: PaletteKey,
  ): THREE.Mesh {
    const m = new THREE.Mesh(geo, this.mat(key));
    if (this.shadow) {
      m.castShadow = true;
      m.receiveShadow = true;
    }
    this.group.add(m);
    return m;
  }

  /** Lathe profile: [radius, y] points, Y-up. */
  lathe(
    profile: Vec2[],
    key: PaletteKey,
    segments = 28,
    phiStart = 0,
    phiLength = pi * 2,
  ): THREE.Mesh {
    const pts = profile.map(([r, y]) => new THREE.Vector2(r, y));
    return this.mesh(
      new THREE.LatheGeometry(pts, segments, phiStart, phiLength),
      key,
    );
  }

  box(
    w: number,
    h: number,
    d: number,
    key: PaletteKey,
    at: [number, number, number] = [0, 0, 0],
  ): THREE.Mesh {
    const m = this.mesh(new THREE.BoxGeometry(w, h, d), key);
    m.position.set(at[0], at[1], at[2]);
    return m;
  }

  cylinder(
    rTop: number,
    rBot: number,
    h: number,
    key: PaletteKey,
    at: [number, number, number] = [0, 0, 0],
    segments = 20,
  ): THREE.Mesh {
    const m = this.mesh(
      new THREE.CylinderGeometry(rTop, rBot, h, segments),
      key,
    );
    m.position.set(at[0], at[1], at[2]);
    return m;
  }

  /** Thin wall tube along Y (pipe stub). */
  pipe(
    radius: number,
    length: number,
    key: PaletteKey,
    at: [number, number, number] = [0, 0, 0],
    radial = 12,
  ): THREE.Mesh {
    const m = this.mesh(
      new THREE.CylinderGeometry(radius, radius, length, radial),
      key,
    );
    m.position.set(at[0], at[1], at[2]);
    return m;
  }

  /** Tube along a path (CatmullRom). */
  tube(
    points: THREE.Vector3[],
    radius: number,
    key: PaletteKey,
    tubular = 32,
    radial = 8,
  ): THREE.Mesh {
    const curve = new THREE.CatmullRomCurve3(points);
    return this.mesh(
      new THREE.TubeGeometry(curve, tubular, radius, radial, false),
      key,
    );
  }

  plate(
    w: number,
    h: number,
    thickness: number,
    key: PaletteKey,
    at: [number, number, number] = [0, 0, 0],
  ): THREE.Mesh {
    return this.box(w, thickness, h, key, at);
  }

  torus(
    radius: number,
    tube: number,
    key: PaletteKey,
    at: [number, number, number] = [0, 0, 0],
    radial = 16,
    tubular = 24,
  ): THREE.Mesh {
    const m = this.mesh(
      new THREE.TorusGeometry(radius, tube, radial, tubular),
      key,
    );
    m.position.set(at[0], at[1], at[2]);
    return m;
  }

  /** Canvas texture lettering on a thin plate facing +Z by default. */
  text(
    content: string,
    opts: {
      width: number;
      height: number;
      key?: PaletteKey;
      at?: [number, number, number];
      color?: string;
      bg?: string;
      font?: string;
      align?: CanvasTextAlign;
    },
  ): THREE.Mesh {
    const {
      width,
      height,
      key = "dark",
      at = [0, 0, 0],
      color = "#f4f1ea",
      bg = "transparent",
      font = "600 64px 'IBM Plex Sans', sans-serif",
      align = "center",
    } = opts;
    const canvas = document.createElement("canvas");
    canvas.width = 512;
    canvas.height = Math.max(64, Math.round(512 * (height / width)));
    const ctx = canvas.getContext("2d")!;
    if (bg !== "transparent") {
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    ctx.fillStyle = color;
    ctx.textAlign = align;
    ctx.textBaseline = "middle";
    const lines = content.split("\n");
    const lineH = canvas.height / (lines.length + 0.5);
    // Fit each line inside the canvas with side padding so leading glyphs (e.g. C in COMMODORE) never clip
    const pad = 28;
    const maxW = canvas.width - pad * 2;
    lines.forEach((line, i) => {
      let useFont = font;
      ctx.font = useFont;
      let metrics = ctx.measureText(line);
      if (metrics.width > maxW) {
        const m = /([\d.]+)px/.exec(font);
        if (m) {
          const px = parseFloat(m[1]);
          const scaled = Math.max(10, Math.floor(px * (maxW / metrics.width)));
          useFont = font.replace(/[\d.]+px/, `${scaled}px`);
          ctx.font = useFont;
        }
      }
      const x = align === "left" ? pad : canvas.width / 2;
      ctx.fillText(line, x, lineH * (i + 0.75));
    });
    const tex = new THREE.CanvasTexture(canvas);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 4;
    const mat = new THREE.MeshStandardMaterial({
      map: tex,
      transparent: true,
      roughness: 0.85,
      metalness: 0.05,
      color: 0xffffff,
    });
    const geo = new THREE.PlaneGeometry(width, height);
    const m = new THREE.Mesh(geo, mat);
    m.position.set(at[0], at[1], at[2]);
    m.castShadow = false;
    m.receiveShadow = false;
    this.group.add(m);
    // Keep a backing plate for silhouette when bg transparent
    void key;
    return m;
  }

  setPosition(x: number, y: number, z: number): this {
    this.group.position.set(x, y, z);
    return this;
  }

  setRotation(rx: number, ry: number, rz: number): this {
    this.group.rotation.set(rx, ry, rz);
    return this;
  }

  /** Attach to parent and return this group. */
  finish(root: THREE.Object3D): THREE.Group {
    root.add(this.group);
    return this.group;
  }
}
