#!/usr/bin/env python3
"""FreeCAD: Ouray solids -> STEP + per-part STLs (mm internals)."""
import sys
import os

OUT = r"C:\Users\Valued Customer\AppData\Local\Temp\ouray-poc-v1"
CAD = os.path.join(OUT, "cad")
os.makedirs(CAD, exist_ok=True)

import FreeCAD as App
import Part
import Mesh
import MeshPart
import Import

doc = App.newDocument("OurayPOC")

# Dimensions in mm (from metres * 1000)
def cyl(r, h, place=(0,0,0), axis='Z'):
    c = Part.makeCylinder(r, h)
    if axis == 'Y':
        c.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
    elif axis == 'X':
        c.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
    c.translate(App.Vector(*place))
    return c

def box(sx, sy, sz, place=(0,0,0)):
    # box centered-ish: FreeCAD makeBox from corner; shift by -half
    b = Part.makeBox(sx, sy, sz)
    b.translate(App.Vector(place[0]-sx/2, place[1]-sy/2, place[2]-sz/2))
    return b

def add_feature(name, shape):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

# --- Chassis frame ---
chassis = box(7200, 1000, 180, (600, 0, 720))
add_feature("chassis", chassis)

# --- Boiler ---
boiler = cyl(550, 4200, (-2000, 0, 1550), axis='X')
# FreeCAD cylinder along X: after rotate, base at origin then translate
# Remake carefully: cylinder along X centered
boiler_s = Part.makeCylinder(550, 4200)
boiler_s.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
boiler_s.translate(App.Vector(-2000, 0, 1550))
add_feature("boiler", boiler_s)

# --- Cylinder (one representative) ---
cyl_s = Part.makeCylinder(280, 850)
cyl_s.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
cyl_s.translate(App.Vector(-1975, -850, 950))
add_feature("cylinder", cyl_s)

# --- Driver wheel (spoked-ish solid: tire + hub + spokes as fused) ---
def make_driver_wheel():
    R = 640
    W = 120
    # Tire ring: outer cylinder minus inner
    outer = Part.makeCylinder(R, W)
    inner = Part.makeCylinder(R * 0.82, W + 2)
    inner.translate(App.Vector(0, 0, -1))
    tire = outer.cut(inner)
    hub = Part.makeCylinder(R * 0.18, W + 10)
    hub.translate(App.Vector(0, 0, -5))
    parts = [tire, hub]
    # Spokes
    import math
    for i in range(14):
        ang = (2 * math.pi * i) / 14
        spoke = Part.makeCylinder(18, R * 0.75)
        spoke.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
        # position spoke from hub outward in XY of wheel (wheel in XY, axle Z)
        # Actually wheel cylinder is along Z; spokes in XY plane
        spoke = Part.makeBox(R * 0.75, 20, 25)
        spoke.translate(App.Vector(R * 0.12, -10, W/2 - 12))
        spoke.rotate(App.Vector(0,0,W/2), App.Vector(0,0,1), math.degrees(ang))
        parts.append(spoke)
    fused = parts[0]
    for p in parts[1:]:
        fused = fused.fuse(p)
    # Orient wheel: axle along Y for loco (rotate X 90)
    fused.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
    return fused

driver_wheel = make_driver_wheel()
add_feature("driver_wheel", driver_wheel)

# --- Pilot wheel ---
def make_pilot_wheel():
    R = 300
    W = 100
    outer = Part.makeCylinder(R, W)
    inner = Part.makeCylinder(R * 0.8, W + 2)
    inner.translate(App.Vector(0, 0, -1))
    tire = outer.cut(inner)
    hub = Part.makeCylinder(R * 0.2, W + 8)
    hub.translate(App.Vector(0, 0, -4))
    import math
    parts = [tire, hub]
    for i in range(8):
        ang = (2 * math.pi * i) / 8
        spoke = Part.makeBox(R * 0.7, 14, 18)
        spoke.translate(App.Vector(R * 0.12, -7, W/2 - 9))
        spoke.rotate(App.Vector(0,0,W/2), App.Vector(0,0,1), math.degrees(ang))
        parts.append(spoke)
    fused = parts[0]
    for p in parts[1:]:
        fused = fused.fuse(p)
    fused.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
    return fused

pilot_wheel = make_pilot_wheel()
add_feature("pilot_wheel", pilot_wheel)

# --- Tender ---
tender = box(3200, 1700, 1700, (5800, 0, 1150))
add_feature("tender", tender)

doc.recompute()

# Export combined STEP via Import.export (Part::Feature list — not bare Shape stub)
step_path = os.path.join(CAD, "ouray-poc-v1.step")
objs = [doc.getObject(n) for n in ("chassis", "boiler", "cylinder", "driver_wheel", "pilot_wheel", "tender")]
objs = [o for o in objs if o is not None]
Import.export(objs, step_path)
print("STEP_EXPORTED", step_path, "bytes_pending")

# Per-part STLs
def export_stl(obj, path):
    # Mesh from shape
    shape = obj.Shape
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.5, AngularDeflection=0.1, Relative=False)
    mesh.write(path)
    print("STL", path, os.path.getsize(path))

for name in ("chassis", "boiler", "cylinder", "driver_wheel", "pilot_wheel", "tender"):
    obj = doc.getObject(name)
    if obj:
        export_stl(obj, os.path.join(CAD, f"{name}.stl"))

step_size = os.path.getsize(step_path)
print(f"STEP_SIZE={step_size}")
if step_size < 10000:
    print("HARD_FAIL_STUB_STEP")
    sys.exit(2)

# Verify wheel STLs
for wn in ("driver_wheel.stl", "pilot_wheel.stl"):
    sz = os.path.getsize(os.path.join(CAD, wn))
    print(f"WHEEL_STL_{wn}={sz}")
    if sz < 1000:
        print("HARD_FAIL_WHEEL_STL")
        sys.exit(3)

doc.saveAs(os.path.join(CAD, "ouray-poc-v1.FCStd"))
print("FREECAD_OK")
sys.exit(0)
