"""Düymə olsa · Ep01 — tabletop scene, built entirely from code.

Run:
  blender -b --factory-startup -P scene/build_scene.py -- [--render] [--still SEC]
          [--res 0.6667] [--samples 40] [--start F] [--end F] [--out DIR]

Builds the scene from episode.json (timings) and textures/, saves scene/ep01.blend,
optionally renders background frames (the UI is a separate HTML layer, see ui/).
"""
import bpy, bmesh, json, math, os, sys
from mathutils import Vector, Matrix, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EP = json.load(open(os.path.join(ROOT, 'episode.json')))
FPS = EP['fps']
SC = EP['scene']
TEX = os.path.join(HERE, 'textures')

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []


def arg(name, default=None, cast=str):
    if name in argv:
        i = argv.index(name)
        return cast(argv[i + 1]) if i + 1 < len(argv) and not argv[i + 1].startswith('--') else True
    return default


def F(sec):
    return round(sec * FPS) + 1  # Blender frames start at 1


TABLE_Z = 0.75
GLASS_XY = (0.015, -0.10)

# ───────────────────────────── helpers ─────────────────────────────


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.fps = FPS
    s.frame_start = 1
    s.frame_end = F(EP['ui']['end_card']) - 1
    return s


def link(obj, coll=None):
    (coll or bpy.context.scene.collection).objects.link(obj)
    return obj


