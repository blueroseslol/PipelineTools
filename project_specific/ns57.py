#Project Specific Functions
from .. import core
import pymel.core as pm
import logging

# Logging initialize

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# reload
core._reload()
ul = core.ul
ru = core.rul
rcl = core.rcl

#--- Utilities Function ---

def set_Vray_material(mat,mat_type='dielectric',**kwargs):
    '''set Material Attribute'''
    if type(mat) == pm.nt.VRayMtl:
        dielectric_setting = {
            'brdfType':1,
            'reflectionGlossiness':0.805,
            'reflectionColorAmount':1,
            'useFresnel':1,
            'lockFresnelIORToRefractionIOR':1,
            'bumpMapType':1,
            'bumpMult':2.2
        }
        metal_setting = {
            'brdfType':1,
            'reflectionGlossiness':0.743,
            'reflectionColorAmount':1,
            'useFresnel':0,
            'lockFresnelIORToRefractionIOR':1,
            'bumpMapType':1,
            'bumpMult':1.8
        }
        shader_type = {
            'metal':metal_setting,
            'dielectric':dielectric_setting
        }
        if shader_type.has_key(mat_type):
            for attr,value in shader_type[mat_type].items():
                mat.attr(attr).set(value)
    for key,value in kwargs.items():
        try:
            mat.attr(key).set(value)
        except (IOError, OSError, AttributeError) as why:
            print why

def get_character_infos():
    scene_name = pm.sceneName()
    while True:
        if scene_name == scene_name.parent:
            return
        scene_name = scene_name.parent
        if scene_name.parent.endswith('CH'):
            break
    ch_infos = scene_name.basename().split('_')
    return ch_infos

def add_suffix(ob, suff="_skinDeform"):
    pm.rename(ob, ob.name()+str(suff))

@ul.do_function_on()
def create_skinDeform(ob, bsName='BodyBS'):
    if not ob.name().endswith('skinDeform'):
        dupOb = ob.duplicate(name="_".join([ob.name(), "skinDeform"]))
        for child in dupOb[0].listRelatives(ad=True):
            add_suffix(child)
    try:
        pm.delete(bsName)
    except pm.MayaNodeError:
        pass
    finally:
        pm.blendShape(ob, dupOb, name=bsName)

@ul.do_function_on()
def create_renderMesh(ob, bsName='BodyBS'):
    if '_' in ul.get_name(ob):
        dupOb = ob.duplicate(name="_".join(ul.get_name(ob).split('_')[:-1]))
        for child in dupOb[0].listRelatives(ad=True):
            child.rename(name="_".join(ul.get_name(child).split('_')[:-1]))
        pm.reorder(dupOb[0], f=True)
    try:
        pm.delete(bsName)
    except pm.MayaNodeError:
        pass
    finally:
        pm.blendShape(ob, dupOb, name=bsName)

@ul.error_alert
def create_send_folder(version=1):
    ws = pm.workspace
    todayFolder = pm.date(f='YYMMDD')
    if version>1:
        todayFolder = "{}_{:02d}".format(todayFolder,int(version))
    ws.path.makedirs(ws.path.join([ws.path.replace('Works','%s/Works'%todayFolder),'scenes']))
    # ws.path.makedirs(ws.path.replace('Works','%s/Works'%todayFolder)+'sourceimages')

def basic_intergration():
    pm.PyNode('CH_ReferenceShape').visibility.set(False)
    root = pm.PyNode('ROOT')
    chref = pm.PyNode('CH_Ctrl_Reference')
    for atr in ['tx', 'ty', 'tz',
                'rx', 'ry', 'rz',
                'sx', 'sy', 'sz']:
        root.attr(atr).lock()
        root.attr(atr).set(cb=False, k=False)
        if atr.startswith('s'):
            chref.attr(atr).set(cb=False, k=False)
    temp = pm.circle(radius=100)
    temp[0].setRotation([-90,0,0])
    pm.makeIdentity(temp[0], apply=True)
    chref = pm.PyNode('CH_Ctrl_Reference')
    pm.parent(temp[0].getShape(), chref, r=True, s=True)
    pm.delete(chref.getShape(), shape=True)
    pm.delete(temp[0])
    chref.getShape().overrideEnabled.set(True)
    chref.getShape().overrideRGBColors.set(True)
    chref.getShape().overrideColorRGB.set([1,0,0])

    if chref.hasAttr('radius'):
        chref.radius.delete()
    chref.addAttr('radius',at='float',k=1)
    chRad=100
    if get_character_infos():
        assert get_character_infos()[0].isdigit(), 'Character ID is not number'
        chID = int(get_character_infos()[0])
        if 1 < chID <= 10:
            chRad = chID * 4
        elif chID <= 35:
            chRad = chID * 2 
        else:
            chRad = chID - 10
    chref.radius.set(chRad)
    chref.radius >> temp[1].radius

    if pm.objExists('facialGp'):
        for atr in ['FacialVis','FacialBS']:
            if not chref.hasAttr(atr):
                chref.addAttr(atr,at='bool',k=1)
        chref.FacialVis >> pm.PyNode('facialGp').visibility
        for bs in ['FacialBS','EyeDeformBS']:
            if pm.objExists(bs):
                chref.FacialBS >> pm.PyNode(bs).envelope

    if pm.objExists('secondaryGp'):
        for atr in ['SecondaryVis','SecondaryBS']:
            if not chref.hasAttr(atr):
                chref.addAttr(atr,at='bool',k=1)
        chref.SecondaryVis >> pm.PyNode('secondaryGp').visibility
        if pm.objExists('SecondaryBS'):
            chref.SecondaryBS >> pm.PyNode('SecondaryBS').envelope

    if pm.objExists('xgenGp'):
        for atr in ['XgenVis','XgenBS']:
            if not chref.hasAttr(atr):
                chref.addAttr(atr,at='bool',k=1)
        chref.XgenVis >> pm.PyNode('xgenGp').visibility
        if pm.objExists('XgenBS'):
            chref.XgenBS >> pm.PyNode('XgenBS').envelope


