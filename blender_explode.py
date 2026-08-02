"""Interactive exploded-view scene of NeuralCard — accurate colors, correct
explosion directions, moving cameras, and re-assembly ending on the card.
Builds and SAVES NeuralCard_exploded.blend (no render). Press Space to play.
Run: blender --background --python blender_explode.py

Timeline (24 fps, 320 frames = ~13 s):
  f1-70    explode  (front parts lift up, back parts drop down, slight radial spread)
  f70-215  exploded hold, cameras tour it (wide -> medium -> close)
  f215-275 re-assemble (everything flies back)
  f275-320 hold on the finished card, camera settles
Cameras orbit/crane CONTINUOUSLY through every segment.
"""
import bpy
import os
import math
from mathutils import Vector, Matrix

H = os.path.expanduser("~/kicad-projects/NeuralCard")
GLB = f"{H}/NeuralCard.glb"
BLEND = f"{H}/NeuralCard_exploded.blend"
HDRI = "/Applications/Blender.app/Contents/Resources/5.1/datafiles/studiolights/world/studio.exr"
F_EXPL, F_HOLD, F_BACK, F_END = 70, 215, 275, 320

# ---------------------------------------------------------------- clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for coll in (bpy.data.meshes, bpy.data.cameras, bpy.data.lights, bpy.data.materials, bpy.data.worlds):
    for d in list(coll):
        coll.remove(d)

# ---------------------------------------------------------------- import; bake world xform -> mm; unparent
bpy.ops.import_scene.gltf(filepath=GLB)
meshes = [o for o in bpy.data.objects if o.type == 'MESH' and len(o.data.vertices)]
S = Matrix.Scale(1000.0, 4)
for o in meshes:
    o.data = o.data.copy()              # unique-ify shared meshes (LEDs)
    o.data.transform(o.matrix_world)    # bake Z-up world transform into geometry
    o.data.transform(S)                 # meters -> mm
    o.parent = None                     # CRITICAL: no rotated glTF parents -> local == world
    o.matrix_world = Matrix.Identity(4)
# delete now-empty glTF node hierarchy
for o in [o for o in bpy.data.objects if o.type == 'EMPTY']:
    bpy.data.objects.remove(o)
bpy.context.view_layer.update()


def world_bbox(objs):
    mn = [1e9, 1e9, 1e9]
    mx = [-1e9, -1e9, -1e9]
    for o in objs:
        for v in o.data.vertices:
            w = o.matrix_world @ v.co
            for i in range(3):
                mn[i] = min(mn[i], w[i])
                mx[i] = max(mx[i], w[i])
    return Vector(mn), Vector(mx)


bmn, bmx = world_bbox(meshes)
CENTER = (bmn + bmx) * 0.5
print("ASSEMBLY center", [round(c, 1) for c in CENTER], "size", [round(s, 1) for s in (bmx - bmn)])

# ---------------------------------------------------------------- classify by Z vs the bare board
front, back, board = [], [], []
for o in meshes:
    omn, omx = world_bbox([o])
    c = (omn + omx) * 0.5
    if (omx.x - omn.x) > 60 and (omx.y - omn.y) > 40:
        board.append(o)
    elif c.z > 0.5:
        front.append(o)
    elif c.z < -0.5:
        back.append(o)
    else:
        board.append(o)
# sanity: LEDs (24 small parts) must be the front group
print(f"CLASSIFY board={len(board)} front={len(front)} back={len(back)}")

# ---------------------------------------------------------------- ACCURATE materials
# Keep KiCad's true base colors; only correct metallic/roughness (KiCad exports met=1 rough=1).
led_mats = set()
for o in front:                          # collect materials used only by LEDs
    for slot in o.material_slots:
        if slot.material:
            led_mats.add(slot.material.name)

