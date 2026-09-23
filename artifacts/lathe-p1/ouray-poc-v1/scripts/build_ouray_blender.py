#!/usr/bin/env python3
"""Build Ouray 2-8-0 museum POC in Blender — look.png, blend, glb."""
import bpy
import bmesh
import math
import os
import sys
from mathutils import Vector, Matrix

OUT = r"C:\Users\Valued Customer\AppData\Local\Temp\ouray-poc-v1"
os.makedirs(os.path.join(OUT, "game"), exist_ok=True)
os.makedirs(os.path.join(OUT, "museum"), exist_ok=True)
os.makedirs(os.path.join(OUT, "cad"), exist_ok=True)

# --- reset ---
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

def coll(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        scene.collection.children.link(c)
    return c

def link(obj, cname):
    c = coll(cname)
    # unlink from scene root if present
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    c.objects.link(obj)
    return obj

def mat(name, color, metallic=0.7, roughness=0.35, emission=None):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission[:3], 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission[3] if len(emission) > 3 else 2.0
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m

MAT_BOILER = mat("BoilerShell", (0.62, 0.64, 0.66), 0.85, 0.28)
MAT_DARK = mat("DarkIron", (0.08, 0.085, 0.09), 0.6, 0.45)
MAT_BRASS = mat("BrassTrim", (0.72, 0.55, 0.22), 0.95, 0.25)
MAT_GLASS = mat("HeadlightGlass", (0.35, 0.55, 0.95), 0.1, 0.05, emission=(0.25, 0.45, 0.95, 3.0))
MAT_TIRE = mat("WheelTire", (0.05, 0.05, 0.05), 0.3, 0.55)
MAT_SPOKE = mat("WheelSpoke", (0.55, 0.57, 0.58), 0.8, 0.3)
MAT_ROD = mat("SideRod", (0.7, 0.72, 0.74), 0.9, 0.22)
MAT_WOOD = mat("Pedestal", (0.55, 0.48, 0.38), 0.05, 0.7)
MAT_RAIL = mat("Rail", (0.35, 0.36, 0.38), 0.7, 0.4)
MAT_LETTER = mat("LetterPaint", (0.95, 0.95, 0.92), 0.0, 0.55)

def assign(obj, m):
    if obj.data.materials:
        obj.data.materials[0] = m
    else:
        obj.data.materials.append(m)

def mesh_from_bm(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    return obj

def make_cylinder(name, radius, depth, loc, rot=(0,0,0), verts=48, cname="boiler"):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    link(obj, cname)
    return obj

def make_uvsphere(name, radius, loc, cname="stack_domes", segs=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=segs//2, radius=radius, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    link(obj, cname)
    return obj

def make_cube(name, scale, loc, cname="cab"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    link(obj, cname)
    return obj

def make_cone(name, r1, r2, depth, loc, rot=(0,0,0), cname="stack_domes", verts=32):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    link(obj, cname)
    return obj

# ============================================================
# DIMENSIONS (metres) — compact American 2-8-0 mountain loco
# Overall ~11.5 m loco+tender, driver dia ~1.3 m
# ============================================================
BOILER_R = 0.55
BOILER_LEN = 4.2
BOILER_Z = 1.55
BOILER_Y = 0.0

# Chassis / frame
FRAME_LEN = 7.2
FRAME_W = 1.0
FRAME_H = 0.18
FRAME_Z = 0.72

# Drivers: 4 axles, dia ~1.28 m
DRIVER_R = 0.64
DRIVER_W = 0.14   # half-width per side tire thickness visual
DRIVER_X = [-0.55, 0.75, 2.05, 3.35]  # along +X rear of cylinders
DRIVER_Z = DRIVER_R
DRIVER_Y = 0.72   # half track (outer face)

# Pilot truck: 2 small wheels
PILOT_R = 0.30
PILOT_X = -2.35
PILOT_Y = 0.55
PILOT_Z = PILOT_R

# ============================================================
# CHASSIS
# ============================================================
frame = make_cube("chassis_frame", (FRAME_LEN/2, FRAME_W/2, FRAME_H/2), (0.6, 0, FRAME_Z), "chassis")
assign(frame, MAT_DARK)

# side frames / running boards
for side in (-1, 1):
    rb = make_cube(f"running_board_{side}", (FRAME_LEN/2 * 0.95, 0.08, 0.03), (0.6, side * 0.62, FRAME_Z + 0.35), "chassis")
    assign(rb, MAT_DARK)

# ============================================================
# PILOT / COWCATCHER
# ============================================================
# triangular cowcatcher from bars
bm = bmesh.new()
# wedge solid
verts = [
    Vector((-3.55, 0, 0.15)),
    Vector((-2.55, -0.7, 0.15)),
    Vector((-2.55, 0.7, 0.15)),
    Vector((-3.55, 0, 0.85)),
    Vector((-2.55, -0.7, 0.85)),
    Vector((-2.55, 0.7, 0.85)),
]
# Build cowcatcher as extruded triangle fan of vertical bars
for i, t in enumerate([-0.65, -0.45, -0.25, -0.08, 0.08, 0.25, 0.45, 0.65]):
    tip = Vector((-3.55, 0, 0.2))
    base = Vector((-2.55, t, 0.2))
    tip2 = Vector((-3.55, 0, 0.85))
    base2 = Vector((-2.55, t, 0.85))
    # thin bar as cube approx via cylinder along tip-base
    mid = (tip + base) * 0.5
    mid.z = 0.52
    length = (base - tip).length
    bar = make_cube(f"cowcatcher_bar_{i}", (length/2, 0.025, 0.32), (mid.x, mid.y, mid.z), "pilot")
    # rotate toward tip
    angle = math.atan2(t, 1.0)
    bar.rotation_euler = (0, 0, angle)
    bpy.context.view_layer.objects.active = bar
    bpy.ops.object.transform_apply(rotation=True)
    assign(bar, MAT_BOILER)

# pilot beam
pb = make_cube("pilot_beam", (0.12, 0.75, 0.12), (-2.55, 0, 0.55), "pilot")
assign(pb, MAT_DARK)

# pilot truck frame
ptf = make_cube("pilot_truck_frame", (0.55, 0.08, 0.06), (PILOT_X, 0, PILOT_Z + 0.08), "pilot")
assign(ptf, MAT_DARK)

# ============================================================
# WHEELS — PILOT (2) + DRIVERS (4) with spokes
# ============================================================
def make_spoked_wheel(name, radius, width, loc, cname, n_spokes=12, hub_r=None):
    """Build a visible spoked wheel: tire + hub + spokes. Returns parent empty with children."""
    parent = bpy.data.objects.new(name, None)
    link(parent, cname)
    parent.location = loc

    # Tire (torus-like: cylinder ring)
    tire = make_cylinder(f"{name}_tire", radius, width, loc, rot=(math.pi/2, 0, 0), verts=64, cname=cname)
    # Hollow visually by adding inner rim disc? Keep solid thin cylinder for silhouette + spokes on face
    assign(tire, MAT_TIRE)
    tire.parent = parent
    tire.location = (0, 0, 0)

    # Inner rim (slightly smaller, metallic)
    rim = make_cylinder(f"{name}_rim", radius * 0.88, width * 0.7, loc, rot=(math.pi/2, 0, 0), verts=48, cname=cname)
    assign(rim, MAT_SPOKE)
    rim.parent = parent
    rim.location = (0, 0, 0)

    # Hub
    hr = hub_r or radius * 0.18
    hub = make_cylinder(f"{name}_hub", hr, width * 1.15, loc, rot=(math.pi/2, 0, 0), verts=24, cname=cname)
    assign(hub, MAT_BRASS)
    hub.parent = parent
    hub.location = (0, 0, 0)

    # Spokes — thin cylinders from hub to rim in wheel plane (Y is axle)
    spoke_len = radius * 0.75
    for i in range(n_spokes):
        ang = (2 * math.pi * i) / n_spokes
        # spoke along XZ plane, centered
        sx = math.cos(ang) * spoke_len * 0.5
        sz = math.sin(ang) * spoke_len * 0.5
        spoke = make_cylinder(f"{name}_spoke_{i}", 0.018 if radius > 0.4 else 0.012,
                              spoke_len, (loc[0]+sx, loc[1], loc[2]+sz),
                              rot=(0, math.pi/2 - ang, 0), verts=8, cname=cname)
        assign(spoke, MAT_SPOKE)
        spoke.parent = parent
        # re-express local
        spoke.location = (sx, 0, sz)
        spoke.rotation_euler = (0, math.pi/2 - ang, 0)

    # Counterweight blob on drivers
    if radius > 0.4:
        cw = make_cube(f"{name}_counterweight", (radius*0.22, width*0.35, radius*0.12),
                       (loc[0] + radius*0.45, loc[1], loc[2]), cname)
        assign(cw, MAT_SPOKE)
        cw.parent = parent
        cw.location = (radius*0.45, 0, 0)

    return parent

# Pilot wheels — left and right
for side, sy in (("L", -PILOT_Y), ("R", PILOT_Y)):
    make_spoked_wheel(f"pilot_wheel_{side}", PILOT_R, 0.10, (PILOT_X, sy, PILOT_Z), "wheels_pilot", n_spokes=8)

# Driver wheels — 4 axles × L/R
driver_objs = []
for i, dx in enumerate(DRIVER_X):
    for side, sy in (("L", -DRIVER_Y), ("R", DRIVER_Y)):
        w = make_spoked_wheel(f"driver_{i}_{side}", DRIVER_R, 0.12, (dx, sy, DRIVER_Z), "wheels_drivers", n_spokes=14)
        driver_objs.append(w)

# Axles
for i, dx in enumerate(DRIVER_X):
    ax = make_cylinder(f"driver_axle_{i}", 0.05, DRIVER_Y * 2 + 0.1, (dx, 0, DRIVER_Z), rot=(math.pi/2, 0, 0), verts=16, cname="drivers")
    assign(ax, MAT_DARK)

# Pilot axle
pax = make_cylinder("pilot_axle", 0.035, PILOT_Y * 2 + 0.08, (PILOT_X, 0, PILOT_Z), rot=(math.pi/2, 0, 0), verts=12, cname="pilot")
assign(pax, MAT_DARK)

# ============================================================
# SIDE / COUPLING RODS (visible connecting rods on drivers)
# ============================================================
# Main coupling rod linking all 4 drivers on each side
for side, sy in (("L", -DRIVER_Y - 0.08), ("R", DRIVER_Y + 0.08)):
    # coupling rod at pin height ~0.25 above axle centerline offset
    pin_z = DRIVER_Z + 0.22
    x0, x1 = DRIVER_X[0], DRIVER_X[-1]
    rod = make_cube(f"coupling_rod_{side}", ((x1 - x0) / 2 + 0.1, 0.025, 0.04),
                    ((x0 + x1) / 2, sy, pin_z), "drivers")
    assign(rod, MAT_ROD)
    # side rod (main rod) from cylinder to first driver
    srod = make_cube(f"side_rod_{side}", (0.9, 0.03, 0.045),
                     ((DRIVER_X[0] - 1.4), sy, pin_z - 0.05), "drivers")
    assign(srod, MAT_ROD)
    # crank pins
    for i, dx in enumerate(DRIVER_X):
        pin = make_cylinder(f"crank_pin_{side}_{i}", 0.03, 0.08, (dx, sy, pin_z), rot=(math.pi/2, 0, 0), verts=12, cname="drivers")
        assign(pin, MAT_BRASS)

# ============================================================
# CYLINDERS
# ============================================================
for side, sy in (("L", -0.85), ("R", 0.85)):
    cyl = make_cylinder(f"cylinder_{side}", 0.28, 0.85, (-1.55, sy, 0.95), rot=(0, math.pi/2, 0), verts=32, cname="cylinders")
    assign(cyl, MAT_BOILER)
    # valve chest
    vc = make_cube(f"valve_chest_{side}", (0.35, 0.18, 0.14), (-1.55, sy, 1.28), "cylinders")
    assign(vc, MAT_DARK)
    # piston rod guide
    pr = make_cylinder(f"piston_rod_{side}", 0.035, 0.6, (-1.0, sy, 0.95), rot=(0, math.pi/2, 0), verts=12, cname="cylinders")
    assign(pr, MAT_ROD)

# smokebox front
smokebox = make_cylinder("smokebox", BOILER_R + 0.02, 0.9, (-2.0, 0, BOILER_Z), rot=(0, math.pi/2, 0), verts=48, cname="boiler")
assign(smokebox, MAT_DARK)

# front number plate / door
door = make_cylinder("smokebox_door", BOILER_R * 0.85, 0.06, (-2.48, 0, BOILER_Z), rot=(0, math.pi/2, 0), verts=32, cname="boiler")
assign(door, MAT_DARK)

# ============================================================
# BOILER
# ============================================================
boiler = make_cylinder("boiler", BOILER_R, BOILER_LEN, (0.1, 0, BOILER_Z), rot=(0, math.pi/2, 0), verts=64, cname="boiler")
assign(boiler, MAT_BOILER)

# boiler bands
for i, bx in enumerate([-1.2, -0.3, 0.6, 1.5]):
    band = make_cylinder(f"boiler_band_{i}", BOILER_R + 0.015, 0.06, (bx, 0, BOILER_Z), rot=(0, math.pi/2, 0), verts=48, cname="boiler")
    assign(band, MAT_DARK)

# firebox
fb = make_cube("firebox", (0.7, 0.65, 0.7), (2.5, 0, BOILER_Z - 0.15), "boiler")
assign(fb, MAT_DARK)

# ============================================================
# STACK + DOMES + BELL + HEADLIGHT
# ============================================================
# Diamond stack (cone flare)
stack_base = make_cylinder("stack_base", 0.16, 0.35, (-1.85, 0, BOILER_Z + BOILER_R + 0.15), verts=24, cname="stack_domes")
assign(stack_base, MAT_DARK)
stack_diamond = make_cone("stack_diamond", 0.38, 0.14, 0.55, (-1.85, 0, BOILER_Z + BOILER_R + 0.55), verts=24, cname="stack_domes")
assign(stack_diamond, MAT_DARK)
stack_cap = make_cylinder("stack_cap", 0.40, 0.06, (-1.85, 0, BOILER_Z + BOILER_R + 0.85), verts=24, cname="stack_domes")
assign(stack_cap, MAT_DARK)

# Sand dome (front)
dome1 = make_uvsphere("sand_dome", 0.28, (-0.4, 0, BOILER_Z + BOILER_R + 0.05), "stack_domes")
dome1.scale = (1, 1, 0.75)
bpy.ops.object.transform_apply(scale=True)
assign(dome1, MAT_BOILER)

# Steam dome (rear)
dome2 = make_uvsphere("steam_dome", 0.32, (0.9, 0, BOILER_Z + BOILER_R + 0.08), "stack_domes")
dome2.scale = (1, 1, 0.8)
bpy.ops.object.transform_apply(scale=True)
assign(dome2, MAT_BOILER)

# Bell between domes
bell = make_uvsphere("bell", 0.12, (0.25, 0, BOILER_Z + BOILER_R + 0.22), "stack_domes", segs=16)
assign(bell, MAT_BRASS)
bell_yoke = make_cube("bell_yoke", (0.08, 0.04, 0.12), (0.25, 0, BOILER_Z + BOILER_R + 0.38), "stack_domes")
assign(bell_yoke, MAT_BRASS)

# Headlight — square housing + blue lens
hl_box = make_cube("headlight_housing", (0.14, 0.18, 0.18), (-2.55, 0, BOILER_Z + 0.55), "stack_domes")
assign(hl_box, MAT_DARK)
hl_lens = make_cylinder("headlight_lens", 0.12, 0.04, (-2.70, 0, BOILER_Z + 0.55), rot=(0, math.pi/2, 0), verts=24, cname="stack_domes")
assign(hl_lens, MAT_GLASS)

# ============================================================
# CAB
# ============================================================
cab = make_cube("cab_body", (1.1, 0.85, 0.95), (3.5, 0, BOILER_Z + 0.35), "cab")
assign(cab, MAT_DARK)
cab_roof = make_cube("cab_roof", (1.2, 0.95, 0.08), (3.5, 0, BOILER_Z + 1.25), "cab")
assign(cab_roof, MAT_DARK)
# windows (slightly inset lighter panels — glass-ish)
for side, sy in (("L", -0.86), ("R", 0.86)):
    win = make_cube(f"cab_window_{side}", (0.35, 0.02, 0.35), (3.35, sy, BOILER_Z + 0.55), "cab")
    assign(win, MAT_GLASS)

# ============================================================
# TENDER
# ============================================================
tender = make_cube("tender_body", (1.6, 0.85, 0.85), (5.8, 0, 1.15), "tender")
assign(tender, MAT_DARK)
tender_top = make_cube("tender_coal", (1.4, 0.7, 0.25), (5.8, 0, 2.05), "tender")
assign(tender_top, MAT_TIRE)  # dark coal
# tender trucks (simple wheel pairs)
for tx in (5.1, 6.5):
    for side, sy in (("L", -0.55), ("R", 0.55)):
        tw = make_spoked_wheel(f"tender_wheel_{tx}_{side}", 0.28, 0.09, (tx, sy, 0.28), "tender", n_spokes=8, hub_r=0.06)
# lettering board (flat white panel — SILVERTON R.R. 100 stand-in)
letter = make_cube("tender_letter_board", (1.2, 0.01, 0.25), (5.8, -0.86, 1.35), "tender")
assign(letter, MAT_LETTER)

# drawbar
db = make_cube("drawbar", (0.5, 0.08, 0.08), (4.7, 0, 0.75), "tender")
assign(db, MAT_DARK)

# ============================================================
# MUSEUM PEDESTAL + TRACK
# ============================================================
ped = make_cube("pedestal", (7.5, 2.2, 0.08), (1.5, 0, -0.08), "chassis")
assign(ped, MAT_WOOD)

for side, sy in (("L", -0.72), ("R", 0.72)):
    rail = make_cube(f"rail_{side}", (7.0, 0.04, 0.05), (1.2, sy, 0.02), "chassis")
    assign(rail, MAT_RAIL)
# ties
for i in range(14):
    tie = make_cube(f"tie_{i}", (0.08, 0.95, 0.04), (-2.5 + i * 0.7, 0, -0.01), "chassis")
    assign(tie, MAT_WOOD)

# ============================================================
# WORLD / LIGHTING / CAMERA
# ============================================================
# World — warm cream museum void
world = bpy.data.worlds.new("MuseumWorld")
scene.world = world
world.use_nodes = True
wn = world.node_tree
for n in list(wn.nodes):
    wn.nodes.remove(n)
wout = wn.nodes.new("ShaderNodeOutputWorld")
bg = wn.nodes.new("ShaderNodeBackground")
# ~0.82 cream/off-white
bg.inputs["Color"].default_value = (0.82, 0.80, 0.76, 1.0)
bg.inputs["Strength"].default_value = 0.95
wn.links.new(bg.outputs["Background"], wout.inputs["Surface"])

# Lights
def area_light(name, loc, energy, size, color=(1.0, 0.97, 0.92)):
    light_data = bpy.data.lights.new(name=name, type='AREA')
    light_data.energy = energy
    light_data.size = size
    light_data.color = color
    light_obj = bpy.data.objects.new(name, light_data)
    scene.collection.objects.link(light_obj)
    light_obj.location = loc
    # point toward loco center
    direction = Vector((1.2, 0, 1.2)) - Vector(loc)
    light_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return light_obj

area_light("KeyLight", (4.5, -5.5, 5.5), 450, 4.0)
area_light("FillLight", (-3.0, 5.0, 4.0), 220, 5.0, (0.95, 0.96, 1.0))
area_light("RimLight", (6.0, 3.0, 3.5), 180, 3.0, (1.0, 0.95, 0.9))

# Camera 3/4 view — wheels readable
cam_data = bpy.data.cameras.new("OurayCam")
cam = bpy.data.objects.new("OurayCam", cam_data)
scene.collection.objects.link(cam)
cam.location = (6.2, -7.8, 3.4)
# look at roughly mid-loco near drivers
target = Vector((1.5, 0, 1.2))
direction = target - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam_data.lens = 50
scene.camera = cam

# ============================================================
# RENDER SETTINGS — Cycles HIP, not black
# ============================================================
scene.render.engine = 'CYCLES'
scene.cycles.samples = 96
scene.cycles.use_denoising = True
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.render.filepath = os.path.join(OUT, "look.png")
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'None'

# Prefer HIP GPU
prefs = bpy.context.preferences.addons.get('cycles')
if prefs:
    cprefs = prefs.preferences
    try:
        cprefs.compute_device_type = 'HIP'
        for dev in cprefs.devices:
            dev.use = True
        scene.cycles.device = 'GPU'
        print("Cycles device: GPU HIP")
    except Exception as e:
        print("HIP unavailable, using CPU:", e)
        scene.cycles.device = 'CPU'
else:
    scene.cycles.device = 'CPU'

# ============================================================
# SAVE + EXPORT + RENDER
# ============================================================
blend_path = os.path.join(OUT, "museum", "ouray-poc-v1.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print("Saved blend:", blend_path)

# GLB export — all mesh objects
glb_path = os.path.join(OUT, "game", "ouray-poc-v1.glb")
bpy.ops.export_scene.gltf(filepath=glb_path, export_format='GLB', use_selection=False,
                          export_apply=True)
print("Exported GLB:", glb_path)

# Render
bpy.ops.render.render(write_still=True)
print("Rendered look.png")

# Verify luminance
import struct
import zlib

def png_mean_luma(path):
    """Rough mean luma from PNG via bpy image load."""
    img = bpy.data.images.load(path)
    px = list(img.pixels)  # RGBA float 0-1
    n = img.size[0] * img.size[1]
    # sample every 16th pixel for speed
    acc = 0.0
    count = 0
    step = 16
    for i in range(0, n, step):
        r = px[i*4]
        g = px[i*4+1]
        b = px[i*4+2]
        acc += 0.2126*r + 0.7152*g + 0.0722*b
        count += 1
    mean = acc / max(count, 1)
    bpy.data.images.remove(img)
    return mean * 255.0

luma = png_mean_luma(os.path.join(OUT, "look.png"))
print(f"LOOK_MEAN_LUMA={luma:.2f}")
if luma < 40.0:
    print("FAIL: look.png mean luma < 40 — black/unusable")
    # bump world + re-render once
    bg.inputs["Strength"].default_value = 1.4
    for L in bpy.data.lights:
        L.energy *= 1.8
    bpy.ops.render.render(write_still=True)
    luma = png_mean_luma(os.path.join(OUT, "look.png"))
    print(f"LOOK_MEAN_LUMA_RETRY={luma:.2f}")
    if luma < 40.0:
        print("HARD_FAIL_BLACK_LOOK")
        sys.exit(2)

# Count wheel objects
wheel_names = [o.name for o in bpy.data.objects if 'wheel' in o.name.lower() or 'driver_' in o.name.lower() or 'spoke' in o.name.lower()]
print(f"WHEEL_RELATED_OBJECTS={len(wheel_names)}")
print("WHEEL_NAMES_SAMPLE=", wheel_names[:40])

print("BLENDER_OK")
sys.exit(0)