def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def mesh_obj(name, bm, coll=None, smooth=True, mat=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    if mat:
        me.materials.append(mat)
    return link(o, coll)


def lathe(name, profile, segs=96, coll=None, mat=None, closed_top=False):
    """Solid of revolution from [(r, z), ...] (open polyline, bottom→top around the outside
    then back down the inside for walled objects)."""
    bm = bmesh.new()
    verts = [bm.verts.new((r, 0, z)) for r, z in profile]
    edges = [bm.edges.new((verts[i], verts[i + 1])) for i in range(len(verts) - 1)]
    bmesh.ops.spin(bm, geom=verts + edges, cent=(0, 0, 0), axis=(0, 0, 1), angle=2 * math.pi, steps=segs, use_duplicate=False)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    if closed_top:
        bmesh.ops.holes_fill(bm, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm, coll, mat=mat)


def subsurf(o, lv=2):
    m = o.modifiers.new('Subsurf', 'SUBSURF'); m.levels = lv; m.render_levels = lv
    return o


def key(o, path, frame, value=None, interp='BEZIER'):
    if value is not None:
        setattr(o, path, value)
    o.keyframe_insert(data_path=path, frame=frame)
    fc = None
    ad = o.animation_data
    if ad and ad.action:
        for c in ad.action.fcurves:
            if c.data_path == path:
                for kp in c.keyframe_points:
                    if kp.co[0] == frame:
                        kp.interpolation = interp
    return fc


def add_noise(o, path, strength, scale, index=None, phase=0.0):
    ad = o.animation_data
    if not ad or not ad.action:
        o.keyframe_insert(data_path=path, frame=1)
        ad = o.animation_data
    for c in ad.action.fcurves:
        if c.data_path == path and (index is None or c.array_index == index):
            m = c.modifiers.new('NOISE'); m.strength = strength; m.scale = scale; m.phase = phase + c.array_index * 7.3


# ───────────────────────────── materials ─────────────────────────────


def node_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    return m, nt, out


def principled(name, color, rough=0.5, spec=0.5, sss=0.0, sss_r=(1, .2, .1), metal=0.0, coat=0.0, sheen=0.0):
    m, nt, out = node_mat(name)
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Specular IOR Level'].default_value = spec
    if sss:
        b.inputs['Subsurface Weight'].default_value = sss
        b.inputs['Subsurface Radius'].default_value = sss_r
        b.inputs['Subsurface Scale'].default_value = 0.01
    if coat:
        b.inputs['Coat Weight'].default_value = coat
    if sheen:
        b.inputs['Sheen Weight'].default_value = sheen
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


def glass_mat(name, color=(1, 1, 1), ior=1.5, rough=0.0, shadow_tint=None, absorb=None):
    """Glass that also lets tinted light through for shadow rays (fake caustic glow)."""
    m, nt, out = node_mat(name)
    g = nt.nodes.new('ShaderNodeBsdfGlass')
    g.inputs['Color'].default_value = (*color, 1); g.inputs['IOR'].default_value = ior; g.inputs['Roughness'].default_value = rough
    t = nt.nodes.new('ShaderNodeBsdfTransparent')
    t.inputs['Color'].default_value = (*(shadow_tint or color), 1)
    lp = nt.nodes.new('ShaderNodeLightPath')
    mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Shadow Ray'], mix.inputs[0])
    nt.links.new(g.outputs[0], mix.inputs[1]); nt.links.new(t.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    if absorb:
        v = nt.nodes.new('ShaderNodeVolumeAbsorption')
        v.inputs['Color'].default_value = (*absorb[0], 1); v.inputs['Density'].default_value = absorb[1]
        nt.links.new(v.outputs[0], out.inputs['Volume'])
    return m


def porcelain_gold(name, axis='Z', band=(0.92, 0.97), radial=False):
    """White porcelain with a gold band (by height, or by radius for saucers)."""
    m, nt, out = node_mat(name)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    if radial:
        # distance from centre in generated coords (0..1 box) → 0 centre, ~0.7 rim
        vm = nt.nodes.new('ShaderNodeVectorMath'); vm.operation = 'SUBTRACT'; vm.inputs[1].default_value = (.5, .5, 0)
        nt.links.new(tc.outputs['Generated'], vm.inputs[0])
        mul = nt.nodes.new('ShaderNodeVectorMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = (1, 1, 0)
        nt.links.new(vm.outputs[0], mul.inputs[0])
        ln = nt.nodes.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'
        nt.links.new(mul.outputs[0], ln.inputs[0]); src = ln.outputs['Value']
    else:
        src = sep.outputs[axis]
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    r = ramp.color_ramp; r.interpolation = 'CONSTANT'
    r.elements[0].color = (0, 0, 0, 1)
    e1 = r.elements.new(band[0]); e1.color = (1, 1, 1, 1)
    e2 = r.elements.new(band[1]); e2.color = (0, 0, 0, 1)
    r.elements[1].position = 1.0; r.elements[1].color = (0, 0, 0, 1)
    nt.links.new(src, ramp.inputs[0])
    white = nt.nodes.new('ShaderNodeBsdfPrincipled')
    white.inputs['Base Color'].default_value = (.93, .91, .87, 1); white.inputs['Roughness'].default_value = .12
    white.inputs['Coat Weight'].default_value = .6
    white.inputs['Subsurface Weight'].default_value = .2; white.inputs['Subsurface Scale'].default_value = .004
    gold = nt.nodes.new('ShaderNodeBsdfPrincipled')
    gold.inputs['Base Color'].default_value = (1.0, .72, .32, 1); gold.inputs['Metallic'].default_value = 1; gold.inputs['Roughness'].default_value = .22
    mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(ramp.outputs['Color'], mix.inputs[0])
    nt.links.new(white.outputs[0], mix.inputs[1]); nt.links.new(gold.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    return m


def emission(name, color, strength):
    m, nt, out = node_mat(name)
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = (*color, 1); e.inputs['Strength'].default_value = strength
    nt.links.new(e.outputs[0], out.inputs[0])
    return m


def image_mat(name, path, scale=1.0, rough=0.8, bump=None, sheen=0.0, emit=0.0):
    m, nt, out = node_mat(name)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale, scale, scale)
    nt.links.new(tc.outputs['UV'], mp.inputs[0])
    im = nt.nodes.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(path)
    nt.links.new(mp.outputs[0], im.inputs[0])
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Roughness'].default_value = rough
    b.inputs['Sheen Weight'].default_value = sheen
    nt.links.new(im.outputs['Color'], b.inputs['Base Color'])
    if emit:
        nt.links.new(im.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = emit
    if bump:
        mp2 = nt.nodes.new('ShaderNodeMapping'); mp2.inputs['Scale'].default_value = (scale * 24,) * 3
        nt.links.new(tc.outputs['UV'], mp2.inputs[0])
        bi = nt.nodes.new('ShaderNodeTexImage'); bi.image = bpy.data.images.load(bump); bi.image.colorspace_settings.name = 'Non-Color'
        nt.links.new(mp2.outputs[0], bi.inputs[0])
        bn = nt.nodes.new('ShaderNodeBump'); bn.inputs['Strength'].default_value = 0.25; bn.inputs['Distance'].default_value = 0.0006
        nt.links.new(bi.outputs['Color'], bn.inputs['Height'])
        nt.links.new(bn.outputs[0], b.inputs['Normal'])
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


# ───────────────────────────── props ─────────────────────────────

# Armudu glass profile (radius, height) in metres: pear body, narrow waist, flared rim.
ARMUDU = [(0.0, 0.0), (0.020, 0.0), (0.022, 0.004), (0.0235, 0.012), (0.026, 0.025), (0.0262, 0.034),
          (0.024, 0.046), (0.0195, 0.060), (0.0185, 0.068), (0.020, 0.080), (0.0245, 0.093), (0.0275, 0.101)]


def armudu_glass(coll, glass_m, tea_m, fill=0.86):
    t = 0.0012
    outer = ARMUDU
    inner = [(max(0.0, r - t), z + (0.006 if i < 2 else 0)) for i, (r, z) in enumerate(outer)]
    prof = outer + [(outer[-1][0] - t * 0.5, outer[-1][1] + 0.0008)] + list(reversed(inner[2:])) + [(0.0, inner[2][1])]
    g = lathe('ArmuduGlass', prof, coll=coll, mat=glass_m)
    subsurf(g, 1)
    # tea: inner profile up to fill height, closed top
    top = ARMUDU[-1][1] * fill
    pts = [(0.0, 0.0065)]
    for r, z in inner[2:]:
        if z >= top:
            break
        pts.append((r - 0.0003, z))
    # interpolate radius at fill height
    for i in range(len(inner) - 1):
        (r0, z0), (r1, z1) = inner[i], inner[i + 1]
        if z0 <= top <= z1:
            rt = r0 + (r1 - r0) * (top - z0) / (z1 - z0) - 0.0003
    pts += [(rt, top), (0.0, top)]
    tea = lathe('Tea', pts, coll=coll, mat=tea_m)
    tea.location.z = 0.0
    return g, tea, top


def saucer(coll, mat):
    prof = [(0.0, 0.0), (0.035, 0.0), (0.040, 0.003), (0.045, 0.004), (0.060, 0.008), (0.066, 0.013),
            (0.068, 0.0135), (0.0665, 0.0145), (0.059, 0.0105), (0.044, 0.0065), (0.0, 0.0062)]
    return subsurf(lathe('Saucer', prof, coll=coll, mat=mat), 1)


def jam_dish(coll, glass_m, jam_m, cherry_m):
    prof = [(0.0, 0.0), (0.028, 0.0), (0.030, 0.004), (0.036, 0.008), (0.048, 0.030), (0.050, 0.034),
            (0.0485, 0.0345), (0.0465, 0.031), (0.034, 0.012), (0.0, 0.010)]
    dish = subsurf(lathe('JamDish', prof, coll=coll, mat=glass_m), 1)
    jam = lathe('Jam', [(0.0, 0.0102), (0.034, 0.0125), (0.044, 0.025), (0.0, 0.0255)], coll=coll, mat=jam_m)
    jam.parent = dish
    pos = [(0.012, 0.004), (-0.015, 0.010), (0.004, -0.018), (-0.02, -0.012), (0.024, -0.013), (-0.004, 0.024)]
    for i, (x, y) in enumerate(pos):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0068, location=(x, y, 0.0245), segments=24, ring_count=12)
        c = bpy.context.active_object; c.name = f'Cherry{i}'; c.scale.z = 0.85
        bpy.ops.object.shade_smooth(); c.data.materials.append(cherry_m)
        for cl in c.users_collection:
            cl.objects.unlink(c)
        coll.objects.link(c); c.parent = dish
    return dish


def half_cake(coll, plate_m, sponge_m, cream_m, berry_m):
    plate = subsurf(lathe('CakePlate', [(0.0, 0.0), (0.08, 0.0), (0.09, 0.004), (0.13, 0.010), (0.132, 0.012),
                                         (0.128, 0.0125), (0.09, 0.007), (0.0, 0.006)], coll=coll, mat=plate_m), 1)
    R = 0.105
    layers = [(0.007, 0.024, sponge_m, R), (0.024, 0.031, cream_m, R), (0.031, 0.048, sponge_m, R),
              (0.048, 0.055, cream_m, R), (0.055, 0.072, sponge_m, R), (0.072, 0.082, cream_m, R + 0.002)]
    parts = []
    for i, (z0, z1, m, r) in enumerate(layers):
        bm = bmesh.new()
        n = 48
        ring0, ring1 = [], []
        for k in range(n + 1):
            a = math.pi * k / n  # half disc
            ring0.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z0)))
            ring1.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z1)))
        for k in range(n):
            bm.faces.new((ring0[k], ring0[k + 1], ring1[k + 1], ring1[k]))
        bm.faces.new(list(reversed(ring0))); bm.faces.new(ring1)
        bm.faces.new((ring0[0], ring1[0], ring1[-1], ring0[-1]))  # cut face
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        o = mesh_obj(f'CakeLayer{i}', bm, coll, smooth=False, mat=m)
        bev = o.modifiers.new('Bevel', 'BEVEL'); bev.width = 0.002 if m != cream_m else 0.003; bev.segments = 3
        o.parent = plate
        parts.append(o)
    for i in range(7):
        a = math.pi * (0.1 + 0.8 * i / 6)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0085, location=(0.082 * math.cos(a), 0.082 * math.sin(a), 0.088))
        b = bpy.context.active_object; b.name = f'Berry{i}'; bpy.ops.object.shade_smooth()
        b.data.materials.append(berry_m)
        for cl in b.users_collection:
            cl.objects.unlink(b)
        coll.objects.link(b); b.parent = plate
    return plate


