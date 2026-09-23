"""
Commodore Vanderbilt streamliner — continuous shell, not a boiler-on-a-box.
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


def mat(name, color, metallic=0.35, roughness=0.38, emission=None):
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


def cube(name, loc, size, material, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    ob.data.materials.append(material)
    return ob


def cyl(name, loc, r, depth, material, rot=(0, math.pi / 2, 0), verts=48):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=r, depth=depth, location=loc, rotation=rot, vertices=verts
    )
    ob = bpy.context.active_object
    ob.name = name
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    ob.data.materials.append(material)
    return ob


def sphere(name, loc, r, material, segs=32):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=segs, ring_count=segs)
    ob = bpy.context.active_object
    ob.name = name
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    ob.data.materials.append(material)
    return ob


def bevel(ob, width=0.12, segs=4):
    m = ob.modifiers.new("Bevel", "BEVEL")
    m.width = width
    m.segments = segs
    m.limit_method = "ANGLE"
    m.angle_limit = math.radians(30)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=m.name)
    return ob


def parent(child, root):
    child.parent = root
    child.matrix_parent_inverse = root.matrix_world.inverted()


def build():
    clear_scene()

    shell = mat("NYCShell", (0.12, 0.145, 0.175), metallic=0.28, roughness=0.34)
    shell_dark = mat("NYCShadow", (0.07, 0.08, 0.10), metallic=0.35, roughness=0.4)
    silver = mat("Brightwork", (0.62, 0.64, 0.68), metallic=0.9, roughness=0.2)
    iron = mat("Tire", (0.04, 0.04, 0.045), metallic=0.55, roughness=0.45)
    glass = mat("CabGlass", (0.04, 0.07, 0.10), metallic=0.05, roughness=0.06)
    lamp = mat("Lamp", (0.95, 0.92, 0.78), metallic=0.05, roughness=0.12, emission=((1.0, 0.95, 0.72), 8.0))
    letter = mat("LetterPanel", (0.16, 0.18, 0.21), metallic=0.2, roughness=0.45)

    root = bpy.data.objects.new("CommodoreVanderbilt", None)
    bpy.context.collection.objects.link(root)

    W = 1.55
    H = 2.15
    Z0 = 0.52
    Z1 = Z0 + H
    nose_x = 6.35
    cab_x = -3.55

    hull_len = nose_x - 0.9 - (cab_x - 1.15)
    hull_cx = ((nose_x - 0.9) + (cab_x - 1.15)) / 2
    hull = cube("Hull", (hull_cx, 0, (Z0 + Z1) / 2), (hull_len, W, H), shell)
    bevel(hull, 0.18, 5)
    parent(hull, root)

    nose_box = cube("NoseBlock", (5.55, 0, 1.55), (1.7, W * 0.98, 2.05), shell)
    bevel(nose_box, 0.22, 6)
    parent(nose_box, root)
    wedge = cube("NoseWedge", (6.15, 0, 0.72), (1.15, W * 0.92, 0.85), shell, rot=(0.38, 0, 0))
    bevel(wedge, 0.10, 3)
    parent(wedge, root)
    snout = sphere("Snout", (6.45, 0, 1.55), 0.62, shell, segs=28)
    snout.scale = (0.55, 1.05, 1.15)
    bpy.context.view_layer.objects.active = snout
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    parent(snout, root)

    for z in (1.78, 1.28):
        bezel = cyl("Bezel", (6.72, 0, z), 0.16, 0.08, silver, verts=24)
        parent(bezel, root)
        lite = sphere("Lamp", (6.78, 0, z), 0.12, lamp, segs=16)
        parent(lite, root)

    stack_ring = cyl("StackRing", (3.15, 0, Z1 + 0.02), 0.22, 0.06, shell_dark, rot=(0, 0, 0), verts=24)
    parent(stack_ring, root)
    stack_void = cyl("StackVoid", (3.15, 0, Z1 - 0.04), 0.16, 0.10, shell_dark, rot=(0, 0, 0), verts=20)
    parent(stack_void, root)

    cab = cube("Cab", (cab_x, 0, Z1 + 0.12), (1.85, W * 1.02, 0.55), shell)
    bevel(cab, 0.08, 3)
    parent(cab, root)
    for y, name in ((W / 2 + 0.01, "GlassL"), (-W / 2 - 0.01, "GlassR")):
        g = cube(name, (cab_x + 0.15, y, Z1 - 0.15), (0.55, 0.04, 0.38), glass)
        parent(g, root)
    g_rear = cube("GlassRear", (cab_x - 0.92, 0, Z1 - 0.15), (0.04, 0.70, 0.38), glass)
    parent(g_rear, root)

    skirt = cube("Skirt", (1.1, 0, Z0 - 0.08), (9.4, W + 0.04, 0.38), shell)
    bevel(skirt, 0.06, 2)
    parent(skirt, root)
    for x in (2.35, 1.25, 0.15):
        for y in (W / 2 + 0.01, -W / 2 - 0.01):
            cut = cube(f"WheelArch_{x}_{y}", (x, y, 0.55), (0.95, 0.05, 0.55), shell_dark)
            parent(cut, root)

    t_len = 4.55
    t_cx = cab_x - 1.05 - t_len / 2
    tender = cube("Tender", (t_cx, 0, (Z0 + Z1 + 0.15) / 2), (t_len, W, H + 0.15), shell)
    bevel(tender, 0.10, 3)
    parent(tender, root)
    hatch = cube("TenderHatch", (t_cx + 0.4, 0, Z1 + 0.22), (2.4, W * 0.72, 0.16), shell_dark)
    parent(hatch, root)
    letter_p = cube("TenderLetter", (t_cx - 0.4, W / 2 + 0.01, 1.55), (2.2, 0.03, 0.35), letter)
    parent(letter_p, root)
    coupler = cube("Coupler", (t_cx - t_len / 2 - 0.12, 0, 0.85), (0.22, 0.16, 0.16), silver)
    parent(coupler, root)

    def wheel_set(tag, x, y, r, width=0.14):
        tire = cyl(f"{tag}_tire", (x, y, r), r, width, iron, rot=(math.pi / 2, 0, 0), verts=28)
        hub = cyl(f"{tag}_hub", (x, y, r), r * 0.32, width * 1.1, silver, rot=(math.pi / 2, 0, 0), verts=16)
        parent(tire, root)
        parent(hub, root)

    for x in (4.55, 3.85):
        for y in (0.58, -0.58):
            wheel_set(f"Lead_{x}", x, y, 0.28)
    for x in (2.35, 1.25, 0.15):
        for y in (0.62, -0.62):
            wheel_set(f"Drive_{x}", x, y, 0.48, 0.16)
    for x in (-1.05, -1.75):
        for y in (0.58, -0.58):
            wheel_set(f"Trail_{x}", x, y, 0.30)
    for x in (t_cx + 1.35, t_cx + 0.35, t_cx - 0.65):
        for y in (0.58, -0.58):
            wheel_set(f"Ten_{x}", x, y, 0.26)

    for y in (0.72, -0.72):
        rod = cube(f"Rod_{y}", (1.25, y, 0.48), (2.3, 0.04, 0.05), silver)
        parent(rod, root)

    bpy.ops.object.camera_add(location=(11, -13, 5.5), rotation=(1.15, 0, 0.72))
    bpy.context.scene.camera = bpy.context.active_object
    bpy.ops.object.light_add(type="SUN", location=(8, -5, 12))
    bpy.context.active_object.data.energy = 4
    return root


def export_glb(path):
    bpy.ops.object.select_all(action="DESELECT")
    root = bpy.data.objects.get("CommodoreVanderbilt")
    if root:
        root.select_set(True)
        bpy.context.view_layer.objects.active = root
        for ob in bpy.data.objects:
            if ob.parent == root:
                ob.select_set(True)
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
    print(f"Exported {out}")
