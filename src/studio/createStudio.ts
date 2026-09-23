import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { buildOuray, type LocoBuilt } from "../models/ouray";
import { buildVanderbilt } from "../models/vanderbilt";
import { palette } from "../geometry/materials";

export type ViewMode = "both" | "ouray" | "vanderbilt";

export type StudioApi = {
  setExplode: (t: number) => void;
  setView: (v: ViewMode) => void;
  setTrueScale: (on: boolean) => void;
  setRolling: (play: boolean, speedMs: number) => void;
  setSteam: (on: boolean) => void;
  getRpm: () => { ouray: number; vanderbilt: number };
  getSpeed: () => { ms: number; mph: number; kmh: number };
  getPartIds: () => { ourayIds: string[]; vanderbiltIds: string[] };
  dispose: () => void;
};

const STUDIO = 0xf4f1ea;
/** Parallel lanes along +X; separated in Z. Vanderbilt farther, Ouray nearer. */
const OURAY_Z = 2.0;
const VANDY_Z = -2.2;
/** Light-gray museum pedestals (slab height); cream void remains around them. */
const PEDESTAL_H = 0.14;
const PEDESTAL_COLOR = 0xe2e0da;
/** Short track ≈ loco+tender + small overhang (museum-default; no long floor rails). */
const OURAY_TRACK_LEN = 12.0;
const VANDY_TRACK_LEN = 17.5;
/** Track / pedestal center X in each loco's local frame (mid consist). */
const OURAY_TRACK_CX = 0.95;
const VANDY_TRACK_CX = 2.25;

export type StudioOptions = {
  mount: HTMLElement;
};

