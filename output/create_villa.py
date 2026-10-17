"""Headless procedural villa. blender -b -t 5 --python create_villa.py -- --stage draft|final"""
import bpy, math, random, os, sys, argparse
from mathutils import Vector
random.seed(27)
p=argparse.ArgumentParser(); p.add_argument('--stage',choices=['draft','final'],default='final'); args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
ROOT=os.path.dirname(os.path.abspath(__file__)); OUT=ROOT if os.path.basename(ROOT)=='output' else os.path.join(ROOT,'output'); os.makedirs(OUT,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
 if c.name!='Collection' and c.users==0: bpy.data.collections.remove(c)
COL={}
for n in ['Architecture','Roof and joinery','Glazing and screens','Interiors','Garden stonework','Planting','Lighting','Cameras']:
 c=bpy.data.collections.new(n); bpy.context.scene.collection.children.link(c); COL[n]=c
current='Architecture'
def put(o,name,mat=None):
 o.name=name
 for c in list(o.users_collection): c.objects.unlink(o)
 COL[current].objects.link(o)
 if mat:o.data.materials.append(mat)
 return o

def material(name,color,rough=.5,noise=0,bump=.08,scale=(1,1,1),metal=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 n=m.node_tree.nodes; l=m.node_tree.links; bs=n.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
 if noise:
  t=n.new('ShaderNodeTexNoise'); t.inputs['Scale'].default_value=noise; t.inputs['Detail'].default_value=3
  co=n.new('ShaderNodeTexCoord'); mapping=n.new('ShaderNodeVectorMath'); mapping.operation='MULTIPLY'; mapping.inputs[1].default_value=scale; l.new(co.outputs['Generated'],mapping.inputs[0]); l.new(mapping.outputs[0],t.inputs['Vector'])
  ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.18; ramp.color_ramp.elements[0].color=(*(x*.62 for x in color),1); ramp.color_ramp.elements[1].position=.83; ramp.color_ramp.elements[1].color=(*(min(x*1.22,1) for x in color),1); l.new(t.outputs['Fac'],ramp.inputs[0]); l.new(ramp.outputs[0],bs.inputs['Base Color'])
  b=n.new('ShaderNodeBump'); b.inputs['Strength'].default_value=bump; b.inputs['Distance'].default_value=.045; l.new(t.outputs['Fac'],b.inputs['Height']); l.new(b.outputs[0],bs.inputs['Normal'])
 return m
wood=material('Oiled Japanese cedar | longitudinal grain',(.17,.085,.035),.53,5,.19,(7,7,.13))
deck=material('Weathered hinoki decking',(.28,.19,.10),.65,5,.12,(.15,8,8))
plaster=material('Warm lime plaster',(.69,.65,.55),.86,130,.12)
stone=material('Honed grey basalt',(.10,.12,.11),.85,8,.3)
rockmat=material('Weathered garden granite',(.13,.15,.125),.92,7,.48)
roofmat=material('Patinated charcoal standing seam metal',(.065,.085,.078),.36,7,.08,metal=.65)
metal=material('Dark bronze frames',(.075,.057,.037),.3,metal=.65)
gravel=material('Warm fine granite gravel',(.25,.23,.18),.97,180,.7)
moss=material('Soft shaded moss',(.115,.18,.055),1,30,.4)
leafmats=[material('Maple foliage '+str(i),c,.76) for i,c in enumerate([(.14,.235,.07),(.21,.29,.09),(.29,.35,.11),(.09,.16,.045)])]
bark=material('Maple bark',(.19,.155,.10),.9,10,.4)
bamboo=material('Living bamboo culms',(.29,.34,.12),.58,8,.15,(7,7,.3))
fabric=material('Natural linen upholstery',(.70,.65,.53),.95,130,.16)
paper=material('Washi paper',(.79,.75,.62),.85,90,.08)
glass=material('Clear architectural glass',(.91,.97,.97),.08); glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=1
water=material('Basin water',(.12,.2,.19),.12); water.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.8

def cube(name,loc,dim,mat,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=put(bpy.context.object,name,mat); o.dimensions=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel: mod=o.modifiers.new('Soft crafted edges','BEVEL'); mod.width=bevel; mod.segments=2; o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o

def mesh(name,verts,faces,mat):
 me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new(name,me); COL[current].objects.link(o); o.data.materials.append(mat); return o

def beam(name,a,b,r,mat,vertices=10):
 a,b=Vector(a),Vector(b); d=b-a; bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d.length,location=(a+b)/2); o=put(bpy.context.object,name,mat); o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); return o

def ball(name,loc,dim,mat,sub=1):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=loc); o=put(bpy.context.object,name,mat); o.scale=dim; return o

