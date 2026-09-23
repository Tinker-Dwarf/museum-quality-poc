import * as THREE from "three";
import { Part } from "../../geometry/Part";
import { palette } from "../../geometry/materials";
import { pi } from "../../geometry/parameters";
import type { LocoBuilt, WheelNode } from "../ouray";

/** Driver radius — big Hudson drivers, sized to sit within the streamlined casing. */
export const VANDY_DRIVER_R = 1.2;

/**
 * Commodore Vanderbilt — streamlined NYC Hudson 4-6-4, modeled to the real
 * NYC #5344 references: smooth bathtub casing, curved skirt sweeping up over
 * three exposed spoked drivers, side/main rods, round NYC nose herald.
 */
export function buildVanderbilt(): LocoBuilt {
  const mats = palette();
  const root = new THREE.Group();
  root.name = "vanderbilt";
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

  // —— Chassis / frame under shroud ——
  const chassis = new Part("vandy/chassis", mats);
  chassis.box(14.5, 0.18, 1.1, "iron", [0, 0.55, 0]);
  chassis.finish(root);

  // —— Nose (smooth rounded prow — elongated dome blending into the barrel) ——
  const nose = new Part("vandy/nose", mats);
  const noseBody = new THREE.Mesh(
    new THREE.SphereGeometry(1.15, 44, 28),
    mats.shroudBlue,
  );
  noseBody.scale.set(1.75, 1.0, 1.0); // stretch along X into a rounded prow
  noseBody.position.set(-4.55, 1.55, 0);
  noseBody.castShadow = true;
  noseBody.receiveShadow = true;
  nose.group.add(noseBody);
  // Round NYC herald on the front
  const herRing = nose.cylinder(0.34, 0.34, 0.06, "trim", [-6.62, 1.5, 0], 28);
  herRing.rotation.z = pi / 2;
  const herField = nose.cylinder(0.28, 0.28, 0.06, "dark", [-6.63, 1.5, 0], 28);
  herField.rotation.z = pi / 2;
  const herText = nose.text("NEW YORK\nCENTRAL", {
    width: 0.5,
    height: 0.34,
    at: [-6.67, 1.5, 0],
    color: "#e8e2d6",
    font: "700 30px 'IBM Plex Sans', sans-serif",
  });
  herText.rotation.y = -pi / 2;
  // Headlight lens high on the face
  const headlight = nose.cylinder(0.13, 0.13, 0.1, "trim", [-6.4, 2.05, 0], 20);
  headlight.rotation.z = pi / 2;
  // Vertical louver vents on the lower-front sides
  for (const s of [-1, 1] as const) {
    for (let i = 0; i < 4; i++) {
      nose.box(0.035, 0.42, 0.05, "dark", [-5.5 + i * 0.16, 1.0, s * 0.86]);
    }
  }
  register("nose", nose.group, [-2.4, 0.3, 0]);

  // —— Boiler shell / cowl ——
  const boilerShell = new Part("vandy/boiler_shell", mats);
  // Main shroud barrel
  boilerShell.cylinder(1.15, 1.15, 6.5, "shroudBlue", [-1.5, 1.55, 0], 36);
  const barrel = boilerShell.group.children[0];
  barrel.rotation.z = pi / 2;

  // —— Streamlined side skirt with the signature curved lower edge ——
  // Flat side valance whose bottom sweeps up over the exposed drivers.
  const yBelt = 2.04;
  // Deep scalloped cutouts over the three drivers (raise bay edge so wheels pop like the still)
  const yBay = 1.85;
  const skirtShape = new THREE.Shape();
  skirtShape.moveTo(-6.3, yBelt);
  skirtShape.lineTo(2.4, yBelt);
  skirtShape.lineTo(2.4, 0.88);
  skirtShape.splineThru([
    new THREE.Vector2(2.05, 1.15),
    new THREE.Vector2(1.4, yBay),   // rear driver bay
    new THREE.Vector2(0.4, yBay + 0.06),
    new THREE.Vector2(-0.6, yBay + 0.08), // middle driver bay
    new THREE.Vector2(-1.6, yBay + 0.06),
    new THREE.Vector2(-2.6, yBay),  // lead driver bay
    new THREE.Vector2(-3.5, 1.2),
    new THREE.Vector2(-4.5, 0.62),
    new THREE.Vector2(-5.7, 0.4),
    new THREE.Vector2(-6.3, 0.62),
  ]);
  skirtShape.lineTo(-6.3, yBelt);
  const skirtGeo = new THREE.ExtrudeGeometry(skirtShape, {
    depth: 0.045,
    bevelEnabled: false,
  });
  for (const zc of [1.12, -1.165]) {
    const panel = new THREE.Mesh(skirtGeo, mats.shroudBlue);
    panel.position.z = zc;
    panel.castShadow = true;
    panel.receiveShadow = true;
    boilerShell.group.add(panel);
  }
  // Motion/frame mass behind driver cutouts — kept lighter + shorter so wheels read
  boilerShell.box(7.6, 0.55, 0.55, "iron", [-0.6, 0.72, 0]);
  // Beltline crease highlight where the round top meets the flat side
  for (const s of [-1, 1] as const) {
    boilerShell.box(8.7, 0.03, 0.03, "dark", [-1.4, yBelt, s * 1.17]);
  }

  // Primary name on loco side — centered on mid-barrel so full COMMODORE reads
  boilerShell.text("COMMODORE VANDERBILT", {
    width: 3.8,
    height: 0.26,
    at: [0.15, 1.72, 1.18],
    color: "#f2eee6",
    font: "700 34px 'IBM Plex Sans', sans-serif",
  });
  // Mirror lettering on −Z side
  const nameL = boilerShell.group.children[boilerShell.group.children.length - 1];
  boilerShell.text("COMMODORE VANDERBILT", {
    width: 3.8,
    height: 0.26,
    at: [0.15, 1.72, -1.18],
    color: "#f2eee6",
    font: "700 34px 'IBM Plex Sans', sans-serif",
  });
  const nameR = boilerShell.group.children[boilerShell.group.children.length - 1];
  nameR.rotation.y = pi;

  // Hidden boiler core volume (for explode read)
  boilerShell.cylinder(0.85, 0.85, 5.5, "iron", [-1.5, 1.55, 0], 20);
  const core = boilerShell.group.children[boilerShell.group.children.length - 1];
  core.rotation.z = pi / 2;
  core.visible = false;
  core.userData.core = true;
  register("boiler_shell", boilerShell.group, [0, 1.4, 0]);
  void nameL;

  // —— Cab fairing (roof continuous with the boiler casing height) ——
  const cabFairing = new Part("vandy/cab_fairing", mats);
  cabFairing.box(2.5, 2.3, 2.22, "shroudBlue", [3.1, 1.55, 0]);
  // Rounded roof matching the barrel top (~2.7)
  const roof = cabFairing.cylinder(1.1, 1.1, 2.22, "shroudBlue", [3.1, 1.6, 0], 28);
  roof.rotation.z = pi / 2;
  // Single rectangular side window with a slim frame
  for (const s of [-1, 1] as const) {
    cabFairing.box(0.66, 0.5, 0.05, "dark", [2.55, 2.02, s * 1.12]);
    cabFairing.box(0.56, 0.4, 0.06, "glass", [2.55, 2.02, s * 1.13]);
  }
  register("cab_fairing", cabFairing.group, [0.8, 1.3, 0]);

  // —— Chassis drivers (4-6-4): leading truck, 3 drivers, trailing truck ——
  const chassisDrivers = new THREE.Group();
  chassisDrivers.name = "chassis_drivers";

  // Leading truck — 2 axles (pilot wheels), both sides
  const leadR = 0.42;
  for (const x of [-5.4, -4.5]) {
    for (const s of [-1, 1] as const) {
      const truck = buildSolidDisc(leadR, mats, false);
      truck.position.set(x, leadR, s * 0.75);
      chassisDrivers.add(truck);
      wheels.push({ group: truck, radius: leadR });
    }
  }

  // 3 driver axles — open-spoke discs both sides, sitting in skirt cutouts
  const driverXs = [-2.6, -0.6, 1.4];
  const driverZ = 0.98; // flush to skirt cutouts so faces read at default camera
  for (const x of driverXs) {
    for (const s of [-1, 1] as const) {
      const d = buildSolidDisc(VANDY_DRIVER_R, mats, true);
      d.position.set(x, VANDY_DRIVER_R, s * driverZ);
      chassisDrivers.add(d);
      wheels.push({ group: d, radius: VANDY_DRIVER_R });
    }
  }

  // Trailing truck — 2 axles, both sides
  const trailR = 0.48;
  for (const x of [3.6, 4.5]) {
    for (const s of [-1, 1] as const) {
      const truck = buildSolidDisc(trailR, mats, false);
      truck.position.set(x, trailR, s * 0.75);
      chassisDrivers.add(truck);
      wheels.push({ group: truck, radius: trailR });
    }
  }

  // Running gear — cylinders, main + coupling rods, crankpins (both sides)
  const gear = new Part("vandy/gear", mats);
  const pinY = 1.05;
  for (const s of [-1, 1] as const) {
    const zc = s * 0.95;
    // coupling rod spanning the three drivers
    gear.box(4.3, 0.16, 0.05, "steel", [-0.6, pinY, zc]);
    // main rod slanting from crosshead to the lead driver pin
    const fx = -3.95;
    const fy = 1.16;
    const tx = -2.6;
    const ty = pinY;
    const len = Math.hypot(tx - fx, ty - fy);
    const mr = gear.box(len, 0.1, 0.05, "steel", [(fx + tx) / 2, (fy + ty) / 2, zc]);
    mr.rotation.z = Math.atan2(ty - fy, tx - fx);
    // crankpins on each driver
    for (const dx of driverXs) {
      const cp = gear.cylinder(0.07, 0.07, 0.12, "iron", [dx, pinY, zc]);
      cp.rotation.x = pi / 2;
    }
    // cylinder / steam-chest block ahead of the drivers
    gear.box(0.8, 0.52, 0.34, "dark", [-4.05, 1.15, s * 0.58]);
  }
  chassisDrivers.add(gear.group);

  register("chassis_drivers", chassisDrivers, [0, -1.2, 0]);

  // —— Tender shell (slab-sided, softly rounded top like the loco casing) ——
  const tenderShell = new Part("vandy/tender_shell", mats);
  tenderShell.box(5.4, 2.4, 2.16, "shroudBlue", [7.3, 1.5, 0]);
  // Rounded top shoulders + deck
  for (const s of [-1, 1] as const) {
    const fillet = tenderShell.cylinder(0.28, 0.28, 5.4, "shroudBlue", [7.3, 2.62, s * 0.8], 16);
    fillet.rotation.z = pi / 2;
  }
  tenderShell.box(5.4, 0.28, 1.64, "shroudBlue", [7.3, 2.72, 0]);
  // Rounded top rear corner
  const rearCap = tenderShell.cylinder(0.28, 0.28, 2.16, "shroudBlue", [9.98, 2.62, 0], 16);
  rearCap.rotation.x = pi / 2;
  // Lower valance with truck cutouts
  const tSkirt = new THREE.Shape();
  tSkirt.moveTo(4.6, 1.1);
  tSkirt.lineTo(10.0, 1.1);
  tSkirt.lineTo(10.0, 0.72);
  tSkirt.splineThru([
    new THREE.Vector2(8.9, 0.5),
    new THREE.Vector2(8.2, 0.72),
    new THREE.Vector2(7.2, 0.72),
    new THREE.Vector2(6.2, 0.5),
    new THREE.Vector2(5.4, 0.72),
    new THREE.Vector2(4.6, 0.72),
  ]);
  tSkirt.lineTo(4.6, 1.1);
  const tSkirtGeo = new THREE.ExtrudeGeometry(tSkirt, { depth: 0.05, bevelEnabled: false });
  for (const zc of [1.06, -1.11]) {
    const panel = new THREE.Mesh(tSkirtGeo, mats.shroudBlue);
    panel.position.z = zc;
    panel.castShadow = true;
    panel.receiveShadow = true;
    tenderShell.group.add(panel);
  }

  // Tender trucks
  for (const x of [5.6, 6.6, 7.9, 8.9]) {
    for (const s of [-1, 1] as const) {
      tenderShell.cylinder(0.35, 0.35, 0.14, "dark", [x, 0.35, s * 0.7]);
      const w = tenderShell.group.children[tenderShell.group.children.length - 1];
      w.rotation.x = pi / 2;
    }
  }

  // Tender lettering
  tenderShell.text("NEW YORK CENTRAL", {
    width: 3.8,
    height: 0.28,
    at: [7.3, 1.65, 1.1],
    color: "#e8e2d6",
    font: "600 42px 'IBM Plex Sans', sans-serif",
  });

  register("tender_shell", tenderShell.group, [2.0, 0.5, 0]);

  function setExplode(t: number) {
    const k = Math.min(1, Math.max(0, t));
    const names = [...explodeGroups.keys()];
    names.forEach((name, i) => {
      const obj = explodeGroups.get(name)!;
      const base = rest.get(name)!;
      const exp = obj.userData.explode as THREE.Vector3;
      const delay = i * 0.09;
      const local = Math.min(1, Math.max(0, (k - delay) / Math.max(0.01, 1 - delay * 0.4)));
      const e = local * local * (3 - 2 * local);
      obj.position.set(
        base.x + exp.x * e,
        base.y + exp.y * e,
        base.z + exp.z * e,
      );
      // Reveal boiler core when exploding
      if (name === "boiler_shell") {
        obj.traverse((o) => {
          if ((o as THREE.Mesh).isMesh && o.userData.core) {
            o.visible = k > 0.15;
          }
        });
      }
    });
  }

  return {
    root,
    explodeGroups,
    wheels,
    driverRadius: VANDY_DRIVER_R,
    setExplode,
    label: "Commodore Vanderbilt",
    id: "vanderbilt",
  };
}