export function createStudio(opts: StudioOptions): StudioApi {
  const { mount } = opts;
  let trueScale = true;
  let view: ViewMode = "both";
  let rolling = false;
  let rollSpeed = mphToMs(12); // default ~12 mph
  let rollDistance = 0;
  let steamOn = false;
  let explodeT = 0;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(STUDIO);

  const camera = new THREE.PerspectiveCamera(
    32,
    mount.clientWidth / Math.max(mount.clientHeight, 1),
    0.05,
    200,
  );
  camera.position.set(-7.6, 8.8, 14.2);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(mount.clientWidth, mount.clientHeight);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.NeutralToneMapping;
  renderer.toneMappingExposure = 1.35;
  mount.appendChild(renderer.domElement);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.target.set(0.55, 0.55, -0.1);
  controls.maxPolarAngle = Math.PI * 0.49;

  scene.add(new THREE.AmbientLight(0xf4f1ea, 0.95));
  scene.add(new THREE.HemisphereLight(0xfffaf2, 0xe4ddd0, 1.05));
  const key = new THREE.DirectionalLight(0xfff6e8, 1.25);
  key.position.set(9, 18, 8);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  key.shadow.radius = 8;
  key.shadow.bias = -0.00015;
  key.shadow.normalBias = 0.02;
  key.shadow.camera.near = 0.5;
  key.shadow.camera.far = 60;
  key.shadow.camera.left = -16;
  key.shadow.camera.right = 16;
  key.shadow.camera.top = 16;
  key.shadow.camera.bottom = -16;
  scene.add(key);

  // Stronger camera-side fill so undercarriage iron/steel separates from cream void
  const fill = new THREE.DirectionalLight(0xf2f4f8, 0.85);
  fill.position.set(-8, 9, 10);
  scene.add(fill);

  // Low bounce / undercarriage lift — kills value crush on tires, spokes, rods
  const bounce = new THREE.DirectionalLight(0xfff8f0, 0.75);
  bounce.position.set(2, 1.2, 8);
  scene.add(bounce);
  const underFill = new THREE.DirectionalLight(0xf0ebe3, 0.65);
  underFill.position.set(-2, 0.6, 6);
  scene.add(underFill);
  const underFill2 = new THREE.DirectionalLight(0xffffff, 0.35);
  underFill2.position.set(6, 2.0, 10);
  scene.add(underFill2);

  // Rim from behind + near-side kick for wheel faces in skirt cutouts
  const rim = new THREE.DirectionalLight(0xffffff, 0.48);
  rim.position.set(-4, 6, -12);
  scene.add(rim);
  const wheelKick = new THREE.DirectionalLight(0xfff5ea, 0.4);
  wheelKick.position.set(4, 3.5, 14);
  scene.add(wheelKick);

  // Cream museum void floor — pedestals sit on it; no long floor rails
  const groundMat = new THREE.MeshStandardMaterial({
    color: 0xf4f1ea,
    roughness: 0.97,
    metalness: 0.0,
  });
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(120, 60), groundMat);
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.002;
  ground.receiveShadow = true;
  scene.add(ground);

  // Soft contact catcher on the cream (very light) — primary contact is on pedestals
  const shadowGround = new THREE.Mesh(
    new THREE.PlaneGeometry(40, 24),
    new THREE.ShadowMaterial({ opacity: 0.08 }),
  );
  shadowGround.rotation.x = -Math.PI / 2;
  shadowGround.position.y = 0.001;
  shadowGround.receiveShadow = true;
  scene.add(shadowGround);

  // G1+G2: light-gray pedestals + short track segments (museum-default)
  const ourayPedestal = buildMuseumPedestal({
    length: OURAY_TRACK_LEN + 0.9,
    width: 2.55,
    cx: OURAY_TRACK_CX,
    cz: OURAY_Z,
  });
  scene.add(ourayPedestal);
  ourayPedestal.add(buildShortTrack(OURAY_TRACK_LEN, 0));

  const vandyPedestal = buildMuseumPedestal({
    length: VANDY_TRACK_LEN + 1.0,
    width: 2.85,
    cx: -1.5 + VANDY_TRACK_CX,
    cz: VANDY_Z,
  });
  scene.add(vandyPedestal);
  vandyPedestal.add(buildShortTrack(VANDY_TRACK_LEN, 0));

  const ourayAnchor = new THREE.Group();
  ourayAnchor.name = "ouray-anchor";
  ourayAnchor.position.set(0, PEDESTAL_H, OURAY_Z);
  scene.add(ourayAnchor);

  const vandyAnchor = new THREE.Group();
  vandyAnchor.name = "vanderbilt-anchor";
  vandyAnchor.position.set(-1.5, PEDESTAL_H, VANDY_Z);
  scene.add(vandyAnchor);

  const ouray: LocoBuilt = buildOuray();
  const vanderbilt: LocoBuilt = buildVanderbilt();
  // Face +X (travel direction)
  ourayAnchor.add(ouray.root);
  vandyAnchor.add(vanderbilt.root);

  // Soft steam wisps (simple particle stubs from stacks)
  const steamOuray = makeSteamWisp();
  steamOuray.position.set(-2.55, 3.1, 0);
  steamOuray.visible = false;
  ouray.root.add(steamOuray);
  const steamVandy = makeSteamWisp();
  steamVandy.position.set(-5.5, 3.0, 0);
  steamVandy.visible = false;
  vanderbilt.root.add(steamVandy);

  function applyScale() {
    // True scale ON = relative honest sizes (already built that way).
    // Equalize shrinks Vanderbilt toward Ouray visual weight.
    const s = trueScale ? 1 : 0.55;
    vanderbilt.root.scale.setScalar(s);
  }
  applyScale();

  function setExplode(t: number) {
    explodeT = t;
    ouray.setExplode(t);
    vanderbilt.setExplode(t);
  }

  function frameView(v: ViewMode) {
    view = v;
    ourayAnchor.visible = v === "both" || v === "ouray";
    vandyAnchor.visible = v === "both" || v === "vanderbilt";

    const ox = ourayAnchor.position.x;
    const vx = vandyAnchor.position.x;

    const py = PEDESTAL_H;
    if (v === "ouray") {
      camera.position.set(ox + OURAY_TRACK_CX - 5.2, py + 3.6, OURAY_Z + 6.2);
      controls.target.set(ox + OURAY_TRACK_CX - 0.2, py + 1.15, OURAY_Z);
    } else if (v === "vanderbilt") {
      const s = trueScale ? 1 : 0.55;
      camera.position.set(vx + VANDY_TRACK_CX - 6.5 * s, py + 3.4 * s, VANDY_Z + 11 * s);
      controls.target.set(vx + VANDY_TRACK_CX + 0.2, py + 1.25 * s, VANDY_Z);
    } else {
      // Museum three-quarter: higher, tighter on the pedestal pair
      camera.position.set(-7.6, 8.8, 14.2);
      controls.target.set(0.55, py + 0.35, -0.1);
    }
    controls.update();
  }

  function setView(v: ViewMode) {
    frameView(v);
  }

  function setTrueScale(on: boolean) {
    trueScale = on;
    applyScale();
    frameView(view);
  }

  function setRolling(play: boolean, speedMs: number) {
    rolling = play;
    rollSpeed = speedMs;
  }

  function setSteam(on: boolean) {
    steamOn = on;
    steamOuray.visible = on;
    steamVandy.visible = on;
  }

  function getRpm() {
    const v = rolling ? rollSpeed : 0;
    return {
      ouray: msToRpm(v, ouray.driverRadius),
      vanderbilt: msToRpm(v, vanderbilt.driverRadius),
    };
  }

  function getSpeed() {
    return {
      ms: rollSpeed,
      mph: msToMph(rollSpeed),
      kmh: msToKmh(rollSpeed),
    };
  }

  function getPartIds() {
    return {
      ourayIds: [...ouray.explodeGroups.keys()],
      vanderbiltIds: [...vanderbilt.explodeGroups.keys()],
    };
  }

  const clock = new THREE.Clock();
  let alive = true;
  let frame = 0;

  function tick() {
    if (!alive) return;
    const dt = Math.min(clock.getDelta(), 0.05);
    const t = clock.elapsedTime;

    if (rolling && explodeT < 0.05) {
      const dx = rollSpeed * dt;
      rollDistance += dx;
      if (ourayAnchor.visible) {
        ourayAnchor.position.x = rollDistance;
        spinWheels(ouray, dx);
      }
      if (vandyAnchor.visible) {
        vandyAnchor.position.x = -1.5 + rollDistance;
        spinWheels(vanderbilt, dx);
      }
    }

    // Animate steam wisps
    if (steamOn) {
      animateSteam(steamOuray, t, 1);
      animateSteam(steamVandy, t, 0.7);
    }

    controls.update();
    renderer.render(scene, camera);
    frame = requestAnimationFrame(tick);
  }
  frame = requestAnimationFrame(tick);

  function onResize() {
    camera.aspect = mount.clientWidth / Math.max(mount.clientHeight, 1);
    camera.updateProjectionMatrix();
    renderer.setSize(mount.clientWidth, mount.clientHeight);
  }
  window.addEventListener("resize", onResize);

  // Initial framing
  frameView("both");

  function dispose() {
    alive = false;
    cancelAnimationFrame(frame);
    window.removeEventListener("resize", onResize);
    controls.dispose();
    renderer.dispose();
    if (renderer.domElement.parentNode === mount) {
      mount.removeChild(renderer.domElement);
    }
  }

  return {
    setExplode,
    setView,
    setTrueScale,
    setRolling,
    setSteam,
    getRpm,
    getSpeed,
    getPartIds,
    dispose,
  };
}