def light(name,loc,energy,color,size,target):
 bpy.ops.object.light_add(type='AREA',location=loc); o=put(bpy.context.object,name); o.data.energy=energy; o.data.color=color; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler(); return o

# Human-scale architecture: front is negative Y.
cube('Raised basalt foundation',(0,4.2,.16),(12.4,9.4,.36),stone,.06)
cube('Interior floor',(0,4.3,.43),(12,8.8,.18),deck,.02)
cube('Left private wing rear wall',(-3.5,8.65,1.98),(5,.18,2.9),plaster,.015)
cube('Right living rear wall',(4.5,8.65,1.98),(3,.18,2.9),plaster,.015)
cube('Left side wall',(-6,4.5,1.98),(.16,8.3,2.9),plaster,.015)
cube('Rear courtyard wall',(1,8.65,1.98),(4,.18,2.9),plaster,.015)
# The courtyard is open beneath a roof aperture, surrounded by a timber gallery.
cube('Courtyard earth',(1,4.7,.53),(3.3,3.4,.1),gravel)
for x in [-1.05,3.05]:
 for y in [0,2.25,6.6,8.5]: cube('Exposed cedar column',(x,y,1.93),(.18,.18,2.9),wood,.012)
for x in [-5.9,-3.45,5.9]:
 for y in [0,4.3,8.5]:cube('Perimeter post',(x,y,1.93),(.16,.16,2.9),wood,.01)
for y in [0,2.25,6.6,8.5]:cube('Portal lintel',(1,y,3.22),(4.35,.22,.29),wood,.018)
for x in [-5.9,-1.05,3.05,5.9]:cube('Longitudinal roof beam',(x,4.2,3.31),(.2,8.8,.25),wood,.01)
# Front engawa with individually jointed deck boards.
for i in range(68):
 x=-6.12+i*.183
 cube('Engawa board %02d'%i,(x,-.47,.48),(.173,1.25,.12),deck,.006)
for i in range(23):
 y=.3+i*.36
 for x,w in [(-.83,.32),(2.83,.32)]:cube('Courtyard gallery board',(x,y,.54),(w,.35,.06),deck,.003)
for y,z,w in [(-1.18,.30,4.6),(-1.55,.12,5.2)]:cube('Floating entry stone step',(1,y,z),(w,.43,.16),stone,.025)
# Facade left: fine vertical cedar screen, with structural rails.
current='Glazing and screens'
for i in range(55):cube('Front cedar screen slat %02d'%i,(-5.95+i*.089,-.025,1.91),(.038,.105,2.78),wood,.004)
for z in [.57,1.75,3.26]:cube('Screen horizontal rail',(-3.55,.045,z),(4.95,.08,.065),wood,.006)
# Shoji private wing rear of screen.
for x in [-5.4,-4.2,-3,-1.8]:
 cube('Washi sliding panel',(x,1.22,1.93),(1.15,.045,2.62),paper,.005)
 for dx in [-.575,0,.575]:cube('Shoji stile',(x+dx,1.18,1.93),(.025,.045,2.65),wood)
 for z in [.63,1.06,1.49,1.92,2.35,2.78,3.22]:cube('Shoji lattice',(x,1.18,z),(1.17,.045,.022),wood)
# Glazed right wing, sliders open nearest entrance.
def window(name,a,b,z=1.93,h=2.68):
 mid=(Vector(a)+Vector(b))/2; length=(Vector(b)-Vector(a)).length; along=abs(a[1]-b[1])<.01
 dims=(length,.025,h) if along else (.025,length,h)
 cube(name+' glass',(mid.x,mid.y,z),dims,glass)
 for pt in [a,b]:cube(name+' bronze stile',(pt[0],pt[1],z),(.045,.045,h+.07),metal,.004)
 for zz in [z-h/2,z+h/2]:cube(name+' bronze rail',(mid.x,mid.y,zz),(length+.04,.055,.045) if along else (.055,length+.04,.045),metal,.003)
