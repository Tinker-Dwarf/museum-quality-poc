import * as THREE from "three";
import { Part } from "../../geometry/Part";
import { palette } from "../../geometry/materials";
import { pi, series } from "../../geometry/parameters";

export type WheelNode = {
  group: THREE.Group;
  radius: number;
};

export type LocoBuilt = {
  root: THREE.Group;
  explodeGroups: Map<string, THREE.Object3D>;
  wheels: WheelNode[];
  driverRadius: number;
  setExplode: (t: number) => void;
  label: string;
  id: string;
};

/** Driver radius tuned so 12 mph ≈ 68 rpm (ω = v/r). */
export const OURAY_DRIVER_R = 0.75;

/**
 * Ouray — Silverton mountain workhorse, modeled to the Krcha reference.
 * Charcoal cab/tender, light-gray boiler, diamond stack, cowcatcher, open-spoke drivers (museum still).
 * Codie densify pass (INGOT-101 / Stallari DoD): procedural Part geometry only.
 */
export function buildOuray(): LocoBuilt {
  const mats = palette();
  const root = new THREE.Group();
  root.name = "ouray";
  const explodeGroups = new Map<string, THREE.Object3D>();
  const wheels: WheelNode[] = [];
  const rest = new Map<string, THREE.Vector3>();

  const register = (
    name: string,
    obj: THREE.Object3D,
    explode: [number, number, number],
  ) => {
    obj.name = name;
    obj.userData.explode = new THREE.Vector3(...explode);
    rest.set(name, obj.position.clone());
    explodeGroups.set(name, obj);
    root.add(obj);
  };

  // —— Frame / chassis spar ——
  const chassis = new Part("ouray/chassis", mats);
  chassis.box(7.2, 0.14, 0.9, "iron", [0, 0.55, 0]);
  chassis.box(7.0, 0.08, 0.55, "steel", [0, 0.48, 0]);
  // Outer frame rails + pedestal legs under driver bays
  for (const s of [-1, 1] as const) {
    chassis.box(7.0, 0.1, 0.06, "iron", [0, 0.42, s * 0.42]);
    for (const x of [-1.85, -0.55, 0.75, 2.05]) {
      chassis.box(0.12, 0.38, 0.08, "iron", [x, 0.28, s * 0.42]);
      chassis.box(0.22, 0.06, 0.14, "steel", [x, 0.12, s * 0.42]);
    }
  }
  // End sills
  chassis.box(0.14, 0.2, 0.95, "iron", [-3.55, 0.5, 0]);
  chassis.box(0.14, 0.2, 0.95, "iron", [3.55, 0.5, 0]);
  chassis.finish(root);

  // —— Pilot / slatted cowcatcher ——
  const pilot = new Part("ouray/pilot", mats);
  pilot.box(0.16, 0.28, 1.25, "iron", [-3.5, 0.48, 0]);
  // Beam caps / footboards
  pilot.box(0.12, 0.06, 1.3, "steel", [-3.5, 0.64, 0]);
  const apexX = -4.4;
  const beamX = -3.45;
  const topY = 0.66;
  const botY = 0.12;
  const nSlats = 11;
  for (let i = 0; i < nSlats; i++) {
    const f = (i / (nSlats - 1)) * 2 - 1;
    const z = f * 0.52;
    const frontX = apexX + Math.abs(f) * 0.5;
    const dx = frontX - beamX;
    const dy = botY - topY;
    const len = Math.hypot(dx, dy);
    const bar = pilot.box(len, 0.045, 0.035, "iron", [
      (beamX + frontX) / 2,
      (topY + botY) / 2,
      z,
    ]);
    bar.rotation.z = Math.atan2(dy, dx);
  }
  for (const s of [-1, 1] as const) {
    const railLen = Math.hypot(beamX - apexX, 0.52);
    const rail = pilot.box(railLen, 0.05, 0.05, "iron", [
      (beamX + apexX) / 2,
      botY,
      s * 0.26,
    ]);
    rail.rotation.y = -Math.atan2(0.52, apexX - beamX) * s;
  }
  // Cross ties on cowcatcher
  for (const y of [0.28, 0.48]) {
    pilot.box(0.04, 0.035, 1.0, "steel", [-3.85, y, 0]);
  }
  // Coupler pocket + knuckle stub
  pilot.box(0.22, 0.18, 0.22, "iron", [-3.62, 0.48, 0]);
  const coupler = pilot.cylinder(0.055, 0.055, 0.28, "steel", [-3.82, 0.48, 0]);
  coupler.rotation.z = pi / 2;
  pilot.box(0.1, 0.12, 0.14, "steel", [-3.98, 0.48, 0]);
  // Flag / marker staffs on buffer ends
  for (const s of [-1, 1] as const) {
    pilot.pipe(0.015, 0.35, "steel", [-3.48, 0.78, s * 0.55], 6);
    pilot.cylinder(0.04, 0.04, 0.04, "trim", [-3.48, 0.96, s * 0.55], 8);
  }
  pilot.setPosition(0, 0, 0);
  register("pilot", pilot.group, [-1.4, 0.1, 0]);

  // —— Cylinders L/R ——
  const cylinders = new Part("ouray/cylinders", mats);
  for (const s of [-1, 1] as const) {
    // Steam chest / saddle block
    cylinders.box(0.55, 0.42, 0.38, "iron", [-2.55, 0.95, s * 0.72]);
    // Cylinder body (axis along X)
    cylinders.cylinder(0.28, 0.28, 0.85, "iron", [-2.4, 0.72, s * 0.72], 24);
    const c = cylinders.group.children[cylinders.group.children.length - 1];
    c.rotation.z = pi / 2;
    // Front / rear cylinder heads
    const headF = cylinders.cylinder(0.3, 0.3, 0.06, "steel", [-2.85, 0.72, s * 0.72], 20);
    headF.rotation.z = pi / 2;
    const headR = cylinders.cylinder(0.3, 0.3, 0.06, "steel", [-1.95, 0.72, s * 0.72], 20);
    headR.rotation.z = pi / 2;
    // Packing gland + piston rod stub
    const gland = cylinders.cylinder(0.1, 0.1, 0.12, "steel", [-1.88, 0.72, s * 0.72], 12);
    gland.rotation.z = pi / 2;
    cylinders.cylinder(0.05, 0.05, 0.55, "steel", [-1.55, 0.72, s * 0.72], 10);
    const p = cylinders.group.children[cylinders.group.children.length - 1];
    p.rotation.z = pi / 2;
    // Crosshead guide bars
    cylinders.box(0.55, 0.04, 0.04, "steel", [-1.45, 0.86, s * 0.72]);
    cylinders.box(0.55, 0.04, 0.04, "steel", [-1.45, 0.58, s * 0.72]);
    // Crosshead block
    cylinders.box(0.16, 0.18, 0.1, "iron", [-1.22, 0.72, s * 0.72]);
    // Valve stem chest detail on top
    cylinders.box(0.35, 0.1, 0.16, "dark", [-2.45, 1.18, s * 0.72]);
  }
  register("cylinders", cylinders.group, [0, 0.3, 0.9]);

  // —— Boiler + smokebox ——
  const boiler = new Part("ouray/boiler", mats);
  const smokebox = boiler.cylinder(0.6, 0.6, 1.15, "dark", [-2.5, 1.35, 0], 28);
  smokebox.rotation.z = pi / 2;
  // Smokebox saddle into frames
  boiler.box(1.0, 0.35, 0.85, "dark", [-2.5, 0.95, 0]);
  // Front smokebox ring / flange
  const smokeRing = boiler.torus(0.61, 0.028, "iron", [-3.08, 1.35, 0], 12, 28);
  smokeRing.rotation.y = pi / 2;
  const barrel = boiler.cylinder(0.62, 0.62, 3.35, "shell", [-0.28, 1.38, 0], 28);
  barrel.rotation.z = pi / 2;
  // Jacket bands (polished trim)
  for (const x of [-1.5, -0.75, 0.0, 0.75, 1.4]) {
    const t = boiler.torus(0.635, 0.022, "trim", [x, 1.38, 0], 12, 32);
    t.rotation.y = pi / 2;
  }
  // Handrail stanchions along boiler sides (pair of short posts per band)
  for (const s of [-1, 1] as const) {
    for (const x of [-1.9, -1.1, -0.3, 0.5, 1.2]) {
      boiler.pipe(0.012, 0.12, "steel", [x, 1.72, s * 0.64], 6);
    }
  }
  // Smokebox door — round face with cross handle + center boss
  const door = boiler.cylinder(0.52, 0.54, 0.08, "iron", [-3.11, 1.35, 0], 24);
  door.rotation.z = pi / 2;
  const doorRing = boiler.torus(0.53, 0.03, "steel", [-3.09, 1.35, 0], 12, 32);
  doorRing.rotation.y = pi / 2;
  boiler.box(0.05, 0.9, 0.045, "steel", [-3.15, 1.35, 0]);
  boiler.box(0.05, 0.045, 0.9, "steel", [-3.15, 1.35, 0]);
  const boss = boiler.cylinder(0.09, 0.09, 0.12, "trim", [-3.18, 1.35, 0], 14);
  boss.rotation.z = pi / 2;
  // Door hinges (right side of face)
  for (const dy of [-0.28, 0.0, 0.28]) {
    boiler.box(0.06, 0.08, 0.1, "steel", [-3.12, 1.35 + dy, 0.48]);
  }
  // Washout / inspection plug hints on firebox sides
  for (const s of [-1, 1] as const) {
    for (const [x, y] of [
      [1.35, 0.85],
      [1.55, 0.7],
      [1.75, 0.85],
    ] as const) {
      const plug = boiler.cylinder(0.04, 0.04, 0.06, "trim", [x, y, s * 0.6], 8);
      plug.rotation.x = pi / 2;
    }
  }
  // Firebox / boiler backhead swell into cab
  boiler.box(1.1, 1.0, 1.18, "dark", [1.6, 1.12, 0]);
  // Firebox foundation ring
  boiler.box(1.15, 0.08, 1.22, "iron", [1.6, 0.62, 0]);
  // Ashpan hint under firebox
  boiler.box(0.9, 0.18, 0.7, "dark", [1.55, 0.48, 0]);
  register("boiler", boiler.group, [0, 1.1, 0]);

  // —— Stack + domes + fittings (densify bullseye) ——
  const stackDomes = new Part("ouray/stack_domes", mats);
  const stackX = -2.55;
  const stackBaseY = 1.9;

  // Stack base flange on smokebox
  stackDomes.cylinder(0.22, 0.22, 0.06, "iron", [stackX, stackBaseY - 0.02, 0], 16);
  // Petticoat / stack throat
  stackDomes.lathe(
    [
      [0.14, 0],
      [0.16, 0.08],
      [0.15, 0.16],
    ],
    "iron",
    20,
  );
  stackDomes.group.children[stackDomes.group.children.length - 1].position.set(
    stackX,
    stackBaseY,
    0,
  );

  // Diamond / balloon stack (lathe) — denser profile + higher segment count
  stackDomes.lathe(
    [
      [0.12, 0],
      [0.13, 0.08],
      [0.14, 0.18],
      [0.16, 0.3],
      [0.22, 0.4],
      [0.38, 0.52],
      [0.5, 0.62],
      [0.55, 0.72],
      [0.52, 0.8],
      [0.42, 0.88],
      [0.26, 0.96],
      [0.19, 1.02],
      [0.17, 1.08],
    ],
    "iron",
    32,
  );
  stackDomes.group.children[stackDomes.group.children.length - 1].position.set(
    stackX,
    stackBaseY + 0.14,
    0,
  );

  // Spark screen — cage of thin pipes + rim rings
  const stackTopY = stackBaseY + 1.05;
  const screenR = 0.155;
  for (const a of series(0, pi * 2, 20)) {
    stackDomes.pipe(
      0.009,
      0.14,
      "steel",
      [stackX + Math.cos(a) * screenR, stackTopY + 0.07, Math.sin(a) * screenR],
      6,
    );
  }
  // Cross wires on screen
  for (const a of series(0, pi, 4)) {
    const wire = stackDomes.box(screenR * 2, 0.008, 0.008, "steel", [
      stackX,
      stackTopY + 0.07,
      0,
    ]);
    wire.rotation.y = a;
  }
  const rimLo = stackDomes.torus(0.16, 0.012, "trim", [stackX, stackTopY, 0], 10, 24);
  rimLo.rotation.x = pi / 2;
  const rimHi = stackDomes.torus(
    0.16,
    0.012,
    "trim",
    [stackX, stackTopY + 0.14, 0],
    10,
    24,
  );
  rimHi.rotation.x = pi / 2;
  // Screen cap disc
  stackDomes.cylinder(0.12, 0.12, 0.02, "iron", [stackX, stackTopY + 0.15, 0], 16);

  // Steam dome — shell body + trim crown / safety valves
  stackDomes.lathe(
    [
      [0.18, 0],
      [0.28, 0.05],
      [0.34, 0.12],
      [0.35, 0.22],
      [0.32, 0.32],
      [0.22, 0.4],
      [0.1, 0.44],
    ],
    "shell",
    28,
  );
  stackDomes.group.children[stackDomes.group.children.length - 1].position.set(
    -0.5,
    1.95,
    0,
  );
  stackDomes.torus(0.345, 0.02, "trim", [-0.5, 2.05, 0], 10, 24).rotation.x =
    pi / 2;
  stackDomes.torus(0.3, 0.018, "trim", [-0.5, 2.22, 0], 10, 20).rotation.x =
    pi / 2;
  // Dome crown / manhole cover
  stackDomes.lathe(
    [
      [0.1, 0],
      [0.18, 0.03],
      [0.16, 0.09],
      [0.05, 0.12],
    ],
    "trim",
    18,
  );
  stackDomes.group.children[stackDomes.group.children.length - 1].position.set(
    -0.5,
    2.36,
    0,
  );
  // Twin safety valves on steam dome
  for (const s of [-1, 1] as const) {
    stackDomes.pipe(0.025, 0.14, "trim", [-0.5 + s * 0.1, 2.5, 0], 8);
    stackDomes.cylinder(0.035, 0.02, 0.05, "steel", [-0.5 + s * 0.1, 2.58, 0], 8);
  }

  // Sand dome — shell + trim + delivery pipes
  stackDomes.lathe(
    [
      [0.12, 0],
      [0.2, 0.04],
      [0.26, 0.1],
      [0.27, 0.18],
      [0.22, 0.26],
      [0.12, 0.3],
      [0.05, 0.33],
    ],
    "shell",
    24,
  );
  stackDomes.group.children[stackDomes.group.children.length - 1].position.set(
    0.55,
    1.95,
    0,
  );
  stackDomes.torus(0.26, 0.016, "trim", [0.55, 2.04, 0], 8, 20).rotation.x =
    pi / 2;
  stackDomes.lathe(
    [
      [0.07, 0],
      [0.12, 0.025],
      [0.09, 0.07],
      [0.03, 0.09],
    ],
    "trim",
    14,
  );
  stackDomes.group.children[stackDomes.group.children.length - 1].position.set(
    0.55,
    2.26,
    0,
  );
  // Sand delivery pipes dropping to each side of the boiler
  for (const s of [-1, 1] as const) {
    stackDomes.tube(
      [
        new THREE.Vector3(0.55, 2.1, s * 0.08),
        new THREE.Vector3(0.55, 1.85, s * 0.35),
        new THREE.Vector3(0.55, 1.55, s * 0.68),
        new THREE.Vector3(0.2, 1.35, s * 0.72),
      ],
      0.018,
      "iron",
      16,
      6,
    );
  }

  // Lathe bell (trim shell profile)
  stackDomes.lathe(
    [
      [0.03, 0],
      [0.04, 0.03],
      [0.05, 0.08],
      [0.08, 0.12],
      [0.13, 0.17],
      [0.16, 0.22],
      [0.18, 0.28],
      [0.19, 0.32],
      [0.185, 0.35],
    ],
    "trim",
    24,
  );
  stackDomes.group.children[stackDomes.group.children.length - 1].position.set(
    -1.5,
    1.98,
    0,
  );
  // Bell yoke / hanger cradle
  stackDomes.box(0.32, 0.035, 0.04, "steel", [-1.5, 2.36, 0]);
  for (const s of [-1, 1] as const) {
    stackDomes.box(0.04, 0.12, 0.035, "steel", [-1.5 + s * 0.12, 2.3, 0]);
  }
  stackDomes.pipe(0.016, 0.2, "steel", [-1.5, 2.28, 0], 8);
  // Clapper
  stackDomes.pipe(0.012, 0.14, "dark", [-1.5, 2.1, 0], 6);
  stackDomes.cylinder(0.025, 0.025, 0.03, "iron", [-1.5, 2.02, 0], 8);

  // Whistle — multi-chime stub forward of cab
  stackDomes.pipe(0.03, 0.18, "trim", [0.05, 2.4, 0], 8);
  for (const s of [-1, 0, 1] as const) {
    stackDomes.pipe(0.014, 0.12 + Math.abs(s) * 0.02, "steel", [0.05 + s * 0.035, 2.54, 0], 6);
  }
  stackDomes.box(0.1, 0.025, 0.05, "trim", [0.05, 2.62, 0]);

  // Side handrails / steam lines along boiler
  for (const s of [-1, 1] as const) {
    stackDomes.tube(
      [
        new THREE.Vector3(-2.3, 1.72, s * 0.66),
        new THREE.Vector3(-1.2, 1.68, s * 0.7),
        new THREE.Vector3(0.2, 1.7, s * 0.7),
        new THREE.Vector3(1.35, 1.78, s * 0.62),
      ],
      0.028,
      "steel",
      28,
      6,
    );
    stackDomes.tube(
      [
        new THREE.Vector3(-2.0, 1.35, s * 0.7),
        new THREE.Vector3(-0.6, 1.28, s * 0.74),
        new THREE.Vector3(0.8, 1.32, s * 0.74),
        new THREE.Vector3(1.5, 1.45, s * 0.68),
      ],
      0.022,
      "iron",
      22,
      6,
    );
  }

  // Headlamp — housing, lens, bracket, number boards
  stackDomes.box(0.22, 0.22, 0.22, "iron", [-3.05, 1.95, 0]);
  const lampBody = stackDomes.cylinder(0.13, 0.14, 0.2, "trim", [-3.18, 1.95, 0], 18);
  lampBody.rotation.z = pi / 2;
  const lampLens = stackDomes.cylinder(0.11, 0.11, 0.04, "glass", [-3.3, 1.95, 0], 16);
  lampLens.rotation.z = pi / 2;
  // Bracket down to smokebox
  stackDomes.box(0.08, 0.35, 0.06, "steel", [-3.05, 1.72, 0]);
  stackDomes.box(0.2, 0.04, 0.08, "steel", [-3.05, 1.55, 0]);
  // Number boards flanking lamp
  for (const s of [-1, 1] as const) {
    stackDomes.box(0.04, 0.16, 0.28, "dark", [-3.12, 1.95, s * 0.22]);
    stackDomes.text("102", {
      width: 0.22,
      height: 0.12,
      at: [-3.15, 1.95, s * 0.24],
      color: "#f4f1ea",
      font: "700 64px 'IBM Plex Sans', sans-serif",
    });
    const nb = stackDomes.group.children[stackDomes.group.children.length - 1];
    nb.rotation.y = s > 0 ? 0.35 : -0.35 - pi;
  }
  // Dynamo / generator stub behind stack
  stackDomes.cylinder(0.07, 0.07, 0.14, "steel", [-2.15, 2.05, 0], 12);
  stackDomes.box(0.1, 0.06, 0.08, "iron", [-2.15, 1.95, 0]);

  register("stack_domes", stackDomes.group, [0, 1.6, 0]);

  // —— Cab ——
  const cab = new Part("ouray/cab", mats);
  cab.box(1.55, 1.45, 1.55, "olive", [2.55, 1.45, 0]);
  // Cab roof + overhang eave
  cab.box(1.65, 0.1, 1.7, "roof", [2.55, 2.2, 0]);
  cab.box(1.78, 0.05, 1.85, "roof", [2.55, 2.27, 0]);
  // Roof vents / stacking hatch
  cab.box(0.35, 0.08, 0.45, "dark", [2.35, 2.34, 0]);
  cab.box(0.25, 0.06, 0.3, "iron", [2.75, 2.33, 0]);
  // Window frames + panes (sides)
  for (const s of [-1, 1] as const) {
    cab.box(0.62, 0.52, 0.05, "dark", [2.55, 1.65, s * 0.78]);
    cab.box(0.52, 0.42, 0.04, "glass", [2.55, 1.65, s * 0.8]);
    // Forward cab window
    cab.box(0.08, 0.4, 0.35, "dark", [1.78, 1.7, s * 0.55]);
    cab.box(0.05, 0.32, 0.28, "glass", [1.76, 1.7, s * 0.55]);
    // Grab irons
    cab.tube(
      [
        new THREE.Vector3(1.85, 1.1, s * 0.8),
        new THREE.Vector3(1.85, 1.55, s * 0.8),
        new THREE.Vector3(1.85, 2.0, s * 0.8),
      ],
      0.016,
      "steel",
      8,
      6,
    );
  }
  // Side door openings (dark recess)
  for (const s of [-1, 1] as const) {
    cab.box(0.45, 0.85, 0.04, "dark", [2.95, 1.25, s * 0.78]);
  }
  // Number plate both sides
  for (const s of [-1, 1] as const) {
    cab.text("102", {
      width: 0.45,
      height: 0.28,
      at: [2.55, 1.85, s * 0.79],
      color: "#f4f1ea",
      bg: "#2a3224",
      font: "700 72px 'IBM Plex Sans', sans-serif",
    });
    if (s < 0) {
      const t = cab.group.children[cab.group.children.length - 1];
      t.rotation.y = pi;
    }
  }
  // Running boards + steps
  for (const s of [-1, 1] as const) {
    cab.box(5.5, 0.04, 0.22, "steel", [-0.2, 0.95, s * 0.72]);
    // Board edge lip
    cab.box(5.5, 0.03, 0.03, "iron", [-0.2, 0.97, s * 0.84]);
    // Cab steps
    for (const [x, y] of [
      [2.0, 0.55],
      [2.0, 0.75],
    ] as const) {
      cab.box(0.2, 0.03, 0.28, "steel", [x, y, s * 0.7]);
    }
  }
  register("cab", cab.group, [0.6, 1.2, 0]);

  // —— Drivers (open-spoke) ——
  const drivers = new THREE.Group();
  drivers.name = "drivers";
  const driverXs = [-1.85, -0.55, 0.75, 2.05];
  for (const x of driverXs) {
    const axle = buildOpenSpokeDriver(OURAY_DRIVER_R, mats);
    axle.position.set(x, OURAY_DRIVER_R, 0);
    drivers.add(axle);
    wheels.push({ group: axle, radius: OURAY_DRIVER_R });
  }
  // Coupling rods + main rods + crankpins
  const rod = new Part("ouray/rods", mats);
  const pin = OURAY_DRIVER_R + 0.34;
  for (const s of [-1, 1] as const) {
    const zc = s * 0.62;
    // Coupling rod with thickened big ends
    rod.box(4.0, 0.09, 0.045, "steel", [0.1, pin, zc]);
    for (const dx of driverXs) {
      rod.box(0.22, 0.14, 0.06, "iron", [dx, pin, zc]);
    }
    // Main rod from crosshead to 2nd driver
    const fx = -1.95;
    const fy = 0.75;
    const tx = -0.55;
    const ty = pin;
    const len = Math.hypot(tx - fx, ty - fy);
    const mr = rod.box(len, 0.08, 0.05, "steel", [
      (fx + tx) / 2,
      (fy + ty) / 2,
      zc,
    ]);
    mr.rotation.z = Math.atan2(ty - fy, tx - fx);
    // Crankpins
    for (const dx of driverXs) {
      const cp = rod.cylinder(0.055, 0.055, 0.12, "iron", [dx, pin, zc], 10);
      cp.rotation.x = pi / 2;
    }
    // Eccentric / return crank hint on lead driver
    rod.box(0.18, 0.05, 0.04, "steel", [-1.85, pin - 0.12, zc + s * 0.04]);
  }
  drivers.add(rod.group);
  register("drivers", drivers, [0, -0.9, 0]);

  // Leading pony truck (2-8-0 hint — single axle stub)
  const pony = new Part("ouray/pony", mats);
  const pr = 0.28;
  // Truck frame
  pony.box(0.7, 0.08, 0.85, "iron", [-3.15, 0.22, 0]);
  pony.box(0.5, 0.1, 0.12, "steel", [-3.15, 0.35, 0]);
  for (const s of [-1, 1] as const) {
    pony.cylinder(pr, pr, 0.1, "dark", [-3.15, pr, s * 0.45], 18);
    const w = pony.group.children[pony.group.children.length - 1];
    w.rotation.x = pi / 2;
    // Hub
    const hub = pony.cylinder(pr * 0.25, pr * 0.25, 0.12, "steel", [-3.15, pr, s * 0.45], 10);
    hub.rotation.x = pi / 2;
  }
  // Axle
  const ponyAxle = pony.cylinder(0.04, 0.04, 1.0, "steel", [-3.15, pr, 0], 8);
  ponyAxle.rotation.x = pi / 2;
  pony.finish(root);

  // —— Tender ——
  const tender = new Part("ouray/tender", mats);
  tender.box(2.6, 1.35, 1.5, "olive", [4.55, 1.15, 0]);
  // Rear water-tank deck; bunker left open at the front
  tender.box(1.35, 0.1, 1.54, "roof", [5.15, 1.86, 0]);
  // Deck hatch / filler
  tender.cylinder(0.18, 0.18, 0.06, "iron", [5.35, 1.94, 0], 12);
  tender.cylinder(0.08, 0.08, 0.08, "steel", [5.35, 2.0, 0], 8);
  // Bunker walls
  for (const s of [-1, 1] as const) {
    tender.box(1.7, 0.34, 0.08, "olive", [3.95, 1.98, s * 0.73]);
    // Top rail
    tender.box(1.7, 0.04, 0.04, "iron", [3.95, 2.16, s * 0.73]);
  }
  tender.box(0.08, 0.34, 1.52, "olive", [3.25, 1.98, 0]);
  // Heaped coal in the bunker
  for (const [cx, cz, ch] of [
    [3.7, 0, 0.42],
    [3.95, -0.34, 0.34],
    [3.95, 0.34, 0.34],
    [4.2, 0, 0.4],
    [4.25, -0.28, 0.3],
    [4.25, 0.3, 0.3],
    [4.55, 0, 0.28],
    [3.55, -0.2, 0.28],
    [3.55, 0.22, 0.26],
  ] as const) {
    const lump = tender.box(0.38, ch, 0.38, "dark", [cx, 1.82 + ch / 2, cz]);
    lump.rotation.y = cx * 0.4;
    lump.rotation.z = 0.25;
  }
  // Toolboxes on tender sides
  for (const s of [-1, 1] as const) {
    tender.box(0.55, 0.28, 0.18, "dark", [5.2, 0.7, s * 0.78]);
  }
  // Rear ladder
  for (const y of [0.7, 0.95, 1.2, 1.45, 1.7]) {
    tender.box(0.28, 0.03, 0.04, "steel", [5.88, y, 0]);
  }
  for (const s of [-1, 1] as const) {
    tender.box(0.03, 1.15, 0.03, "steel", [5.88, 1.2, s * 0.12]);
  }
  // Tender trucks with frames
  for (const x of [3.85, 5.15]) {
    tender.box(0.55, 0.08, 0.95, "iron", [x, 0.18, 0]);
    for (const s of [-1, 1] as const) {
      tender.cylinder(0.28, 0.28, 0.1, "dark", [x, 0.28, s * 0.5], 16);
      const w = tender.group.children[tender.group.children.length - 1];
      w.rotation.x = pi / 2;
      const hub = tender.cylinder(0.07, 0.07, 0.12, "steel", [x, 0.28, s * 0.5], 8);
      hub.rotation.x = pi / 2;
    }
  }
  // Lettering both sides
  for (const s of [-1, 1] as const) {
    tender.text("SILVERTON R.R. NO. 102", {
      width: 2.2,
      height: 0.28,
      at: [4.55, 1.25, s * 0.76],
      color: "#f4f1ea",
      font: "600 44px 'IBM Plex Sans', sans-serif",
    });
    if (s < 0) {
      tender.group.children[tender.group.children.length - 1].rotation.y = pi;
    }
    // Number folded into "SILVERTON R.R. NO. 102" line (still match)
  }
  register("tender", tender.group, [1.5, 0.4, 0]);

  function setExplode(t: number) {
    const k = Math.min(1, Math.max(0, t));
    const names = [...explodeGroups.keys()];
    names.forEach((name, i) => {
      const obj = explodeGroups.get(name)!;
      const base = rest.get(name)!;
      const exp = obj.userData.explode as THREE.Vector3;
      const delay = i * 0.08;
      const local = Math.min(1, Math.max(0, (k - delay) / (1 - delay * 0.5)));
      const e = local * local * (3 - 2 * local);
      obj.position.set(
        base.x + exp.x * e,
        base.y + exp.y * e,
        base.z + exp.z * e,
      );
    });
  }

  return {
    root,
    explodeGroups,
    wheels,
    driverRadius: OURAY_DRIVER_R,
    setExplode,
    label: "Ouray",
    id: "ouray",
  };
}

