"""3D cartoon renderer requiring Blender 4.x/5.x. PNG sequence output."""
import bpy,argparse,json,sys,math
from mathutils import Vector
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--story',required=True);p.add_argument('--output',required=True)
p.add_argument('--resolution',type=int,default=360);p.add_argument('--fps',type=int,default=12)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
story=json.loads(Path(a.story).read_text(encoding='utf-8'))
out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
available={x.identifier for x in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items}
scene.render.engine=next((e for e in ['BLENDER_EEVEE_NEXT','BLENDER_EEVEE','BLENDER_WORKBENCH'] if e in available),next(iter(available)))
scene.render.resolution_x=a.resolution*16//9;scene.render.resolution_y=a.resolution
scene.render.resolution_percentage=100;scene.render.fps=a.fps
scene.render.image_settings.file_format='PNG'
def material(name,rgb):
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF')
 if bs:bs.inputs['Base Color'].default_value=(*rgb,1)
 return m
grass=material('Grass',(.23,.65,.26));wood=material('Wood',(.43,.23,.11))
leaf=material('Leaf',(.11,.48,.19));skin=material('Skin',(.79,.45,.27))
shirt=material('Shirt',(.05,.48,.63));pants=material('Pants',(.1,.14,.35))
white=material('White',(1,1,1));black=material('Black',(.03,.03,.05))
mouth=material('Mouth',(.36,.03,.08))
def sphere(name,xyz,scale,mat,parent=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,location=xyz)
 ob=bpy.context.object;ob.name=name;ob.scale=scale;ob.data.materials.append(mat)
 if parent: ob.parent=parent;ob.matrix_parent_inverse=parent.matrix_world.inverted()
 return ob
def cube(name,xyz,scale,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz)
 ob=bpy.context.object;ob.name=name;ob.dimensions=scale;ob.data.materials.append(mat);return ob
cube('Ground',(0,0,-.2),(80,80,.4),grass)
for x,y in [(-5,4),(2,6),(7,5)]:
 cube('Tree trunk',(x,y,1.3),(.5,.5,2.6),wood)
 sphere('Tree leaves',(x,y,3.1),(1.4,1.2,1.4),leaf)
bpy.ops.object.empty_add(type='PLAIN_AXES');rig=bpy.context.object;rig.name='CartoonHero';rig.location=(-2,0,0)
sphere('Body',(0,0,1.45),(.47,.32,.73),shirt,rig)
sphere('Head',(0,-.08,2.53),(.58,.5,.58),skin,rig)
for sign in [-1,1]:
 sphere('Eye',(sign*.23,-.5,2.64),(.15,.08,.18),white,rig)
 sphere('Pupil',(sign*.23,-.57,2.63),(.07,.05,.10),black,rig)
 sphere('Arm',(sign*.61,0,1.48),(.15,.17,.52),skin,rig)
 sphere('Leg',(sign*.23,0,.52),(.18,.21,.53),pants,rig)
sphere('Nose',(0,-.55,2.47),(.12,.14,.13),skin,rig)
lips=sphere('Mouth',(0,-.55,2.26),(.17,.06,.06),mouth,rig)
bpy.ops.object.camera_add(location=(0,-11,4.4))
cam=bpy.context.object;direction=Vector((0,0,1.5))-cam.location
cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=7.5;scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(-3,-5,7))
bpy.context.object.data.energy=1300;bpy.context.object.data.size=5
f=0
for index,shot in enumerate(story['scenes']):
 n=round(float(shot.get('seconds',3))*a.fps)
 action=shot.get('action','talk')
 for k in range(n):
  f+=1;t=k/max(1,n-1)
  rig.location.x=(-2+4*t) if action=='walk' else (1 if index else -2)
  rig.location.z=math.sin(math.pi*t)*1.1 if action=='jump' else (abs(math.sin(k*.3))*.06 if action=='walk' else 0)
  rig.rotation_euler.z=math.sin(k*.14)*.06
  lips.scale.z=.06+(.13*abs(math.sin(k*.55)) if action=='talk' else 0)
  scene.frame_set(f);scene.render.filepath=str(out/f'{f:06d}.png')
  bpy.ops.render.render(write_still=True)
print('RENDER_DONE 3D',f)