window('Living front pane',(4.45,.08),(5.9,.08))
for y in [0,2.1,4.2,6.3]:window('Garden side glazing',(5.91,y),(5.91,y+2.08))
for y in [2.3,4.45,6.6]:window('Courtyard living glazing',(3.09,y),(3.09,y+1.85))
window('Courtyard rear glass',(-.95,7.9),(2.95,7.9))
for x in [3.12,4.4,5.85]:cube('Recessed slider track',(x,-.02,.57),(.025,.18,.012),metal)
# Roof: closed shallow hip with a real courtyard opening.
current='Roof and joinery'
verts=[(-7.6,-1.65,3.55),(7.6,-1.65,3.55),(7.6,10.15,3.55),(-7.6,10.15,3.55),(-3.0,4.25,5.05),(3.0,4.25,5.05)]
roof=mesh('Continuous hipped roof with courtyard aperture',verts,[(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4)],roofmat)
sol=roof.modifiers.new('Roof construction depth','SOLIDIFY'); sol.thickness=.13
bpy.context.view_layer.objects.active=roof; roof.select_set(True); bpy.ops.object.modifier_apply(modifier=sol.name)
cut=cube('Temporary courtyard roof cutter',(1,4.5,4.7),(3.25,3.3,5),plaster)
mod=roof.modifiers.new('Open sky above garden court','BOOLEAN'); mod.operation='DIFFERENCE'; mod.object=cut
bpy.context.view_layer.objects.active=roof; bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(cut,do_unlink=True)
# Horizontal roof courses echo the sketch; trim around the court aperture.
for side in [0,1]:
 for i in range(24):
  t=i/24; y=(-1.65+5.9*t) if side==0 else (10.15-5.9*t); z=3.57+1.5*t; half=7.6-4.6*t
  ranges=[(-half,half)]
  if 2.85<y<6.15:ranges=[(-half,-.65),(2.65,half)]
  for a,b in ranges:
   if b>a:beam('Fine folded roof course',(a,y,z),(b,y,z),.013,roofmat,6)
for a,b in [(0,4),(1,5),(2,5),(3,4),(4,5)]:beam('Hip and ridge cap',verts[a],verts[b],.045,roofmat,8)
for a,b in [(0,1),(1,2),(2,3),(3,0)]:beam('Slim eave gutter',verts[a],verts[b],.065,roofmat,8)
# Visible undersides, fine cedar soffit slats around the projecting roof.
for i in range(104):
 x=-7.45+i*.144
 cube('Front overhang soffit board',(x,-.79,3.49),(.137,1.69,.045),deck,.003)
 cube('Rear overhang soffit board',(x,9.35,3.49),(.137,1.55,.045),deck,.003)
for x in [-6.75,6.75]:
 for i in range(66):cube('Side overhang soffit',(x,-.12+i*.144,3.49),(1.36,.137,.045),deck,.003)
for x in [-5.85,5.85]:beam('Rain chain',(x,-1.3,3.47),(x,-1.3,.22),.013,metal)
# Furnished spaces: low restrained furniture to establish scale.
current='Interiors'
cube('Living woven rug',(4.48,4.12,.55),(2.45,3.4,.025),fabric,.01)
cube('Low sofa timber platform',(4.95,4.5,.77),(1.25,2.7,.22),wood,.06)
for y in [3.65,4.5,5.35]:cube('Linen seat cushion',(4.85,y,.98),(1.1,.82,.24),fabric,.09)
cube('Sofa low upholstered back',(5.45,4.5,1.22),(.2,2.65,.65),fabric,.075)
cube('Low oak tea table',(3.86,4.2,.9),(.65,1.55,.08),wood,.03)
for y in [3.65,4.75]:cube('Tea table legs',(3.86,y,.72),(.47,.07,.32),wood,.012)
for y in [3.9,4.25]:
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.09,location=(3.85,y,1.0)); put(bpy.context.object,'Stoneware tea bowl',stone)
cube('Private room tatami base',(-3.6,4.9,.57),(3.9,4.2,.08),wood)
tatami=material('Rice straw tatami',(.43,.40,.25),.9,110,.16,(1,6,1))
for x in [-4.55,-2.65]:
 for y in [3.9,5.85]:cube('Tatami mat',(x,y,.63),(1.84,1.88,.055),tatami,.008)
