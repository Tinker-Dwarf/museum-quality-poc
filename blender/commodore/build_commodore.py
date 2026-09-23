"""
Commodore Vanderbilt — patent silhouette pass (US 2,108,203).
Kantola tender: covered coal, gangway curtain, car-style rear.
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


def build_wheel(tag, loc, r, width, iron, steel, spokes=12, counter=False):
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

    R = 1.15
    YB = 1.55

    barrel = cylinder("Barrel", (0.55, 0, YB), R, 6.4, shroud, verts=48)
    parent(barrel, root)
    bpy.ops.mesh.primitive_cone_add(
        radius1=R, radius2=R * 0.86, depth=2.4, location=(-3.15, 0, YB),
        rotation=(0, math.pi / 2, 0), vertices=48
    )
    tap = bpy.context.active_object
    tap.name = "BarrelTaper"
    apply_ob(tap)
    tap.data.materials.append(shroud)
    parent(tap, root)

    prow = sphere("Prow", (4.15, 0, YB), R, shroud, segs=64)
    prow.scale = (1.85, 1.0, 1.02)
    bpy.context.view_layer.objects.active = prow
    prow.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    prow.select_set(False)
    parent(prow, root)

    for z, rr in ((1.95, 0.16), (1.42, 0.18)):
        bezel = cylinder("Bezel", (5.95, 0, z), rr + 0.04, 0.07, steel, verts=24)
        parent(bezel, root)
        lens = sphere("Lens", (6.00, 0, z), rr, lamp, segs=20)
        parent(lens, root)
    herald = cylinder("Herald", (5.55, 0, 2.28), 0.22, 0.05, cream, verts=24)
    parent(herald, root)

    cab = cube("Cab", (-3.55, 0, 1.58), (2.35, 2.22, 2.35), shroud)
    bevel(cab, 0.10, 3)
    parent(cab, root)
    roof = cylinder("CabRoof", (-3.55, 0, 1.72), 1.10, 2.22, shroud, verts=28)
    parent(roof, root)
    overhang = cube("CabOverhang", (-4.95, 0, 2.62), (1.15, 2.10, 0.16), shroud)
    bevel(overhang, 0.04, 2)
    parent(overhang, root)
    for s in (-1, 1):
        frame = cube(f"WinFrame_{s}", (-3.95, s * 1.12, 2.05), (0.66, 0.05, 0.50), dark)
        pane = cube(f"Win_{s}", (-3.95, s * 1.14, 2.05), (0.56, 0.04, 0.40), glass)
        parent(frame, root)
        parent(pane, root)

    well = cylinder("StackWell", (2.15, 0, YB + R - 0.02), 0.20, 0.10, dark, rot=(0, 0, 0), verts=20)
    parent(well, root)

    driver_xs = (1.55, 0.15, -1.25)
    for s in (-1, 1):
        walk = cube(f"Walk_{s}", (0.15, s * 1.22, 1.58), (7.6, 0.32, 0.07), shroud)
        parent(walk, root)
        cover = cube(f"SideCover_{s}", (0.35, s * 1.20, 1.28), (7.2, 0.045, 0.42), shroud)
        parent(cover, root)
        for i, z in enumerate((1.42, 1.12, 0.82, 0.55)):
            st = cube(f"NoseStep_{s}_{i}", (3.85 + i * 0.07, s * 1.22, z), (0.32, 0.24, 0.05), shroud)
            parent(st, root)
        cabst = cube(f"CabStep_{s}", (-3.15, s * 1.22, 1.48), (0.35, 0.24, 0.06), shroud)
        parent(cabst, root)

    frame = cube("Frame", (0.0, 0, 0.58), (8.0, 0.55, 0.22), iron)
    parent(frame, root)

    for x, z in ((3.55, 0.38), (2.75, 0.38), (1.55, 0.78), (0.15, 0.78), (-1.25, 0.78), (-2.55, 0.42), (-3.25, 0.42)):
        axle = cylinder(f"Axle_{x}", (x, 0, z), 0.045, 1.85, steel, rot=(math.pi / 2, 0, 0), verts=12)
        parent(axle, root)
    ten_xs = (-5.85, -6.40, -6.95, -8.70, -9.25, -9.80)
    for x in ten_xs:
        axle = cylinder(f"TenAxle_{x}", (x, 0, 0.26), 0.035, 1.70, steel, rot=(math.pi / 2, 0, 0), verts=12)
        parent(axle, root)

    curtain = cube("Vestibule", (-5.15, 0, 1.45), (0.16, 1.85, 1.85), dark)
    parent(curtain, root)
    tender = cube("Tender", (-7.85, 0, 1.38), (5.10, 2.16, 2.12), shroud)
    bevel(tender, 0.12, 4)
    parent(tender, root)
    for s in (-1, 1):
        shoulder = cylinder(f"TenShoulder_{s}", (-7.55, s * 0.78, 2.36), 0.26, 4.40, shroud, verts=16)
        parent(shoulder, root)
    deck = cube("TenderDeck", (-7.70, 0, 2.50), (4.70, 1.52, 0.14), shroud)
    parent(deck, root)
    for i, ox in enumerate((-6.15, -6.65, -7.15, -7.65)):
        panel = cube(f"CoalCover_{i}", (ox, 0, 2.60), (0.46, 1.18, 0.06), dark)
        parent(panel, root)
    coal = cube("Coal", (-6.90, 0, 2.46), (2.20, 1.05, 0.22), dark)
    bevel(coal, 0.05, 2)
    parent(coal, root)
    hatch = cube("WaterHatch", (-9.35, 0, 2.58), (0.90, 0.72, 0.08), dark)
    parent(hatch, root)
    hinge = cube("HatchHinge", (-8.95, 0, 2.62), (0.08, 0.72, 0.04), steel)
    parent(hinge, root)
    fill = cylinder("FillCap", (-9.45, 0, 2.66), 0.14, 0.07, steel, rot=(0, 0, 0), verts=16)
    parent(fill, root)
    rear_chamfer = cube("RearChamfer", (-10.18, 0, 2.38), (0.42, 1.55, 0.18), shroud)
    bevel(rear_chamfer, 0.12, 4)
    parent(rear_chamfer, root)
    backup = cube("BackupLight", (-10.42, 0.42, 2.05), (0.06, 0.16, 0.12), lamp)
    parent(backup, root)
    cap_stenc = cube("CapacityStencil", (-10.42, 0.15, 1.55), (0.03, 0.55, 0.22), dark)
    parent(cap_stenc, root)
    buffer = cube("BufferBeam", (-10.42, 0, 0.72), (0.16, 1.60, 0.32), iron)
    parent(buffer, root)
    for s in (-1, 1):
        step = cube(f"RearStep_{s}", (-10.48, s * 0.72, 0.48), (0.16, 0.22, 0.06), steel)
        parent(step, root)
        pocket = cube(f"Poling_{s}", (-10.42, s * 0.95, 1.05), (0.06, 0.12, 0.12), dark)
        parent(pocket, root)
    for z in (0.90, 1.28, 1.66, 2.04):
        rung = cube(f"Ladder_{z}", (-10.46, -0.58, z), (0.035, 0.26, 0.03), steel)
        parent(rung, root)
    for yy in (-0.70, -0.46):
        rail = cube(f"LadderRail_{yy}", (-10.46, yy, 1.52), (0.03, 0.03, 1.36), steel)
        parent(rail, root)
    grab = cube("RoofGrab", (-10.22, -0.58, 2.36), (0.28, 0.26, 0.03), steel)
    parent(grab, root)
    for s in (-1, 1):
        letter = cube(f"TenderPanel_{s}", (-7.85, s * 1.09, 1.62), (2.6, 0.025, 0.22), cream)
        parent(letter, root)
        for zi, z in enumerate((0.55, 0.95, 2.15)):
            riv = cube(f"Rivet_{s}_{zi}", (-7.85, s * 1.09, z), (4.7, 0.02, 0.025), dark)
            parent(riv, root)
        for gx in (-6.15, -7.35, -8.55, -9.55):
            ir = cube(f"Grab_{s}_{gx}", (gx, s * 1.10, 1.95), (0.22, 0.03, 0.03), steel)
            parent(ir, root)
        rail = cube(f"SideRail_{s}", (-7.85, s * 1.11, 2.22), (4.4, 0.025, 0.025), steel)
        parent(rail, root)
        for cx in (-6.40, -9.25):
            sf = cube(f"TenFrame_{s}_{cx}", (cx, s * 0.92, 0.36), (1.70, 0.08, 0.20), iron)
            parent(sf, root)
            bar = cube(f"Equalizer_{s}_{cx}", (cx, s * 0.92, 0.50), (1.50, 0.04, 0.05), steel)
            parent(bar, root)
        fst = cube(f"FrontStep_{s}", (-5.38, s * 1.12, 0.55), (0.22, 0.18, 0.05), steel)
        parent(fst, root)

    lead_r, drive_r, trail_r, ten_r = 0.38, 0.78, 0.42, 0.26
    for x in (3.55, 2.75):
        for s in (-1, 1):
            for p in build_wheel(f"Lead_{x}_{s}", (x, s * 0.78, lead_r), lead_r, 0.12, iron, steel):
                parent(p, root)
    for x in driver_xs:
        for s in (-1, 1):
            for p in build_wheel(f"Drive_{x}_{s}", (x, s * 0.98, drive_r), drive_r, 0.16, iron, steel):
                parent(p, root)
    for x in (-2.55, -3.25):
        for s in (-1, 1):
            for p in build_wheel(f"Trail_{x}_{s}", (x, s * 0.78, trail_r), trail_r, 0.12, iron, steel):
                parent(p, root)
    for x in ten_xs:
        for s in (-1, 1):
            for p in build_wheel(f"Ten_{x}_{s}", (x, s * 0.78, ten_r), ten_r, 0.10, iron, steel):
                parent(p, root)

    for s in (-1, 1):
        rod = cube(f"Rod_{s}", (0.15, s * 1.08, 0.82), (2.85, 0.05, 0.07), steel)
        parent(rod, root)
        cylb = cube(f"Cyl_{s}", (2.55, s * 0.72, 1.05), (0.85, 0.36, 0.42), dark)
        bevel(cylb, 0.04, 2)
        parent(cylb, root)

    coupler = cube("Coupler", (-10.55, 0, 0.72), (0.22, 0.16, 0.16), steel)
    parent(coupler, root)

    bpy.ops.object.camera_add(location=(12, -14, 6), rotation=(1.15, 0, 0.7))
    bpy.context.scene.camera = bpy.context.active_object
    bpy.ops.object.light_add(type="SUN", location=(8, -6, 14))
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
        filepath=path,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
        export_yup=True,
    )


if __name__ == "__main__":
    build()
    out = argv_out()
    export_glb(out)
    print("Exported", out)
