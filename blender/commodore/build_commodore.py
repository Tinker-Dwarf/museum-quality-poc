"""
Commodore Vanderbilt — museum silhouette pass.
Stretched prow + barrel + cab fairing + close tender + scalloped skirt.
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
    rim = cylinder(f"{tag}_rim", (x, y, z), r * 0.78, width * 0.55, steel, rot=(math.pi / 2, 0, 0), verts=24)
    hub = cylinder(f"{tag}_hub", (x, y, z), r * 0.20, width * 1.15, steel, rot=(math.pi / 2, 0, 0), verts=16)
    parts = [tire, rim, hub]
    for i in range(spokes):
        a = i * (math.pi * 2 / spokes)
        sx = x + math.cos(a) * r * 0.48
        sz = z + math.sin(a) * r * 0.48
        sp = cube(
            f"{tag}_sp{i}",
            (sx, y, sz),
            (r * 0.78, width * 0.28, 0.04),
            steel,
            rot=(0, 0, a),
        )
        parts.append(sp)
    return parts


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

    barrel = cylinder("Barrel", (0.2, 0, YB), R, 7.2, shroud, verts=48)
    parent(barrel, root)

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

    for i in range(4):
        for s in (-1, 1):
            lv = cube(f"Louver_{i}_{s}", (4.35 + i * 0.16, s * 0.95, 1.05), (0.04, 0.06, 0.42), dark)
            parent(lv, root)

    cab = cube("Cab", (-3.55, 0, 1.58), (2.35, 2.22, 2.35), shroud)
    bevel(cab, 0.10, 3)
    parent(cab, root)
    roof = cylinder("CabRoof", (-3.55, 0, 1.72), 1.10, 2.22, shroud, verts=28)
    parent(roof, root)
    for s in (-1, 1):
        frame = cube(f"WinFrame_{s}", (-3.95, s * 1.12, 2.05), (0.66, 0.05, 0.50), dark)
        pane = cube(f"Win_{s}", (-3.95, s * 1.14, 2.05), (0.56, 0.04, 0.40), glass)
        parent(frame, root)
        parent(pane, root)

    well = cylinder("StackWell", (2.15, 0, YB + R - 0.02), 0.20, 0.10, dark, rot=(0, 0, 0), verts=20)
    parent(well, root)

    for s in (-1, 1):
        belt = cube(f"Belt_{s}", (0.1, s * 1.16, 2.08), (8.4, 0.035, 0.035), dark)
        parent(belt, root)

    skirt = cube("SkirtBody", (0.15, 0, 0.95), (8.6, 2.18, 0.85), shroud)
    bevel(skirt, 0.05, 2)
    parent(skirt, root)
    driver_xs = (1.55, 0.15, -1.25)
    for x in driver_xs:
        for s in (-1, 1):
            bay = cube(f"Bay_{x}_{s}", (x, s * 1.12, 0.72), (1.15, 0.08, 0.95), dark)
            parent(bay, root)

    frame = cube("Frame", (0.0, 0, 0.58), (8.0, 0.70, 0.28), iron)
    parent(frame, root)

    tender = cube("Tender", (-6.85, 0, 1.52), (4.15, 2.16, 2.40), shroud)
    bevel(tender, 0.10, 3)
    parent(tender, root)
    t_roof = cube("TenderRoof", (-6.85, 0, 2.78), (4.15, 1.70, 0.22), shroud)
    bevel(t_roof, 0.08, 2)
    parent(t_roof, root)
    hatch = cube("Hatch", (-6.35, 0, 2.92), (2.2, 1.35, 0.12), dark)
    parent(hatch, root)
    for s in (-1, 1):
        letter = cube(f"TenderPanel_{s}", (-7.05, s * 1.09, 1.62), (2.6, 0.03, 0.32), dark)
        parent(letter, root)

    lead_r, drive_r, trail_r, ten_r = 0.38, 0.78, 0.42, 0.32
    for x in (3.55, 2.75):
        for s in (-1, 1):
            for p in build_wheel(f"Lead_{x}_{s}", (x, s * 0.78, lead_r), lead_r, 0.12, iron, steel, spokes=10):
                parent(p, root)
    for x in driver_xs:
        for s in (-1, 1):
            for p in build_wheel(f"Drive_{x}_{s}", (x, s * 0.98, drive_r), drive_r, 0.16, iron, steel, spokes=14):
                parent(p, root)
    for x in (-2.55, -3.25):
        for s in (-1, 1):
            for p in build_wheel(f"Trail_{x}_{s}", (x, s * 0.78, trail_r), trail_r, 0.12, iron, steel, spokes=10):
                parent(p, root)
    for x in (-5.55, -6.35, -7.35, -8.15):
        for s in (-1, 1):
            for p in build_wheel(f"Ten_{x}_{s}", (x, s * 0.78, ten_r), ten_r, 0.12, iron, steel, spokes=8):
                parent(p, root)

    for s in (-1, 1):
        rod = cube(f"Rod_{s}", (0.15, s * 1.08, 0.82), (2.85, 0.05, 0.07), steel)
        parent(rod, root)
        cylb = cube(f"Cyl_{s}", (2.55, s * 0.72, 1.05), (0.85, 0.36, 0.42), dark)
        bevel(cylb, 0.04, 2)
        parent(cylb, root)

    coupler = cube("Coupler", (-9.05, 0, 0.82), (0.28, 0.16, 0.16), steel)
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