cube('Low bed platform',(-3.65,6.4,.8),(2.8,2.0,.22),wood,.025)
cube('Linen futon',(-3.65,6.4,1.0),(2.6,1.87,.2),fabric,.08)
cube('Living back cabinet',(4.5,8.25,.98),(2.55,.55,.85),wood,.025)
for x in [3.6,4.2,4.8,5.4]:cube('Cabinet door shadow gap',(x,7.966,.99),(.012,.012,.67),metal)
# Courtyard and surrounding garden.
current='Garden stonework'
cube('Immediate garden base',(0,1.2,-.18),(26,25,.25),gravel,.16)
# Irregular polygon stepping stones, bevelled edges.
def paving(name,x,y,sx,sy,z=.04):
 n=random.randint(6,8); pts=[]
 for i in range(n):
  a=i*2*math.pi/n; r=random.uniform(.86,1.1);pts.append((x+math.cos(a)*sx*r,y+math.sin(a)*sy*r))
 vs=[(a,b,z-.08) for a,b in pts]+[(a,b,z+.035) for a,b in pts]
 fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 o=mesh(name,vs,fs,stone); mod=o.modifiers.new('Worn stone arris','BEVEL');mod.width=.025;mod.segments=2
 return o
for i in range(10):paving('Irregular approach stepping stone',4.7+math.sin(i*.5)*.7,-7.8+i*.69,.68,.47)
for i in range(6):paving('Entry stone path',3.9-i*.56,-2.2-i*.24,.58,.39)
for i in range(12):paving('Left garden stepping stone',-7.5,-6.7+i*.75,.65,.45)
def rock(name,loc,size):
 o=ball(name,loc,size,rockmat,3)
 for v in o.data.vertices:v.co*=1 + .075*math.sin(v.co.x*8+v.co.y*5) + .045*math.cos(v.co.z*11-v.co.x*3)
 for poly in o.data.polygons: poly.use_smooth=True
 bevel=o.modifiers.new('Weathered corners','BEVEL');bevel.width=.035;bevel.segments=2
 return o
for x,y,s in [(-4.9,-3.3,1.1),(-5.5,-5,.65),(-2.5,-5.8,.7),(2.7,-4.2,.85),(6.8,-1.9,.8),(7.4,2,.9),(-1.3,-3.1,.55),(.1,-2.8,.7),(1.5,4.65,.5),(.1,5.3,.38)]:
 rock('Garden granite boulder',(x,y,s*.38),(s,.7*s,.65*s))
 ball('Moss at boulder foot',(x+.15,y,.04),(s*1.15,s*.8,.08),moss,2)
# Basin carved with lathed solid profile and interior water.
def lathe(name,loc,profile,mat):
 vs=[];N=64
 for r,z in profile:
  for i in range(N):a=i*2*math.pi/N;vs.append((loc[0]+r*math.cos(a),loc[1]+r*math.sin(a),loc[2]+z))
 fs=[]
 for j in range(len(profile)-1):
  for i in range(N):a=j*N+i;b=j*N+(i+1)%N;fs.append((a,b,b+N,a+N))
 o=mesh(name,vs,fs,mat)
 for f in o.data.polygons:f.use_smooth=True
 return o