def sugar_bowl(coll, bowl_m, sugar_m):
    bowl = subsurf(lathe('SugarBowl', [(0.0, 0.0), (0.025, 0.0), (0.03, 0.006), (0.04, 0.025), (0.042, 0.03),
                                       (0.040, 0.031), (0.037, 0.026), (0.026, 0.009), (0.0, 0.008)], coll=coll, mat=bowl_m), 1)
    import random
    rnd = random.Random(3)
    for i in range(7):
        bpy.ops.mesh.primitive_cube_add(size=0.013, location=(rnd.uniform(-.018, .018), rnd.uniform(-.018, .018), 0.02 + 0.006 * (i // 4)),
                                        rotation=(rnd.uniform(-.4, .4), rnd.uniform(-.4, .4), rnd.uniform(0, 3)))
        c = bpy.context.active_object; c.name = f'Qand{i}'
        bev = c.modifiers.new('B', 'BEVEL'); bev.width = 0.0012; bev.segments = 2
        c.data.materials.append(sugar_m)
        for cl in c.users_collection:
            cl.objects.unlink(c)
        coll.objects.link(c); c.parent = bowl
    return bowl


def curve_tube(name, pts, radii, coll, mat, bevel_res=8):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = 1.0; cu.bevel_resolution = bevel_res; cu.use_fill_caps = True
    sp = cu.splines.new('POLY' if len(pts) < 3 else 'NURBS'); sp.points.add(len(pts) - 1)
    for p, (co, r) in zip(sp.points, zip(pts, radii)):
        p.co = (*co, 1); p.radius = r
    sp.use_endpoint_u = True; sp.order_u = min(4, len(pts))
    o = bpy.data.objects.new(name, cu); cu.materials.append(mat)
    return link(o, coll)


def teapot(coll, por_m):
    rig = bpy.data.objects.new('TeapotRig', None); link(rig, coll)
    body = subsurf(lathe('TeapotBody', [(0.0, 0.0), (0.045, 0.0), (0.05, 0.004), (0.066, 0.030), (0.070, 0.055),
                                         (0.062, 0.085), (0.042, 0.100), (0.036, 0.102), (0.0, 0.102)], coll=coll, mat=por_m), 1)
    lid = subsurf(lathe('TeapotLid', [(0.0, 0.0), (0.038, 0.0), (0.034, 0.010), (0.016, 0.020), (0.008, 0.022),
                                       (0.011, 0.030), (0.0, 0.033)], coll=coll, mat=por_m), 1)
    lid.location.z = 0.100
    # spout towards -X, handle +X (local)
    spout = curve_tube('TeapotSpout', [(-0.05, 0, 0.030), (-0.085, 0, 0.050), (-0.105, 0, 0.080), (-0.120, 0, 0.098)],
                       [0.018, 0.011, 0.008, 0.0065], coll, por_m)
    handle = curve_tube('TeapotHandle', [(0.060, 0, 0.080), (0.100, 0, 0.088), (0.108, 0, 0.050), (0.090, 0, 0.022), (0.064, 0, 0.022)],
                        [0.007, 0.007, 0.007, 0.007, 0.007], coll, por_m)
    for o in (body, lid, spout, handle):
        o.parent = rig
    return rig


# ───────────────────────────── hand (metaballs) ─────────────────────────────


def seg_element(mb, p0, p1, r):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    el = mb.elements.new(type='CAPSULE')
    el.co = (p0 + p1) / 2
    el.size_x = max(d.length / 2, 1e-4)
    el.rotation = Vector((1, 0, 0)).rotation_difference(d.normalized())
    el.radius = r
    el.stiffness = 2.0
    return el


def build_hand(name, coll, skin_m, curls, thumb, spread=0.0):
    """Right hand in local space: fingers +X, back of hand +Z, thumb +Y. Wrist at origin−X.
    curls: per finger (index..pinky) list of 3 joint angles (radians, toward palm).
    thumb: (yaw, pitch, curl)."""
    mb = bpy.data.metaballs.new(name)
    mb.resolution = 0.006; mb.render_resolution = 0.0022; mb.threshold = 0.6
    K = 1.55  # metaball radius → visible radius compensation
    # palm
    for y in (-0.018, 0.0, 0.018):
        seg_element(mb, (-0.035, y * 0.9, 0), (0.030, y, 0), 0.0135 * K)
    seg_element(mb, (-0.06, 0, -0.002), (-0.03, 0, 0), 0.022 * K)  # wrist
    seg_element(mb, (-0.20, 0, -0.004), (-0.06, 0, -0.002), 0.026 * K)  # forearm
    bases = [(0.032, 0.024), (0.036, 0.008), (0.033, -0.008), (0.028, -0.023)]
    lengths = [(0.042, 0.025, 0.021), (0.046, 0.028, 0.022), (0.043, 0.027, 0.021), (0.034, 0.021, 0.018)]
    radii = [(0.0092, 0.0084, 0.0076), (0.0095, 0.0086, 0.0078), (0.009, 0.0082, 0.0074), (0.008, 0.0072, 0.0066)]
    for f in range(4):
        p = Vector((bases[f][0], bases[f][1], 0.0))
        ang = 0.0
        yaw = (bases[f][1] / 0.024) * spread
        for j in range(3):
            ang += curls[f][j]
            d = Vector((math.cos(ang), 0, -math.sin(ang)))
            d.rotate(Quaternion((0, 0, 1), yaw))
            q = p + d * lengths[f][j]
            seg_element(mb, p, q, radii[f][j] * K)
            p = q
    # thumb from palm side near wrist
    yaw_t, pitch_t, curl_t = thumb
    p = Vector((-0.022, 0.022, -0.006))
    d = Vector((1, 0, 0))
    d.rotate(Quaternion((0, 0, 1), yaw_t)); d.rotate(Quaternion((1, 0, 0), -pitch_t))
    for j, (L, r) in enumerate([(0.040, 0.0125), (0.030, 0.0098), (0.026, 0.0088)]):
        q = p + d * L
        seg_element(mb, p, q, r * K)
        p = q
        axis = Vector((0, 0, 1)).cross(d).normalized() if j == 0 else axis
        d.rotate(Quaternion(Vector((0, 0, -1)), curl_t))
    o = bpy.data.objects.new(name, mb); mb.materials.append(skin_m)
    link(o, coll)
    return o


def sleeve(name, coll, mat, parent):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.036, depth=0.34, location=(-0.26, 0, -0.002), rotation=(0, math.pi / 2, 0), vertices=32)
    s = bpy.context.active_object; s.name = name
    for cl in s.users_collection:
        cl.objects.unlink(s)
    coll.objects.link(s)
    bev = s.modifiers.new('B', 'BEVEL'); bev.width = 0.01; bev.segments = 4
    bpy.ops.object.shade_smooth()
    s.data.materials.append(mat); s.parent = parent
    return s


def orient(obj, fingers_dir, back_dir, loc):
    x = Vector(fingers_dir).normalized()
    z = Vector(back_dir); z = (z - x * z.dot(x)).normalized()
    y = z.cross(x)
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = loc
    obj.matrix_world = m


# ───────────────────────────── relatives ─────────────────────────────


def relative(coll, name, loc, cloth, skin_m, hair_m, h=1.0, lean=0.0, scarf=None, arms=(0.0, 0.0)):
    """Seated figure, soft metaball silhouette (seen out of focus). Origin at table height."""
    rig = bpy.data.objects.new(name, None); link(rig, coll); rig.location = loc
    K = 1.5
    body = bpy.data.metaballs.new(name + 'Body'); body.resolution = 0.03; body.render_resolution = 0.012; body.threshold = 0.6
    seg_element(body, (0, 0.02, -0.15), (0, 0.0, 0.20 * h), 0.13 * K)                 # torso
    seg_element(body, (-0.16, 0.0, 0.24 * h), (0.16, 0.0, 0.24 * h), 0.065 * K)        # shoulders
    for sx, a in ((-1, arms[0]), (1, arms[1])):
        sh = (0.18 * sx, 0.0, 0.22 * h); el = (0.21 * sx, -0.10 - a * 0.05, 0.02 + a * 0.12)
        hd = (0.10 * sx, -0.26 - a * 0.04, 0.03 + a * 0.20)
        seg_element(body, sh, el, 0.048 * K); seg_element(body, el, hd, 0.038 * K)
    bo = bpy.data.objects.new(name + 'Body', body); body.materials.append(cloth); link(bo, coll); bo.parent = rig
    head = bpy.data.metaballs.new(name + 'Head'); head.resolution = 0.02; head.render_resolution = 0.008; head.threshold = 0.6
    seg_element(head, (0, 0, 0.26 * h), (0, 0, 0.33 * h), 0.042 * K)                  # neck
    e = head.elements.new(type='ELLIPSOID'); e.co = (0, 0, 0.42 * h); e.radius = 0.095 * K
    e.size_x, e.size_y, e.size_z = 0.82, 0.92, 1.08
    ho = bpy.data.objects.new(name + 'Head', head); head.materials.append(skin_m); link(ho, coll); ho.parent = rig
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(0, 0.02, 0.45 * h), segments=32, ring_count=16)
    hair = bpy.context.active_object; hair.name = name + 'Hair'
    hair.location = (0, 0.03, 0.46 * h); hair.scale = (1.1, 1.08, 1.0)
    if scarf:
        hair.location = (0, 0.04, 0.44 * h); hair.scale = (1.15, 1.05, 1.2)
    bpy.ops.object.shade_smooth(); hair.data.materials.append(scarf or hair_m)
    for cl in hair.users_collection:
        cl.objects.unlink(hair)
    coll.objects.link(hair); hair.parent = rig
    rig.rotation_euler.x = lean
    return rig