for m in bpy.data.materials:
    if not m.use_nodes:
        continue
    b = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not b:
        continue
    col = b.inputs['Base Color'].default_value
    r, g, bl = col[0], col[1], col[2]
    lum = (r + g + bl) / 3.0
    sat = max(r, g, bl) - min(r, g, bl)

    def setin(name, val):
        if name in b.inputs:
            b.inputs[name].default_value = val

    alpha = b.inputs['Alpha'].default_value if 'Alpha' in b.inputs else 1.0
    if m.name in led_mats and (sat > 0.15 or lum > 0.5):
        # LED lens/body accents -> red translucent with a soft inner glow
        setin('Base Color', (0.9, 0.04, 0.03, 1.0))
        setin('Metallic', 0.0)
        setin('Roughness', 0.18)
        if 'Transmission Weight' in b.inputs:
            b.inputs['Transmission Weight'].default_value = 0.35
        if 'Emission Color' in b.inputs:
            b.inputs['Emission Color'].default_value = (1.0, 0.05, 0.03, 1.0)
        if 'Emission Strength' in b.inputs:
            b.inputs['Emission Strength'].default_value = 2.5
        m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else m.blend_method
    elif g > r * 1.3 and g > bl * 1.3 and alpha < 0.99:
        # SOLDERMASK -> classic glossy PCB green, opaque
        setin('Base Color', (0.016, 0.22, 0.078, 1.0))
        setin('Alpha', 1.0)
        setin('Metallic', 0.0)
        setin('Roughness', 0.32)
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 0.5
        if 'Coat Roughness' in b.inputs:
            b.inputs['Coat Roughness'].default_value = 0.12
    elif lum > 0.85 and sat < 0.1 and alpha < 0.99:
        # SILKSCREEN -> pure matte white, opaque
        setin('Base Color', (0.93, 0.93, 0.93, 1.0))
        setin('Alpha', 1.0)
        setin('Metallic', 0.0)
        setin('Roughness', 0.55)
    elif r > 0.45 and g > 0.3 and bl < 0.25:
        # GOLD (ENIG pads, pins, LED frames) -> real metal
        setin('Metallic', 1.0)
        setin('Roughness', 0.25)
    elif sat < 0.12 and lum > 0.35:
        # GREY/WHITE METAL (coin holder steel, shields, button caps)
        setin('Metallic', 1.0)
        setin('Roughness', 0.32)
    elif lum < 0.15:
        # BLACK PLASTIC / IC bodies
        setin('Metallic', 0.0)
        setin('Roughness', 0.42)
    else:
        # FR4 edge & everything else: keep color, sane roughness
        setin('Metallic', 0.0)
        setin('Roughness', 0.6)

# ---------------------------------------------------------------- explosion + re-assembly keyframes
def key_loc(o, frame, loc):
    o.location = loc
    o.keyframe_insert("location", frame=frame)


for grp, zdir, mag in ((front, +1, 15.0), (back, -1, 24.0)):
    for o in grp:
        omn, omx = world_bbox([o])
        c = (omn + omx) * 0.5
        radial = Vector((c.x - CENTER.x, c.y - CENTER.y, 0.0))
        if radial.length > 0.01:
            radial.normalize()
        target = (radial.x * 7.0, radial.y * 7.0, zdir * mag)
        key_loc(o, 1, (0, 0, 0))
        key_loc(o, F_EXPL, target)       # exploded
        key_loc(o, F_HOLD, target)       # hold
        key_loc(o, F_BACK, (0, 0, 0))    # fly back together

# ---------------------------------------------------------------- world (HDRI) + floor + lights
world = bpy.data.worlds.new("Studio")
bpy.context.scene.world = world
world.use_nodes = True
wt = world.node_tree
wt.nodes.clear()
env = wt.nodes.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(HDRI)
bg = wt.nodes.new("ShaderNodeBackground")
bg.inputs[1].default_value = 0.35
wout = wt.nodes.new("ShaderNodeOutputWorld")
wt.links.new(env.outputs[0], bg.inputs[0])
wt.links.new(bg.outputs[0], wout.inputs[0])

bpy.ops.mesh.primitive_plane_add(size=1500, location=(CENTER.x, CENTER.y, -32))
floor = bpy.context.object
fm = bpy.data.materials.new("floor")
fm.use_nodes = True
fb = fm.node_tree.nodes["Principled BSDF"]
fb.inputs["Base Color"].default_value = (0.02, 0.022, 0.028, 1.0)
fb.inputs["Roughness"].default_value = 0.38
fb.inputs["Metallic"].default_value = 0.4
floor.data.materials.append(fm)