lathe('Carved granite tsukubai',(-1.7,-5,.02),[(0,0),(.42,0),(.56,.14),(.62,.5),(.57,.68),(.41,.68),(.36,.55),(.32,.2),(0,.2)],rockmat)
lathe('Still water in stone basin',(-1.7,-5,.02),[(0,.54),(.36,.54)],water)
beam('Bamboo basin spout',(-2.05,-4.65,.9),(-1.65,-4.95,.9),.035,bamboo)
beam('Bamboo spout support',(-2.05,-4.65,.1),(-2.05,-4.65,.93),.045,bamboo)
paving('Basin kneeling stone',-1.8,-6,.72,.44)
# Boundary timber fence.
for y in [i*.19-7 for i in range(90)]:cube('Garden boundary cedar batten',(-9.0,y,.99),(.065,.045,1.95),wood,.006)
for z in [.3,1.5]:cube('Boundary fence rail',(-9.04,1.5,z),(.08,17,.09),wood)
# Botanically articulated branches and individual leaf meshes, batched per tree.
current='Planting'
def leaves(name,clusters,matlist,count=32,leafsize=.14):
 vs=[];fs=[]
 for center,radius in clusters:
  for k in range(count):
   c=Vector(center)+Vector((random.uniform(-1,1)*radius,random.uniform(-1,1)*radius,random.uniform(-.4,.5)*radius)); a=random.uniform(0,math.tau); sz=leafsize*random.uniform(.7,1.4)
   u=Vector((math.cos(a),math.sin(a),random.uniform(-.45,.45)))*sz; v=Vector((-math.sin(a),math.cos(a),0))*sz*.5
   idx=len(vs); vs.extend([tuple(c-u),tuple(c-v),tuple(c+Vector((0,0,sz*.13))),tuple(c+u),tuple(c+v)]); fs.extend([(idx,idx+1,idx+2),(idx+1,idx+3,idx+2),(idx+3,idx+4,idx+2),(idx+4,idx,idx+2)])
 o=mesh(name,vs,fs,matlist[0])
 for m in matlist[1:]:o.data.materials.append(m)
 for f in o.data.polygons:f.material_index=random.randrange(len(matlist))
 return o

def tree(name,x,y,h):
 clusters=[];base=Vector((x,y,.1))
 for j in range(3):
  end=base+Vector((random.uniform(-.35,.35),random.uniform(-.3,.3),h*.63));beam(name+' trunk',base,end,.055 if h<4 else .09,bark)
  for k in range(7):
   a=k*math.tau/7+j*.8;tip=end+Vector((math.cos(a)*h*.32,math.sin(a)*h*.3,random.uniform(.1,.35)*h));beam(name+' branch',end,tip,.022,bark)
   for t in range(3):
    twig=tip+Vector((random.uniform(-.5,.5),random.uniform(-.5,.5),random.uniform(-.08,.35)));beam(name+' fine twig',tip,twig,.008,bark,6);clusters.append((twig,h*.13))
 leaves(name+' delicate canopy',clusters,leafmats,42,.105 if h<4 else .14)
tree('Courtyard Japanese maple',1.0,4.7,2.7)
tree('Left garden Japanese maple',-5.6,-2.7,4.7)
tree('Right garden maple',7.6,4.8,4.4)
# Bamboo group right foreground mirrors sketch.
clusters=[]
for i in range(17):
 x=3.45+random.uniform(-.45,.45);y=-3.25+random.uniform(-.4,.4);h=random.uniform(2.2,3.5);tip=(x+random.uniform(-.25,.25),y+random.uniform(-.2,.2),h)
 beam('Bamboo culm',(x,y,.05),tip,.025,bamboo,8)
 for j in range(1,int(h/.32)):
  z=j*.32;beam('Bamboo node',(x-.002,y,z),(x-.002,y,z+.022),.031,wood,8)
 for k in range(3):
  z=h*(.54+k*.16);end=(x+random.uniform(-.65,.65),y+random.uniform(-.4,.4),z+.2);beam('Bamboo twig',(x,y,z),end,.008,bamboo,6);clusters.append((end,.32))
leaves('Bamboo narrow foliage',clusters,leafmats[:2],18,.15)
# Ground ferns / grasses as slender tapered blades.
vs=[];fs=[]
for i in range(170):
 x=random.uniform(-8.5,8.5);y=random.uniform(-7,9)
 if -6.3<x<6.3 and -.9<y<9:continue
 if 3.8<x<6 and y<0:continue
 for j in range(9):
  a=random.uniform(0,math.tau);h=random.uniform(.14,.4);w=.018;root=Vector((x+random.uniform(-.08,.08),y+random.uniform(-.08,.08),.015)); tip=root+Vector((math.cos(a)*h*.55,math.sin(a)*h*.55,h));v=Vector((-math.sin(a)*w,math.cos(a)*w,0));idx=len(vs);vs.extend([tuple(root-v),tuple(root+v),tuple(tip)]);fs.append((idx,idx+1,idx+2))
