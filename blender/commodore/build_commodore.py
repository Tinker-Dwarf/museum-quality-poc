"""
Procedural Commodore Vanderbilt-style 4-6-4 Hudson streamliner.
Run:
  blender --background --python build_commodore.py -- --out commodore.glb
"""
import bpy
import math
import sys
from mathutils import Vector


def argv_out():
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1 :]
        if "--out" in args:
            return args[args.index("--out") + 1]
    return "commodore.glb"


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.meshes):
        bpy.data.meshes.remove(block)
    for block in list(bpy.data.materials):
        bpy.data.materials.remove(block)
    for block in list(bpy.data.curves):
        bpy.data.curves.remove(block)


def mat(name, color, metallic=0.15, roughness=0.35, emission=None):
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


def add_cube(name, loc, scale, material, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    ob.data.materials.append(material)
    return ob


def add_cyl(name, loc, r, depth, material, rot=(math.pi / 2, 0, 0), verts=32):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=r, depth=depth, location=loc, rotation=rot, vertices=verts
    )
    ob = bpy.context.active_object
    ob.name = name
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    ob.data.materials.append(material)
    return ob


def add_uvsphere(name, loc, r, material, segs=24):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=segs, ring_count=segs)
    ob = bpy.context.active_object
    ob.name = name
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    ob.data.materials.append(material)
    return ob