function buildOpenSpokeDriver(
  r: number,
  mats: ReturnType<typeof palette>,
): THREE.Group {
  const g = new THREE.Group();
  // Tire / rim with flange (lathe)
  const tire = new THREE.Mesh(
    new THREE.LatheGeometry(
      [
        new THREE.Vector2(r * 0.5, -0.055),
        new THREE.Vector2(r * 0.88, -0.065),
        new THREE.Vector2(r * 0.98, -0.05),
        new THREE.Vector2(r, -0.035),
        new THREE.Vector2(r, 0.04),
        new THREE.Vector2(r * 1.04, 0.05),
        new THREE.Vector2(r * 1.04, 0.07),
        new THREE.Vector2(r * 0.98, 0.06),
        new THREE.Vector2(r * 0.88, 0.065),
        new THREE.Vector2(r * 0.5, 0.055),
      ],
      32,
    ),
    mats.dark,
  );
  tire.rotation.x = pi / 2;
  tire.castShadow = true;
  g.add(tire);

  // Hub
  const hub = new THREE.Mesh(
    new THREE.CylinderGeometry(r * 0.16, r * 0.18, 0.16, 16),
    mats.steel,
  );
  hub.rotation.x = pi / 2;
  hub.castShadow = true;
  g.add(hub);

  // Axle ends
  for (const z of [-0.12, 0.12]) {
    const ax = new THREE.Mesh(
      new THREE.CylinderGeometry(r * 0.06, r * 0.06, 0.08, 10),
      mats.steel,
    );
    ax.rotation.x = pi / 2;
    ax.position.z = z;
    g.add(ax);
  }

  // Open spokes
  const spokeN = 14;
  for (let i = 0; i < spokeN; i++) {
    const a = (i / spokeN) * pi * 2;
    const spoke = new THREE.Mesh(
      new THREE.BoxGeometry(r * 0.76, 0.032, 0.04),
      mats.steel,
    );
    spoke.position.set(Math.cos(a) * r * 0.42, Math.sin(a) * r * 0.42, 0);
    spoke.rotation.z = a;
    spoke.castShadow = true;
    g.add(spoke);
  }

  // Crescent counterweight filling spoke bays
  const cw = new THREE.Mesh(
    new THREE.CylinderGeometry(
      r * 0.78,
      r * 0.78,
      0.06,
      28,
      1,
      false,
      -0.85,
      1.7,
    ),
    mats.iron,
  );
  cw.rotation.x = pi / 2;
  cw.position.set(0, 0, 0.02);
  cw.castShadow = true;
  g.add(cw);

  // Rim bolt ring hint
  const boltRing = new THREE.Mesh(
    new THREE.TorusGeometry(r * 0.9, 0.012, 6, 24),
    mats.steel,
  );
  boltRing.rotation.x = pi / 2;
  g.add(boltRing);

  return g;
}