/** Light-gray museum slab; soft contact shadow blob on top. Local origin = slab center top. */
function buildMuseumPedestal(opts: {
  length: number;
  width: number;
  cx: number;
  cz: number;
}): THREE.Group {
  const g = new THREE.Group();
  g.name = "museum-pedestal";
  g.position.set(opts.cx, PEDESTAL_H, opts.cz);

  const mat = new THREE.MeshStandardMaterial({
    color: PEDESTAL_COLOR,
    roughness: 0.92,
    metalness: 0.02,
  });
  const slab = new THREE.Mesh(
    new THREE.BoxGeometry(opts.length, PEDESTAL_H, opts.width),
    mat,
  );
  slab.position.set(0, -PEDESTAL_H / 2, 0);
  slab.receiveShadow = true;
  slab.castShadow = true;
  g.add(slab);

  // Soft contact shadow on pedestal top (under consist / short track)
  const contact = new THREE.Mesh(
    new THREE.PlaneGeometry(opts.length * 0.88, opts.width * 0.62),
    new THREE.MeshBasicMaterial({
      color: 0x2a2824,
      transparent: true,
      opacity: 0.08,
      depthWrite: false,
    }),
  );
  contact.rotation.x = -Math.PI / 2;
  contact.position.y = 0.004;
  contact.receiveShadow = false;
  g.add(contact);

  const shadowCatch = new THREE.Mesh(
    new THREE.PlaneGeometry(opts.length * 0.98, opts.width * 0.95),
    new THREE.ShadowMaterial({ opacity: 0.18 }),
  );
  shadowCatch.rotation.x = -Math.PI / 2;
  shadowCatch.position.y = 0.006;
  shadowCatch.receiveShadow = true;
  g.add(shadowCatch);

  return g;
}

