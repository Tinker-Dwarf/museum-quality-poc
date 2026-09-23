"""
Commodore Vanderbilt — J-1e #5344 Kantola 1934.
1 u = 1 ft. Face is a flat vertical prow (not a sphere).
Run:
  blender --background --python build_commodore.py -- --out commodore.glb
"""
import bpy
import math
import sys


def argv_out():
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1 :]
        if "--out" in args:
            return args[args.index("--out") + 1]
    return "commodore.glb"


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
        for block in list(coll):
            coll.remove(block)


def mat(name, color, metallic=0.28, roughness=0.36, emission=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission[0], 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission[1]
    return m


def apply_ob(ob):
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    ob.select_set(False)
    return ob


def cube(name, loc, size, material, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (size[0] / 2.0, size[1] / 2.0, size[2] / 2.0)
    apply_ob(ob)
    ob.data.materials.append(material)
    return ob


def cylinder(name, loc, r, depth, material, rot=(0, math.pi / 2, 0), verts=48):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=r, depth=depth, location=loc, rotation=rot, vertices=verts
    )
    ob = bpy.context.active_object
    ob.name = name
    apply_ob(ob)
    ob.data.materials.append(material)
    return ob


def sphere(name, loc, r, material, segs=40):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=segs, ring_count=max(16, segs // 2))
    ob = bpy.context.active_object
    ob.name = name
    apply_ob(ob)
    ob.data.materials.append(material)
    return ob


def bevel(ob, width=0.08, segs=3):
    m = ob.modifiers.new("Bevel", "BEVEL")
    m.width = width
    m.segments = segs
    m.limit_method = "ANGLE"
    m.angle_limit = math.radians(25)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=m.name)
    return ob


def parent(child, root):
    mw = child.matrix_world.copy()
    child.parent = root
    child.matrix_parent_inverse = root.matrix_world.inverted()
    child.matrix_world = mw


def build_wheel(tag, loc, r, width, iron, steel):
    x, y, z = loc
    tire = cylinder(f"{tag}_tire", (x, y, z), r, width, iron, rot=(math.pi / 2, 0, 0), verts=32)
    rim = cylinder(f"{tag}_rim", (x, y, z), r * 0.72, width * 0.45, steel, rot=(math.pi / 2, 0, 0), verts=24)
    hub = cylinder(f"{tag}_hub", (x, y, z), r * 0.22, width * 1.1, steel, rot=(math.pi / 2, 0, 0), verts=16)
    return [tire, rim, hub]


def build():
    clear_scene()
    shroud = mat("Shroud", (0.13, 0.155, 0.185), metallic=0.22, roughness=0.38)
    dark = mat("Dark", (0.05, 0.055, 0.06), metallic=0.4, roughness=0.42)
    iron = mat("Iron", (0.06, 0.06, 0.065), metallic=0.65, roughness=0.4)
    steel = mat("Steel", (0.55, 0.57, 0.60), metallic=0.88, roughness=0.22)
    glass = mat("Glass", (0.05, 0.08, 0.11), metallic=0.05, roughness=0.06)
    lamp = mat("Lamp", (0.95, 0.93, 0.8), metallic=0.05, roughness=0.1, emission=((1.0, 0.96, 0.75), 10.0))
    cream = mat("Herald", (0.82, 0.78, 0.68), metallic=0.15, roughness=0.4)

    root = bpy.data.objects.new("CommodoreVanderbilt", None)
    bpy.context.collection.objects.link(root)

    DRIVE_R = 79.0 / 24.0
    LEAD_R = 36.0 / 24.0
    TRAIL_F = 36.0 / 24.0
    TRAIL_R = 51.0 / 24.0
    TEN_R = 33.0 / 24.0
    BOIL_R = 91.5 / 24.0
    BOIL_Z = 9.15
    LEAD = (30.2, 24.8)
    DRIVE = (18.0, 11.0, 4.0)
    TRAIL = (-2.5, -8.3)
    TEN_FRONT = (-14.0, -18.4, -22.8)
    TEN_REAR = (-43.0, -47.4, -51.8)
    TEN_XS = TEN_FRONT + TEN_REAR

    barrel = cylinder("Barrel", (11.0, 0, BOIL_Z), BOIL_R, 28.0, shroud, verts=48)
    parent(barrel, root)
    bpy.ops.mesh.primitive_cone_add(
        radius1=BOIL_R, radius2=BOIL_R * 0.84, depth=10.0,
        location=(-8.0, 0, BOIL_Z), rotation=(0, math.pi / 2, 0), vertices=48,
    )
    tap = bpy.context.active_object
    tap.name = "BarrelTaper"
    apply_ob(tap)
    tap.data.materials.append(shroud)
    parent(tap, root)

    face = cube("Face", (31.55, 0, 7.35), (1.9, 7.5, 11.6), shroud)
    bevel(face, 0.72, 5)
    parent(face, root)
    crown = sphere("Crown", (31.45, 0, 12.55), 3.70, shroud, segs=40)
    crown.scale = (0.38, 1.01, 0.36)
    bpy.context.view_layer.objects.active = crown
    crown.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    crown.select_set(False)
    parent(crown, root)
    for s in (-1, 1):
        cheek = cube(f"Cheek_{s}", (28.4, s * 3.15, 8.4), (6.4, 1.5, 8.8), shroud)
        bevel(cheek, 0.35, 3)
        parent(cheek, root)
    bezel = cylinder("Bezel", (32.55, 0, 9.35), 0.95, 0.28, steel, verts=28)
    parent(bezel, root)
    lens = sphere("Lens", (32.72, 0, 9.35), 0.78, lamp, segs=24)
    parent(lens, root)
    herald = cylinder("Herald", (32.52, 0, 6.55), 1.15, 0.16, cream, verts=28)
    herald.scale = (1.0, 1.35, 0.72)
    bpy.context.view_layer.objects.active = herald
    herald.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    herald.select_set(False)
    parent(herald, root)
    hring = cylinder("HeraldRing", (32.58, 0, 6.55), 1.28, 0.08, dark, verts=28)
    hring.scale = (1.0, 1.35, 0.72)
    bpy.context.view_layer.objects.active = hring
    hring.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    hring.select_set(False)
    parent(hring, root)
    grill = cube("GrillPanel", (32.48, 0, 12.35), (0.22, 2.8, 1.35), dark)
    parent(grill, root)
    for i in range(5):
        sl = cube(f"GrillSlat_{i}", (32.58, -1.00 + i * 0.50, 12.35), (0.10, 0.14, 1.15), steel)
        parent(sl, root)
    stack = cylinder("StackWell", (20.5, 0, BOIL_Z + BOIL_R - 0.05), 0.55, 0.22, dark, rot=(0, 0, 0), verts=24)
    parent(stack, root)

    cab = cube("Cab", (-10.2, 0, 9.2), (8.4, 10.2, 10.4), shroud)
    bevel(cab, 0.35, 3)
    parent(cab, root)
    roof = cylinder("CabRoof", (-10.2, 0, 10.4), 5.05, 10.2, shroud, verts=28)
    parent(roof, root)
    overhang = cube("CabOverhang", (-15.4, 0, 14.55), (3.6, 9.6, 0.45), shroud)
    bevel(overhang, 0.12, 2)
    parent(overhang, root)
    for s in (-1, 1):
        frame = cube(f"WinFrame_{s}", (-11.6, s * 5.15, 11.6), (2.4, 0.16, 1.8), dark)
        pane = cube(f"Win_{s}", (-11.6, s * 5.22, 11.6), (2.05, 0.10, 1.45), glass)
        parent(frame, root)
        parent(pane, root)
        num = cube(f"NumBoard_{s}", (-8.6, s * 5.16, 8.4), (1.8, 0.10, 0.7), dark)
        parent(num, root)

    for s in (-1, 1):
        walk = cube(f"Walk_{s}", (8.0, s * 4.35, 8.55), (32.0, 0.85, 0.22), shroud)
        parent(walk, root)
        cover = cube(f"SideCover_{s}", (8.5, s * 4.28, 6.55), (30.0, 0.16, 2.4), shroud)
        parent(cover, root)
        rail = cube(f"WalkRail_{s}", (8.0, s * 4.70, 9.15), (31.0, 0.08, 0.08), steel)
        parent(rail, root)
        sw = cube(f"StairWell_{s}", (29.4, s * 3.72, 6.9), (3.2, 0.42, 5.2), dark)
        parent(sw, root)
        for i, z in enumerate((4.4, 5.5, 6.6, 7.7, 8.8)):
            st = cube(f"NoseStep_{s}_{i}", (28.6 + i * 0.28, s * 3.72, z), (0.95, 0.55, 0.12), shroud)
            parent(st, root)
        cabst = cube(f"CabStep_{s}", (-8.2, s * 4.35, 8.15), (1.3, 0.70, 0.18), shroud)
        parent(cabst, root)

    frame = cube("Frame", (8.0, 0, 3.4), (36.0, 2.2, 0.7), iron)
    parent(frame, root)
    shovel = cube("Shovel", (30.8, 0, 2.85), (5.4, 6.2, 3.6), shroud)
    bevel(shovel, 0.55, 4)
    parent(shovel, root)
    point = cube("ShovelPoint", (32.4, 0, 1.85), (2.2, 4.4, 1.7), shroud)
    bevel(point, 0.35, 3)
    parent(point, root)
    pilot = cube("PilotBeam", (33.4, 0, 1.35), (1.1, 6.4, 0.55), iron)
    parent(pilot, root)
    fcoup = cube("FrontCoupler", (34.1, 0, 1.25), (0.7, 0.35, 0.35), steel)
    parent(fcoup, root)

    axles = ([(x, LEAD_R) for x in LEAD] + [(x, DRIVE_R) for x in DRIVE] + [(TRAIL[0], TRAIL_F), (TRAIL[1], TRAIL_R)])
    for x, z in axles:
        axle = cylinder(f"Axle_{x}", (x, 0, z), 0.16, 9.2, steel, rot=(math.pi / 2, 0, 0), verts=12)
        parent(axle, root)
    for x in TEN_XS:
        axle = cylinder(f"TenAxle_{x}", (x, 0, TEN_R), 0.13, 8.6, steel, rot=(math.pi / 2, 0, 0), verts=12)
        parent(axle, root)

    curtain = cube("Vestibule", (-15.9, 0, 8.4), (0.55, 8.6, 8.6), dark)
    parent(curtain, root)
    tender = cube("Tender", (-34.0, 0, 7.6), (36.5, 10.3, 11.2), shroud)
    bevel(tender, 0.40, 4)
    parent(tender, root)
    for s in (-1, 1):
        shoulder = cylinder(f"TenShoulder_{s}", (-33.0, s * 3.6, 12.6), 1.05, 32.0, shroud, verts=16)
        parent(shoulder, root)
    deck = cube("TenderDeck", (-33.5, 0, 13.35), (34.0, 7.2, 0.45), shroud)
    parent(deck, root)
    for i, ox in enumerate((-22.0, -24.6, -27.2, -29.8)):
        panel = cube(f"CoalCover_{i}", (ox, 0, 13.7), (2.3, 5.6, 0.22), dark)
        parent(panel, root)
    coal = cube("Coal", (-25.8, 0, 13.15), (10.5, 5.0, 0.7), dark)
    bevel(coal, 0.18, 2)
    parent(coal, root)
    hatch = cube("WaterHatch", (-45.5, 0, 13.55), (3.4, 3.0, 0.28), dark)
    parent(hatch, root)
    hinge = cube("HatchHinge", (-44.0, 0, 13.72), (0.28, 3.0, 0.12), steel)
    parent(hinge, root)
    fill = cylinder("FillCap", (-46.2, 0, 13.85), 0.55, 0.22, steel, rot=(0, 0, 0), verts=16)
    parent(fill, root)
    rear_ch = cube("RearChamfer", (-51.8, 0, 12.6), (1.6, 7.4, 0.7), shroud)
    bevel(rear_ch, 0.35, 4)
    parent(rear_ch, root)
    backup = cube("BackupLight", (-52.4, 1.6, 11.2), (0.22, 0.55, 0.4), lamp)
    parent(backup, root)
    cap_st = cube("CapacityStencil", (-52.35, 0.4, 8.6), (0.10, 2.2, 0.8), dark)
    parent(cap_st, root)
    buffer = cube("BufferBeam", (-52.4, 0, 3.15), (0.7, 8.0, 1.15), iron)
    parent(buffer, root)
    for s in (-1, 1):
        step = cube(f"RearStep_{s}", (-52.6, s * 3.3, 2.15), (0.55, 0.85, 0.20), steel)
        parent(step, root)
        pocket = cube(f"Poling_{s}", (-52.35, s * 4.4, 5.4), (0.22, 0.45, 0.45), dark)
        parent(pocket, root)
    for z in (3.4, 5.2, 7.0, 8.8, 10.6):
        rung = cube(f"Ladder_{z}", (-52.55, -2.4, z), (0.12, 1.05, 0.10), steel)
        parent(rung, root)
    for yy in (-2.9, -1.9):
        rail = cube(f"LadderRail_{yy}", (-52.55, yy, 7.2), (0.10, 0.10, 8.0), steel)
        parent(rail, root)
    grab = cube("RoofGrab", (-51.6, -2.4, 13.0), (1.1, 1.05, 0.10), steel)
    parent(grab, root)
    for s in (-1, 1):
        letter = cube(f"TenderPanel_{s}", (-34.0, s * 5.18, 8.7), (14.0, 0.06, 0.7), cream)
        stripe = cube(f"TenStripe_{s}", (-34.0, s * 5.18, 7.6), (28.0, 0.05, 0.16), cream)
        parent(letter, root)
        parent(stripe, root)
        for zi, z in enumerate((3.2, 5.0, 12.2)):
            riv = cube(f"Rivet_{s}_{zi}", (-34.0, s * 5.18, z), (32.0, 0.05, 0.08), dark)
            parent(riv, root)
        for gx in (-20.0, -28.0, -36.0, -44.0):
            ir = cube(f"Grab_{s}_{gx}", (gx, s * 5.22, 10.6), (0.9, 0.10, 0.10), steel)
            parent(ir, root)
        srail = cube(f"SideRail_{s}", (-34.0, s * 5.28, 12.4), (30.0, 0.08, 0.08), steel)
        parent(srail, root)
        for cx, group in ((-18.4, TEN_FRONT), (-47.4, TEN_REAR)):
            sf = cube(f"TenFrame_{s}_{cx}", (cx, s * 4.4, 2.0), (10.0, 0.28, 0.8), iron)
            parent(sf, root)
            bar = cube(f"Equalizer_{s}_{cx}", (cx, s * 4.4, 2.7), (9.0, 0.14, 0.18), steel)
            parent(bar, root)
        fst = cube(f"FrontStep_{s}", (-16.0, s * 5.25, 2.4), (0.8, 0.7, 0.16), steel)
        parent(fst, root)
    wscoop = cube("WaterScoop", (-34.0, 0, 1.15), (8.0, 1.4, 0.35), iron)
    parent(wscoop, root)

    for x in LEAD:
        for s in (-1, 1):
            for p in build_wheel(f"Lead_{x}_{s}", (x, s * 4.1, LEAD_R), LEAD_R, 0.42, iron, steel):
                parent(p, root)
    for x in DRIVE:
        for s in (-1, 1):
            for p in build_wheel(f"Drive_{x}_{s}", (x, s * 4.55, DRIVE_R), DRIVE_R, 0.55, iron, steel):
                parent(p, root)
    for x, tr in ((TRAIL[0], TRAIL_F), (TRAIL[1], TRAIL_R)):
        for s in (-1, 1):
            for p in build_wheel(f"Trail_{x}_{s}", (x, s * 4.1, tr), tr, 0.42, iron, steel):
                parent(p, root)
    for x in TEN_XS:
        for s in (-1, 1):
            for p in build_wheel(f"Ten_{x}_{s}", (x, s * 4.1, TEN_R), TEN_R, 0.36, iron, steel):
                parent(p, root)
    for s in (-1, 1):
        rod = cube(f"Rod_{s}", (11.0, s * 4.85, 4.4), (14.2, 0.16, 0.22), steel)
        parent(rod, root)
        cylb = cube(f"Cyl_{s}", (22.5, s * 3.5, 5.6), (3.6, 1.35, 1.7), dark)
        bevel(cylb, 0.15, 2)
        parent(cylb, root)
        cl = sphere(f"ClassLamp_{s}", (32.2, s * 3.15, 11.4), 0.18, lamp, segs=12)
        parent(cl, root)
    coupler = cube("Coupler", (-53.1, 0, 3.0), (0.8, 0.5, 0.5), steel)
    parent(coupler, root)
    bpy.ops.object.camera_add(location=(55, -78, 32), rotation=(1.15, 0, 0.62))
    bpy.context.scene.camera = bpy.context.active_object
    bpy.ops.object.light_add(type="SUN", location=(30, -20, 50))
    bpy.context.active_object.data.energy = 4.5
    return root


def export_glb(path):
    bpy.ops.object.select_all(action="DESELECT")
    root = bpy.data.objects.get("CommodoreVanderbilt")
    if root:
        def sel(ob):
            ob.select_set(True)
            for ch in ob.children:
                sel(ch)
        sel(root)
        bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB", use_selection=True, export_apply=True,
        export_texcoords=True, export_normals=True, export_materials="EXPORT",
        export_cameras=False, export_lights=False, export_yup=True,
    )


if __name__ == "__main__":
    build()
    out = argv_out()
    export_glb(out)
    print("Exported", out)