# ───────────────────────────── build ─────────────────────────────


def build():
    s = reset()
    props = collection('Props'); room = collection('Room'); people = collection('Relatives'); hands = collection('Hands')

    # materials
    M = dict(
        glass=glass_mat('Glass', (0.98, 0.98, 0.97), 1.5, 0.0, shadow_tint=(0.96, 0.95, 0.92)),
        tea=glass_mat('Tea', (0.95, 0.42, 0.12), 1.34, 0.0, shadow_tint=(1.0, 0.55, 0.18), absorb=((0.75, 0.18, 0.04), 28.0)),
        stream=glass_mat('Stream', (1.0, 0.55, 0.2), 1.33, 0.0, shadow_tint=(1, .6, .25), absorb=((0.85, 0.35, 0.08), 6.0)),
        jam=glass_mat('Jam', (0.75, 0.05, 0.06), 1.42, 0.03, shadow_tint=(0.8, 0.1, 0.08), absorb=((0.6, 0.02, 0.03), 60.0)),
        cherry=principled('Cherry', (0.32, 0.01, 0.03), rough=0.12, coat=1.0, sss=0.3, sss_r=(1, .1, .1)),
        porcelain=porcelain_gold('Porcelain', band=(0.90, 0.96)),
        saucer=porcelain_gold('SaucerGold', band=(0.62, 0.68), radial=True),
        plate=porcelain_gold('PlateGold', band=(0.63, 0.67), radial=True),
        sponge=principled('Sponge', (0.72, 0.46, 0.22), rough=0.85, sss=0.15),
        cream=principled('Cream', (0.92, 0.86, 0.74), rough=0.45, sss=0.4, sss_r=(1, .9, .7)),
        berry=principled('Berry', (0.45, 0.02, 0.05), rough=0.15, coat=1.0),
        sugar=principled('Sugar', (0.95, 0.94, 0.92), rough=0.6, sss=0.5),
        skin=principled('Skin', (0.62, 0.40, 0.29), rough=0.48, sss=0.25, sss_r=(1.0, 0.35, 0.2)),
        sleeve=principled('Sleeve', (0.018, 0.022, 0.04), rough=0.95, sheen=0.25),
        sleeve2=principled('Sleeve2', (0.12, 0.02, 0.04), rough=0.95, sheen=0.25),
        cloth=image_mat('Tablecloth', os.path.join(TEX, 'tablecloth.png'), scale=10.0, rough=0.75,
                        bump=os.path.join(TEX, 'weave.png'), sheen=0.5),
        carpet=image_mat('Carpet', os.path.join(TEX, 'carpet.png'), rough=0.9, sheen=0.4),
        wall=principled('Wall', (0.42, 0.28, 0.18), rough=0.9),
        bulb=emission('Bulb', (1.0, 0.72, 0.42), 30.0),
        shade=emission('LampShade', (1.0, 0.62, 0.30), 6.0),
        dusk=emission('Dusk', (0.18, 0.26, 0.55), 1.4),
        hair=principled('Hair', (0.03, 0.02, 0.02), rough=0.5),
        fruitO=principled('Orange', (0.9, 0.38, 0.05), rough=0.4), fruitG=principled('Apple', (0.45, 0.6, 0.1), rough=0.3),
    )
    clothes = [principled('C1', (0.22, 0.03, 0.06), 0.8, sheen=0.5), principled('C2', (0.06, 0.08, 0.14), 0.8, sheen=0.5),
               principled('C3', (0.08, 0.16, 0.12), 0.8, sheen=0.5), principled('C4', (0.30, 0.22, 0.15), 0.8, sheen=0.5),
               principled('C5', (0.35, 0.30, 0.26), 0.8, sheen=0.5)]
    scarf = principled('Scarf', (0.42, 0.30, 0.12), 0.7, sheen=0.6)
    scarf2 = principled('Scarf2', (0.12, 0.10, 0.10), 0.7, sheen=0.6)

    # table + cloth
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0.6, TABLE_Z))
    cloth = bpy.context.active_object; cloth.name = 'Tablecloth'; cloth.scale = (1.4, 2.6, 1)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.uv.smart_project() if False else None
    cloth.data.materials.append(M['cloth'])
    # UVs in metres so the pattern scale is physical
    uv = cloth.data.uv_layers[0] if cloth.data.uv_layers else cloth.data.uv_layers.new()
    for loop in cloth.data.loops:
        v = cloth.data.vertices[loop.vertex_index].co
        uv.data[loop.index].uv = (v.x / 2.0, v.y / 2.0)
    for cl in cloth.users_collection:
        cl.objects.unlink(cloth)
    room.objects.link(cloth)

    # room
    def plane(name, loc, rot, size, mat, coll=room):
        bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
        o = bpy.context.active_object; o.name = name; o.scale = (*size, 1); o.data.materials.append(mat)
        for cl in o.users_collection:
            cl.objects.unlink(o)
        coll.objects.link(o)
        return o
    plane('BackWall', (0, 3.4, 1.5), (math.pi / 2, 0, 0), (6, 3), M['wall'])
    plane('Carpet', (0.25, 3.38, 1.55), (math.pi / 2, 0, 0), (1.3, 1.95), M['carpet'])
    plane('LeftWall', (-1.8, 1.5, 1.5), (math.pi / 2, 0, math.pi / 2), (5, 3), M['wall'])
    plane('Window', (-1.78, 2.2, 1.55), (math.pi / 2, 0, math.pi / 2), (0.9, 1.2), M['dusk'])
    # chandelier bulbs and a floor lamp → warm bokeh
    for i, (x, y, z) in enumerate([(-0.25, 1.6, 2.05), (0.0, 1.75, 2.12), (0.25, 1.6, 2.05), (-0.12, 1.45, 2.0), (0.12, 1.85, 2.0), (0.0, 1.55, 1.95)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.025, location=(x, y, z))
        b = bpy.context.active_object; b.name = f'Bulb{i}'; b.data.materials.append(M['bulb'])
        for cl in b.users_collection:
            cl.objects.unlink(b)
        room.objects.link(b)
    bpy.ops.mesh.primitive_cone_add(radius1=0.22, radius2=0.14, depth=0.3, location=(1.15, 2.6, 1.45), vertices=48)
    sh = bpy.context.active_object; sh.name = 'FloorLampShade'; sh.data.materials.append(M['shade'])
    for cl in sh.users_collection:
        cl.objects.unlink(sh)
    room.objects.link(sh)

    # lights
    def area(name, loc, target, size, power, color):
        ld = bpy.data.lights.new(name, 'AREA'); ld.size = size; ld.energy = power; ld.color = color
        o = bpy.data.objects.new(name, ld); link(o, room); o.location = loc
        d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        return o
    gx, gy = GLASS_XY
    area('KeyBacklight', (gx + 0.12, gy + 0.55, TABLE_Z + 0.28), (gx, gy, TABLE_Z + 0.05), 0.30, 22, (1.0, 0.66, 0.36))
    area('Fill', (-0.5, -0.6, 1.6), (0, 0.1, TABLE_Z), 1.2, 9, (1.0, 0.82, 0.62))
    area('Chandelier', (0, 1.6, 2.0), (0, 1.3, 0.8), 0.8, 110, (1.0, 0.68, 0.38))
    area('WindowCool', (-1.6, 1.8, 1.5), (0, 1.5, 1.0), 1.0, 40, (0.55, 0.65, 1.0))
    area('Rim', (0.9, 0.8, 1.3), (gx, gy, TABLE_Z + 0.05), 0.4, 12, (1.0, 0.75, 0.5))
    w = bpy.data.worlds.new('World'); s.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = (0.03, 0.02, 0.015, 1)
    w.node_tree.nodes['Background'].inputs[1].default_value = 0.6

    # props: glass on saucer
    sa = saucer(props, M['saucer']); sa.location = (gx, gy, TABLE_Z)
    glass_rig = bpy.data.objects.new('GlassRig', None); link(glass_rig, props)
    glass_rig.location = (gx, gy, TABLE_Z + 0.0062)
    g, tea, tea_top = armudu_glass(props, M['glass'], M['tea'])
    g.parent = glass_rig; tea.parent = glass_rig
    focus = bpy.data.objects.new('FocusTarget', None); link(focus, props); focus.parent = glass_rig; focus.location = (0, 0, 0.06)

    jd = jam_dish(props, M['glass'], M['jam'], M['cherry']); jd.location = (gx - 0.16, gy + 0.05, TABLE_Z)
    ck = half_cake(props, M['plate'], M['sponge'], M['cream'], M['berry']); ck.location = (gx + 0.14, gy + 0.30, TABLE_Z)
    ck.rotation_euler.z = math.radians(-115)
    sb = sugar_bowl(props, M['glass'], M['sugar']); sb.location = (gx - 0.10, gy + 0.24, TABLE_Z)

    # background table life (blurred): more glasses, teapot, fruit
    import random
    rnd = random.Random(11)
    for i, (x, y) in enumerate([(-0.45, 0.95), (0.42, 1.05), (-0.15, 1.55), (0.22, 1.6), (-0.5, 1.7)]):
        sx = saucer(props, M['saucer']); sx.location = (x, y, TABLE_Z)
        gg, tt, _ = armudu_glass(props, M['glass'], M['tea'], fill=rnd.uniform(.5, .85))
        for o in (gg, tt):
            o.location = (x, y, TABLE_Z + 0.006)
    for i in range(9):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=(0.05 + rnd.uniform(-.09, .09), 1.2 + rnd.uniform(-.07, .07), TABLE_Z + 0.04 + 0.02 * (i // 5)))
        f = bpy.context.active_object; f.name = f'Fruit{i}'; bpy.ops.object.shade_smooth()
        f.data.materials.append(M['fruitO'] if i % 3 else M['fruitG'])
    bg_pot = teapot(props, M['porcelain']); bg_pot.location = (-0.32, 1.25, TABLE_Z)

    # relatives (soft, out of focus) — Xala leans in from the far left
    rel = [('Xala', (-0.36, 1.45, TABLE_Z), clothes[0], scarf, 1.0, -0.18, (0.0, 0.9)),
           ('Dayi', (0.40, 1.80, TABLE_Z), clothes[1], None, 1.1, 0.0, (0.0, 0.0)),
           ('Ana', (0.74, 1.05, TABLE_Z), clothes[3], None, 1.0, 0.05, (0.4, 0.0)),
           ('Bibi', (-0.82, 1.05, TABLE_Z), clothes[2], scarf2, 0.98, 0.04, (0.0, 0.0)),
           ('Baci', (0.0, 2.25, TABLE_Z), clothes[4], None, 1.0, 0.0, (0.0, 0.6))]
    for name, loc, cl, sc, h, lean, arms in rel:
        r = relative(people, name, loc, cl, M['skin'], M['hair'], h=h, lean=lean, scarf=sc, arms=arms)
        r.rotation_euler.z = math.atan2(loc[0], loc[1] - gy + 0.6) * 0.9

    # ── camera ──
    cam_d = bpy.data.cameras.new('Cam'); cam_d.lens = 30; cam_d.sensor_fit = 'VERTICAL'; cam_d.sensor_height = 36
    cam_d.dof.use_dof = True; cam_d.dof.aperture_fstop = 1.15; cam_d.dof.focus_object = focus
    cam = bpy.data.objects.new('Camera', cam_d); link(cam); s.camera = cam
    p0 = Vector((0.06, -0.56, 1.08))
    tgt = Vector((gx - 0.005, gy + 0.30, TABLE_Z + 0.05))
    cam.location = p0
    cam.rotation_euler = (tgt - p0).to_track_quat('-Z', 'Y').to_euler()
    push = (tgt - p0).normalized() * SC['camera_push']
    key(cam, 'location', 1, p0)
    for c in cam.animation_data.action.fcurves:
        for kp in c.keyframe_points:
            kp.interpolation = 'SINE'; kp.easing = 'EASE_IN_OUT'
    cam.keyframe_insert('rotation_euler', frame=1)

    # ── teapot pour (0 → pour_end), then exits ──
    pot = teapot(props, M['porcelain'])
    PS = 0.72
    pot.scale = (PS, PS, PS)
    rim_z = TABLE_Z + 0.0062 + ARMUDU[-1][1]
    tip_local = Vector((-0.122, 0, 0.098))
    spout_target = Vector((gx + 0.006, gy + 0.002, rim_z + 0.10))
    from mathutils import Euler

    def pot_pose(frame, tilt, lift=Vector((0, 0, 0))):
        rot = Euler((0, math.radians(tilt), math.radians(-10)))
        loc = spout_target - (rot.to_matrix() @ (tip_local * PS)) + lift
        key(pot, 'location', frame, loc); key(pot, 'rotation_euler', frame, rot)
    pot_pose(1, -36)
    pot_pose(F(SC['pour_end']) - 4, -35, Vector((0.002, 0, 0.003)))
    pot_pose(F(SC['pour_end']) + 6, -8, Vector((0.03, 0.0, 0.05)))
    pot_pose(F(SC['teapot_exit']), -4, Vector((0.26, 0.12, 0.30)))
    # pouring hand on the handle (leaves frame with the pot); a relative's hand from across the table
    ph = build_hand('PourHand', hands, M['skin'], curls=[(1.35, 1.3, 0.8)] * 4, thumb=(0.5, 0.1, 0.5))
    ph.parent = pot
    ph.matrix_parent_inverse = Matrix.Identity(4)
    orient(ph, (0.0, -1.0, -0.25), (1.0, 0.0, 0.4), Vector((0.125, 0.045, 0.055)))
    ph.scale = (1 / PS,) * 3
    sleeve('PourSleeve', hands, M['sleeve2'], ph)

    # tea stream: cylinder from spout tip down to tea surface, origin at bottom
    tea_surface_z = TABLE_Z + 0.0062 + tea_top
    bpy.ops.mesh.primitive_cylinder_add(radius=0.0021, depth=1.0, location=(0, 0, 0.5), vertices=16)
    st = bpy.context.active_object; st.name = 'TeaStream'
    bpy.ops.object.transform_apply(location=True)
    bpy.ops.object.shade_smooth()
    st.data.materials.append(M['stream'])
    st.location = (gx + 0.006, gy + 0.002, tea_surface_z - 0.004)
    length = spout_target.z - (tea_surface_z - 0.004) - 0.004
    key(st, 'scale', 1, (1, 1, length))
    key(st, 'scale', F(SC['pour_end']) - 5, (1, 1, length))
    key(st, 'scale', F(SC['pour_end']) - 1, (0.45, 0.45, length * 0.7))
    key(st, 'scale', F(SC['pour_end']) + 2, (0.2, 0.2, 0.0))
    # tea fill rises a touch while pouring
    key(tea, 'scale', 1, (1, 1, 0.965)); key(tea, 'scale', F(SC['pour_end']), (1, 1, 1.0))

    # ── lift: POV right hand pinches the rim, glass rises and freezes halfway ──
    lh = build_hand('LiftHand', hands, M['skin'], curls=[(1.05, 1.0, 0.55), (1.1, 1.0, 0.55), (1.35, 1.4, 0.8), (1.5, 1.4, 0.8)],
                    thumb=(0.85, 0.75, 0.35), spread=0.06)
    sleeve('LiftSleeve', hands, M['sleeve'], lh)
    grip = Vector((gx + 0.04, gy - 0.085, rim_z + 0.058))
    off = Vector((0.16, -0.26, -0.10))
    fdir, bdir = (-0.32, 0.90, 0.22), (0.15, -0.25, 1.0)

    def place_hand(frame, loc, f=fdir, b=bdir):
        orient(lh, f, b, loc)
        lh.keyframe_insert('location', frame=frame); lh.keyframe_insert('rotation_euler', frame=frame)
    place_hand(1, grip + off)
    place_hand(F(SC['hand_enter']), grip + off)
    place_hand(F(SC['hand_grip']) - 4, grip + Vector((0.01, -0.012, 0.012)))
    place_hand(F(SC['hand_grip']), grip)
    lift = Vector((-0.01, -0.025, SC['lift_height']))
    place_hand(F(SC['lift_start']), grip)
    place_hand(F(SC['lift_stop']), grip + lift)
    place_hand(F(SC['lift_stop']) + 3, grip + lift + Vector((0, 0, 0.002)))
    place_hand(s.frame_end, grip + lift + Vector((0, 0, 0.001)))
    key(glass_rig, 'location', F(SC['lift_start']), glass_rig.location.copy())
    key(glass_rig, 'location', F(SC['lift_stop']), glass_rig.location + lift)
    key(glass_rig, 'location', F(SC['lift_stop']) + 3, glass_rig.location + Vector((0, 0, 0.002)))
    key(glass_rig, 'location', s.frame_end, glass_rig.location + Vector((0, 0, -0.001)))
    key(glass_rig, 'rotation_euler', F(SC['lift_start']), (0, 0, 0))
    key(glass_rig, 'rotation_euler', F(SC['lift_stop']), (math.radians(-3), math.radians(2), 0))
    # sudden stop: ease-in from rest, hard stop at the top (no ease-out)
    for o in (lh, glass_rig):
        for c in o.animation_data.action.fcurves:
            for kp in c.keyframe_points:
                if abs(kp.co[0] - F(SC['lift_start'])) < 0.5:
                    kp.interpolation = 'SINE'; kp.easing = 'EASE_IN'
                if abs(kp.co[0] - F(SC['hand_enter'])) < 0.5:
                    kp.interpolation = 'SINE'; kp.easing = 'EASE_OUT'

    # ── render settings ──
    s.render.engine = 'CYCLES'
    cy = s.cycles
    cy.device = 'CPU'
    cy.samples = int(arg('--samples', 40, int)); cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.03
    cy.use_denoising = True; cy.denoiser = 'OPENIMAGEDENOISE'
    cy.max_bounces = 10; cy.diffuse_bounces = 2; cy.glossy_bounces = 4; cy.transmission_bounces = 10
    cy.transparent_max_bounces = 10; cy.caustics_reflective = False; cy.caustics_refractive = False
    cy.sample_clamp_indirect = 6.0; cy.blur_glossy = 1.0
    s.render.use_persistent_data = True
    res = float(arg('--res', 1.0, float))
    s.render.resolution_x = round(EP['width'] * res); s.render.resolution_y = round(EP['height'] * res)
    s.render.resolution_percentage = 100
    s.view_settings.view_transform = 'AgX'; s.view_settings.look = 'AgX - Punchy'
    s.view_settings.exposure = -0.35
    s.render.image_settings.file_format = 'PNG'; s.render.image_settings.color_mode = 'RGB'
    s.render.film_transparent = False
    return s


if __name__ == '__main__':
    s = build()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'ep01.blend'))
    out = arg('--out', os.path.join(ROOT, 'build', 'bg'))
    if arg('--still') not in (None, True):
        t = float(arg('--still'))
        s.frame_set(F(t))
        s.render.filepath = os.path.join(out, f'still_{t:05.2f}.png')
        bpy.ops.render.render(write_still=True)
    elif arg('--render'):
        s.frame_start = int(arg('--start', s.frame_start, int)); s.frame_end = int(arg('--end', s.frame_end, int))
        s.render.filepath = os.path.join(out, 'bg_')
        bpy.ops.render.render(animation=True)