/** Short ties + rails centered at local origin on a pedestal top. */
function buildShortTrack(length: number, localZ = 0): THREE.Group {
  const mats = palette();
  const gauge = 1.05;
  const lane = new THREE.Group();
  lane.name = "short-track";
  lane.position.set(0, 0, localZ);

  const half = length / 2;
  const spacing = 0.72;
  const i0 = Math.ceil((-half + 0.15) / spacing);
  const i1 = Math.floor((half - 0.15) / spacing);
  for (let i = i0; i <= i1; i++) {
    const tie = new THREE.Mesh(
      new THREE.BoxGeometry(0.22, 0.08, gauge + 0.45),
      mats.wood,
    );
    tie.position.set(i * spacing, 0.04, 0);
    tie.receiveShadow = true;
    tie.castShadow = true;
    lane.add(tie);
  }
  for (const dz of [-gauge / 2, gauge / 2]) {
    const rail = new THREE.Mesh(
      new THREE.BoxGeometry(length, 0.06, 0.08),
      mats.rail,
    );
    rail.position.set(0, 0.1, dz);
    rail.castShadow = true;
    rail.receiveShadow = true;
    lane.add(rail);
  }
  return lane;
}

function spinWheels(built: LocoBuilt, dx: number) {
  for (const w of built.wheels) {
    const omega = dx / w.radius;
    w.group.rotation.z -= omega;
  }
}

function makeSteamWisp(): THREE.Group {
  const g = new THREE.Group();
  g.name = "steam";
  const mat = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    transparent: true,
    opacity: 0.14,
    roughness: 1,
    metalness: 0,
    depthWrite: false,
  });
  for (let i = 0; i < 6; i++) {
    const s = 0.12 + i * 0.055;
    const m = new THREE.Mesh(new THREE.SphereGeometry(s, 12, 12), mat.clone());
    m.position.set(i * 0.1, 0.2 + i * 0.32, (i % 2) * 0.08 - 0.04);
    g.add(m);
  }
  return g;
}

function animateSteam(g: THREE.Group, t: number, scale: number) {
  g.children.forEach((c, i) => {
    const m = c as THREE.Mesh;
    m.position.y = i * 0.35 * scale + Math.sin(t * 1.4 + i) * 0.08;
    m.position.x = i * 0.12 + Math.cos(t * 0.9 + i * 0.7) * 0.06;
    const mat = m.material as THREE.MeshStandardMaterial;
    mat.opacity = 0.1 + 0.05 * Math.sin(t * 2 + i);
    const s = (0.2 + i * 0.08) * (1 + 0.15 * Math.sin(t + i));
    m.scale.setScalar(s / (0.2 + i * 0.08));
  });
}

export function mphToMs(mph: number): number {
  return mph * 0.44704;
}
export function msToMph(ms: number): number {
  return ms / 0.44704;
}
export function msToKmh(ms: number): number {
  return ms * 3.6;
}
export function msToRpm(ms: number, radius: number): number {
  if (radius <= 0 || ms <= 0) return 0;
  return (ms / radius) * (60 / (2 * Math.PI));
}