aim = bpy.data.objects.new("AIM", None)
bpy.context.collection.objects.link(aim)
aim.location = CENTER


def add_area(name, loc, power, size):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = power
    ld.size = size
    ob = bpy.data.objects.new(name, ld)
    bpy.context.collection.objects.link(ob)
    ob.location = loc
    c = ob.constraints.new('TRACK_TO')
    c.target = aim
    return ob


add_area("key", (CENTER.x + 70, CENTER.y - 90, 130), 4.2e5, 110)
add_area("rim", (CENTER.x - 30, CENTER.y + 120, 90), 2.6e5, 90)
add_area("under", (CENTER.x, CENTER.y - 30, -60), 1.2e5, 80)   # lights the dropped back parts

# ---------------------------------------------------------------- cameras: continuous orbit + crane
def make_cam(name, offset, keys, target_loc=None, lens=55):
    """keys: list of (frame, orbit_deg, cam_offset) -> pivot orbits, camera cranes."""
    piv = bpy.data.objects.new(f"{name}_piv", None)
    bpy.context.collection.objects.link(piv)
    piv.location = target_loc if target_loc else CENTER
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cam = bpy.data.objects.new(name, cd)
    bpy.context.collection.objects.link(cam)
    cam.parent = piv
    a = bpy.data.objects.new(f"{name}_aim", None)
    bpy.context.collection.objects.link(a)
    a.location = target_loc if target_loc else CENTER
    tc = cam.constraints.new('TRACK_TO')
    tc.target = a
    for fr, ang, off in keys:
        piv.rotation_euler = (0, 0, math.radians(ang))
        piv.keyframe_insert("rotation_euler", frame=fr)
        cam.location = off
        cam.keyframe_insert("location", frame=fr)
    return cam


# WIDE rides through the explosion: orbits 60 deg and cranes up as parts separate
cam_wide = make_cam("Wide", (0, -190, 70), [
    (1, -30, (0, -190, 55)),
    (F_EXPL, 10, (0, -185, 95)),
    (95, 30, (0, -180, 105)),
])
# MEDIUM sweeps around the exploded stack
cam_med = make_cam("Med", (0, -120, 60), [
    (95, 40, (0, -130, 75)),
    (165, 105, (0, -110, 40)),
])
# CLOSE pushes in on the glowing LED layer
close_t = Vector((CENTER.x + 8, CENTER.y, CENTER.z + 10))
cam_close = make_cam("Close", (0, -60, 26), [
    (165, 110, (0, -64, 30)),
    (F_HOLD, 150, (0, -44, 16)),
], target_loc=close_t, lens=70)
# FINAL watches the re-assembly, then settles low on the finished card
cam_final = make_cam("Final", (0, -150, 80), [
    (F_HOLD, 160, (0, -165, 95)),
    (F_BACK, 200, (0, -135, 45)),
    (F_END, 215, (0, -115, 28)),
])

scene = bpy.context.scene
for fr, cam in ((1, cam_wide), (95, cam_med), (165, cam_close), (F_HOLD, cam_final)):
    mk = scene.timeline_markers.new(cam.name, frame=fr)
    mk.camera = cam
scene.camera = cam_wide

# ---------------------------------------------------------------- scene / eevee settings
scene.frame_start = 1
scene.frame_end = F_END
scene.frame_current = 1
scene.render.fps = 24
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
try:
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception:
    scene.render.engine = 'BLENDER_EEVEE'
ee = scene.eevee
for attr, val in (("use_raytracing", True), ("taa_render_samples", 64), ("taa_samples", 16)):
    if hasattr(ee, attr):
        try:
            setattr(ee, attr, val)
        except Exception:
            pass
try:
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = -0.4
except Exception:
    pass

# open viewports in rendered shading
for scr in bpy.data.screens:
    for area in scr.areas:
        if area.type == 'VIEW_3D':
            for sp in area.spaces:
                if sp.type == 'VIEW_3D':
                    sp.shading.type = 'RENDERED'
                    sp.shading.use_scene_lights = True
                    sp.shading.use_scene_world = True

bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("SAVED", BLEND)