# def create_sway_short_hair(bone,rootTop):
#     bones = get_current_chain(bone)
#     bonename = bone.name().split('|')[-1]
#     startBone = bones[0]
#     endBone = bones[-1]
#     midBone = bones[int(round((len(bones)-1)/2.0))]
#     ikhandle, ikeffector, ikcurve = pm.ikHandle(
#         sj=startBone, ee=endBone,solver='ikSplineSolver')
#     ikhandle.rename(bonename+'_ikhandle')
#     ikeffector.rename(bonename+'_ikeffector')
#     ikcurve.rename(bonename+'_ikCurve')
#     sbonetop, mbonetop, ebonetop = [
#         dup_bone(b,name = b.name()+'_top') for b in [startBone,midBone,endBone]]
#     print (len(bones)-1)%2.0
#     if (len(bones)-1)%2.0 == 1:
#         boneUp = bones[int(math.ceil((len(bones)-1)/2.0))]
#         boneDown = bones[int(math.floor((len(bones)-1)/2.0))]
#         mbonetop.setTranslation(
#             (boneUp.getTranslation('world')+boneDown.getTranslation('world'))/2,'world')
#     for b in [sbonetop, mbonetop, ebonetop]:
#         b.setParent(None)
#         b.radius.set(b.radius.get()*2)
#     curveSkin = pm.skinCluster(sbonetop,mbonetop,ebonetop,ikcurve)
#     if not rootTop.hasAttr('swayspeedX'):
#         pm.addAttr(
#             rootTop,
#             ln='swayspeedX', nn='Sway X Speed', sn='swayspX',
#             at='float', k=1, dv=0.75)
#     if not rootTop.hasAttr('swaystrengthX'):
#         pm.addAttr(
#             rootTop,
#             ln='swaystrengthX', nn='Sway X Strength', sn='swaystrX',
#             at='float', k=1, dv=0.25)
#     if not rootTop.hasAttr('swayfrequencyX'):
#         pm.addAttr(rootTop,
#         ln='swayfrequencyX', nn='Sway X Frequency', sn='swayfreX',
#         at='float', k=1, dv=2)
#     if not rootTop.hasAttr('swayspeedY'):
#         pm.addAttr(rootTop,
#         ln='swayspeedY', nn='Sway Y Speed', sn='swayspY',
#         at='float', k=1, dv=1)
#     if not rootTop.hasAttr('swaystrengthY'):
#         pm.addAttr(rootTop,
#         ln='swaystrengthY', nn='Sway Y Strength', sn='swaystrY',
#         at='float', k=1, dv=0.5)
#     if not rootTop.hasAttr('swayfrequencyY'):
#         pm.addAttr(rootTop,
#         ln='swayfrequencyY', nn='Sway Y Frequency', sn='swayfreY',
#         at='float', k=1, dv=1)
#     pm.select(ikcurve,r=True)
#     X = pm.nonLinear( type='sine' )
#     X[1].rename(bonename+'_sineX')
#     pm.select(ikcurve,r=True)
#     Y = pm.nonLinear( type='sine' )
#     Y[1].rename(bonename+'_sineY')
#     #Z = pm.nonLinear(type='sine')
#     for sineHandle in [X,Y]:
#         sineHandle[0].lowBound.set(0)
#         sineHandle[0].amplitude.set(0.25)
#         sineHandle[0].dropoff.set(-1)
#         sineHandle[0].wavelength.set(1.5)
#         sineHandle[1].setTranslation(sbonetop.getTranslation('world'), 'world')
#         tempAim = pm.aimConstraint(
#             ebonetop,
#             sineHandle[1],
#             aimVector=[0,1,0],
#             )
#         sineHandle[1].setParent(sbonetop)
#         sineHandle[1].scaleY.set(
#             sbonetop.getTranslation().distanceTo(ebonetop.getTranslation()))
#         tempAim.worldUpType.set(1)
#         tempAim.setWorldUpObject(mbonetop.name())
#         if sineHandle == Y:
#             tempAim.setUpVector([1,0,0])
#         else:
#             tempAim.setUpVector([0,0,1])
#     sineExpress = pm.expression(
#         s='%s.offset=time*%s*noise(time);\n%s.offset=time*%s*noise(time);'%(
#             X[0].name(),rootTop.swayspX.name(),Y[0].name(),rootTop.swayspY.name()),
#         td=True, ae=1, uc='all')
#     rootTop.swaystrX >> X[0].amplitude
#     rootTop.swayfreX >> X[0].wavelength
#     rootTop.swaystrY >> Y[0].amplitude
#     rootTop.swayfreY >> Y[0].wavelength
#     return (sbonetop, mbonetop, ebonetop)