mesh('Garden grasses',vs,fs,leafmats[1])
# Scattered small pebbles, shared mesh instances.
proto=ball('Pebble prototype',(0,0,-10),(1,1,1),stone,1)
for i in range(650):
 x=random.uniform(-8.8,8.8);y=random.uniform(-7.5,9)
 if -6.4<x<6.4 and -1<y<9:continue
 o=bpy.data.objects.new('Scattered gravel pebble',proto.data);COL[current].objects.link(o);o.location=(x,y,.015);s=random.uniform(.015,.045);o.scale=(s,s*.75,s*.5)
bpy.data.objects.remove(proto,do_unlink=True)
# Matte foliage avoids waxy highlights in strong daylight.
for m in leafmats:
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.92;bs.inputs['Specular IOR Level'].default_value=.15
# Photographic lighting.
current='Lighting'
world=bpy.data.worlds.new('Soft daylight sky');bpy.context.scene.world=world;world.use_nodes=True
nodes=world.node_tree.nodes;sky=nodes.new('ShaderNodeTexSky');sky.sky_type='NISHITA';sky.sun_elevation=math.radians(35);sky.sun_rotation=math.radians(135);sky.altitude=.1;sky.air_density=1.1;world.node_tree.links.new(sky.outputs[0],nodes.get('Background').inputs[0]);nodes.get('Background').inputs[1].default_value=.3
light('Large soft garden daylight',(-7,-7,11),1800,(1,.89,.72),7,(0,2,0))
for x,y in [(4.7,3),(-3.5,3),(1,7.3)]:light('Warm sheltered ceiling light',(x,y,3.08),95,(1,.69,.40),1.8,(x,y,.5))
# Visible linear light strips beneath shelter.
emit=material('Warm concealed LED',(.85,.57,.23),.4);bs=emit.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(1,.62,.27,1);bs.inputs['Emission Strength'].default_value=2
for x in [-1.05,3.05]:cube('Concealed gallery light',(x,4.25,3.16),(.018,8.15,.018),emit)
current='Cameras'
def camera(name,loc,target,lens):
 bpy.ops.object.camera_add(location=loc);o=put(bpy.context.object,name);o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o.data.clip_end=200;return o
front=camera('01 | Sketch comparison',(.45,-18.2,3.65),(0,2.4,2.3),35)
hero=camera('02 | Garden perspective',(13.2,-18.0,7.2),(0,2.3,1.7),40)
court=camera('03 | Courtyard threshold',(1,-3.8,1.9),(1,5.2,1.75),25)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='METERS';scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.use_denoising=False;scene.cycles.samples=32 if args.stage=='draft' else 128;scene.cycles.max_bounces=8;scene.cycles.transparent_max_bounces=8
scene.render.resolution_x=1152 if args.stage=='draft' else 1800;scene.render.resolution_y=768 if args.stage=='draft' else 1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.85
scene.camera=front
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_perspective='CAMERA'
   area.spaces.active.shading.color_type='MATERIAL'
for filename in ['create_villa.py','MODELING_PLAN.md']:
 bpy.data.texts.load(os.path.join(ROOT,filename)).use_fake_user=True
# Source sketch included in the native file for review.
ref=bpy.data.images.load(os.path.join(ROOT,'japanese villa.jpg'));ref.pack();ref.use_fake_user=True
scene['design_notes']='Primary reference: packed japanese villa.jpg. Assumed 12 x 9 m villa; meters. Central open-sky garden court; no distant landscape.'
scene['render_notes']='CPU Cycles. Denoising disabled: system build lacks OpenImageDenoise.'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'japanese_contemporary_villa.blend'))
views=[(front,'progress_front')] if args.stage=='draft' else [(front,'final_front'),(hero,'final_garden'),(court,'final_courtyard')]
for cam,name in views:
 scene.camera=cam;scene.render.filepath=os.path.join(OUT,name+'.png');bpy.ops.render.render(write_still=True)
scene.camera=front;scene.render.filepath=os.path.join(OUT,'final_front.png');bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'japanese_contemporary_villa.blend'))
print('VILLA_COMPLETE',args.stage,len(bpy.data.objects))