function buildSolidDisc(
  r: number,
  mats: ReturnType<typeof palette>,
  withCounterweight: boolean,
): THREE.Group {
  const g = new THREE.Group();
  // Tire / rim (lathe)
  const disc = new THREE.Mesh(
    new THREE.LatheGeometry(
      [
        new THREE.Vector2(r * 0.62, -0.07),
        new THREE.Vector2(r * 0.9, -0.08),
        new THREE.Vector2(r, -0.06),
        new THREE.Vector2(r, 0.06),
        new THREE.Vector2(r * 0.9, 0.08),
        new THREE.Vector2(r * 0.62, 0.06),
      ],
      32,
    ),
    mats.iron,
  );
  disc.rotation.x = pi / 2;
  disc.castShadow = true;
  g.add(disc);

  // Open spokes
  const spokeN = 14;
  for (let i = 0; i < spokeN; i++) {
    const a = (i / spokeN) * pi * 2;
    const spoke = new THREE.Mesh(
      new THREE.BoxGeometry(r * 0.82, 0.07, 0.08),
      mats.steel,
    );
    spoke.position.set(Math.cos(a) * r * 0.44, Math.sin(a) * r * 0.44, 0);
    spoke.rotation.z = a;
    spoke.castShadow = true;
    g.add(spoke);
  }

  // Hub
  const hub = new THREE.Mesh(
    new THREE.CylinderGeometry(r * 0.2, r * 0.2, 0.18, 16),
    mats.steel,
  );
  hub.rotation.x = pi / 2;
  hub.castShadow = true;
  g.add(hub);

  if (withCounterweight) {
    // Smaller counterweight — leave open spoke bays readable in skirt cutouts
    const cw = new THREE.Mesh(
      new THREE.CylinderGeometry(r * 0.75, r * 0.75, 0.06, 24, 1, false, -0.55, 1.1),
      mats.iron,
    );
    cw.rotation.x = pi / 2;
    cw.position.set(0, 0, 0.02);
    cw.castShadow = true;
    g.add(cw);
  }

  return g;
}