def add_torus(name, loc, major, minor, material, rot=(math.pi / 2, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(
        location=loc, rotation=rot, major_radius=major, minor_radius=minor
    )
    ob = bpy.context.active_object
    ob.name = name
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    ob.data.materials.append(material)
    return ob


def wheel(name, loc, radius, width, steel, hub, tire):
    tire_ob = add_cyl(f"{name}_tire", loc, radius, width, tire, verts=24)
    hub_ob = add_cyl(f"{name}_hub", loc, radius * 0.35, width * 1.15, hub, verts=16)
    spokes = []
    for i in range(8):
        a = i * (math.pi / 4)
        s = add_cube(
            f"{name}_spoke_{i}",
            loc,
            (radius * 0.42, width * 0.12, 0.03),
            steel,
            rot=(0, 0, a),
        )
        spokes.append(s)
    return [tire_ob, hub_ob] + spokes


def join(name, objects):
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objects:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    objects[0].name = name
    return objects[0]


def build():
    clear_scene()

    gunmetal = mat("Gunmetal", (0.12, 0.13, 0.15), metallic=0.85, roughness=0.28)
    gray = mat("StreamlineGray", (0.22, 0.24, 0.26), metallic=0.55, roughness=0.32)
    black = mat("BlackIron", (0.03, 0.03, 0.03), metallic=0.7, roughness=0.4)
    silver = mat("Silver", (0.55, 0.57, 0.6), metallic=0.9, roughness=0.18)
    brass = mat("Brass", (0.62, 0.42, 0.12), metallic=0.85, roughness=0.25)
    window = mat("CabGlass", (0.05, 0.08, 0.12), metallic=0.1, roughness=0.08)
    coal = mat("Coal", (0.04, 0.04, 0.045), metallic=0.0, roughness=0.9)
    lamp = mat("Headlamp", (0.95, 0.92, 0.75), metallic=0.0, roughness=0.15, emission=((1.0, 0.95, 0.7), 12.0))
    stripe = mat("NYCStripe", (0.75, 0.12, 0.1), metallic=0.2, roughness=0.4)
    wood = mat("TenderDeck", (0.18, 0.1, 0.05), metallic=0.0, roughness=0.7)

    parts = []

    body = add_cube("Body", (0.0, 0.0, 1.55), (4.4, 0.72, 0.72), gray)
    parts.append(body)
    casing = add_cyl("Casing", (0.15, 0.0, 1.72), 0.78, 8.2, gray, rot=(0, math.pi / 2, 0), verts=36)
    parts.append(casing)
    nose = add_uvsphere("Nose", (4.55, 0.0, 1.55), 0.78, gray, segs=28)
    parts.append(nose)
    cap = add_cyl("NoseCap", (5.15, 0.0, 1.55), 0.38, 0.22, silver, rot=(0, math.pi / 2, 0))
    parts.append(cap)
    light = add_uvsphere("Headlamp", (5.28, 0.0, 1.55), 0.18, lamp, segs=16)
    parts.append(light)

    parts.append(add_cube("StripeL", (0.2, 0.74, 1.18), (4.6, 0.02, 0.04), stripe))
    parts.append(add_cube("StripeR", (0.2, -0.74, 1.18), (4.6, 0.02, 0.04), stripe))

    cab = add_cube("Cab", (-4.15, 0.0, 1.85), (0.95, 0.78, 0.95), gray)
    parts.append(cab)
    parts.append(add_cube("CabRoof", (-4.15, 0.0, 2.78), (1.05, 0.82, 0.08), gunmetal))
    parts.append(add_cube("WindowL", (-3.85, 0.80, 2.15), (0.35, 0.03, 0.28), window))
    parts.append(add_cube("WindowR", (-3.85, -0.80, 2.15), (0.35, 0.03, 0.28), window))
    parts.append(add_cube("WindowRear", (-5.08, 0.0, 2.15), (0.03, 0.55, 0.28), window))

    parts.append(add_cyl("Stack", (2.4, 0.0, 2.55), 0.16, 0.35, gunmetal, rot=(0, 0, 0), verts=16))

    parts.append(add_cube("Pilot", (5.05, 0.0, 0.55), (0.55, 0.85, 0.18), gunmetal, rot=(0.35, 0, 0)))
    for y in (-0.55, 0.0, 0.55):
        parts.append(add_cube(f"PilotBar_{y}", (5.35, y, 0.42), (0.35, 0.04, 0.04), silver))

    parts.append(add_cyl("CylL", (2.6, 0.95, 0.85), 0.22, 1.1, gunmetal, rot=(0, math.pi / 2, 0)))
    parts.append(add_cyl("CylR", (2.6, -0.95, 0.85), 0.22, 1.1, gunmetal, rot=(0, math.pi / 2, 0)))

    lead_x = [4.15, 3.45]
    drive_x = [2.15, 1.15, 0.15]
    trail_x = [-1.05, -1.75]

    wheel_parts = []
    for x in lead_x:
        for y in (0.72, -0.72):
            wheel_parts += wheel(f"Lead_{x}_{y}", (x, y, 0.38), 0.32, 0.12, silver, gunmetal, black)
    for x in drive_x:
        for y in (0.78, -0.78):
            wheel_parts += wheel(f"Drive_{x}_{y}", (x, y, 0.58), 0.52, 0.16, silver, gunmetal, black)
    for x in trail_x:
        for y in (0.72, -0.72):
            wheel_parts += wheel(f"Trail_{x}_{y}", (x, y, 0.38), 0.32, 0.12, silver, gunmetal, black)

    parts.append(add_cube("RodL", (1.15, 0.98, 0.58), (1.15, 0.04, 0.05), silver))
    parts.append(add_cube("RodR", (1.15, -0.98, 0.58), (1.15, 0.04, 0.05), silver))

    tender = add_cube("Tender", (-7.15, 0.0, 1.35), (1.85, 0.72, 0.85), gray)
    parts.append(tender)
    parts.append(add_cube("CoalLoad", (-6.85, 0.0, 2.15), (1.15, 0.55, 0.28), coal))
    parts.append(add_cube("TenderDeck", (-8.35, 0.0, 1.95), (0.45, 0.72, 0.08), wood))
    for x in (-6.35, -7.15, -7.95):
        for y in (0.72, -0.72):
            wheel_parts += wheel(f"Ten_{x}_{y}", (x, y, 0.32), 0.28, 0.11, silver, gunmetal, black)

    parts.append(add_cube("Coupler", (-9.15, 0.0, 0.85), (0.18, 0.12, 0.12), gunmetal))
    parts.append(add_cube("NumberPlate", (4.85, 0.0, 2.05), (0.08, 0.28, 0.16), brass))

    all_obs = parts + wheel_parts
    loco = join("CommodoreVanderbilt", all_obs)

    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    loco.location = (0.0, 0.0, 0.0)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    bpy.ops.object.camera_add(location=(10, -12, 5), rotation=(1.1, 0, 0.7))
    bpy.context.scene.camera = bpy.context.active_object
    bpy.ops.object.light_add(type="SUN", location=(6, -4, 10))
    bpy.context.active_object.data.energy = 4

    return loco


def export_glb(path):
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        use_selection=False,
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
        export_yup=True,
    )


if __name__ == "__main__":
    loco = build()
    out = argv_out()
    export_glb(out)
    print(f"Exported {out}")
    print(f"Object: {loco.name} verts={len(loco.data.vertices)}")
