import pymel.core as pm
from PipelineTools.utilities import *
####Function Definition
def rebuildControl(ob, obshape='circle', ra=1):
    '''rebuild Hair Tube Control to specific type'''
    if not type(ob) == pm.nodetypes.Transform:
        return
    obOldShape = ob.getShape()
    shapeType = {
        'circle':(3, 8),
        'triangle':(1, 3),
        'square':(1, 4)}
    obNewShape = pm.circle(c=(0, 0, 0),
                           nr=(0, 1, 0),
                           sw=360, r=ra,
                           d=shapeType[obshape][0],
                           ut=0, tol=5.77201e-008,
                           s=shapeType[obshape][1],
                           ch=1,
                           name="HairProfileCurve#")
    for a in [('overrideEnabled', 1), ('overrideRGBColors', 1), ('overrideColorRGB', (0.2, 0.5, 0.2))]:
        obNewShape[0].getShape().attr(a[0]).set(a[1])
    pm.parent(obNewShape[0].getShape(), ob, r=1, s=1)
    pm.delete(obOldShape)
    pm.delete(obNewShape)

def createPointParent(ob, name="PointParent#", shapeReplace=False, r=1):
    '''Create a Parent of selected'''
    obOldParent = ob.getParent()
    obNewParent = pm.polySphere(name=name, subdivisionsAxis=6, subdivisionsHeight=4, radius=r/3)
    for a in [('castsShadows', 0),
              ('receiveShadows', 0),
              ('smoothShading', 0),
              ('primaryVisibility', 0),
              ('visibleInReflections', 0),
              ('visibleInRefractions', 0),
              ('overrideEnabled', 1),
              ('overrideShading', 0),
              ('overrideTexturing', 0),
              ('overrideRGBColors', 1),
              ('overrideColorRGB', (1, 0, 0))]:
        obNewParent[0].getShape().attr(a[0]).set(a[1])
    if not shapeReplace:
        pm.xform(obNewParent[0], ws=1, t=pm.xform(ob, q=1, ws=1, t=1))
        pm.xform(obNewParent[0], ws=1, ro=pm.xform(ob, q=1, ws=1, ro=1))
        #pm.color(obNewParent[0],rgb=(1,0,0))
        #obNewParent.setAttr("translate",obPos)
        if obOldParent:
            pm.parent(obNewParent[0], obOldParent)
        pm.parent(ob, obNewParent[0])
    else:
        pm.parent(obNewParent[0].listsRelatives(shapes=1)[0], ob, r=1, s=1)
        pm.delete(obNewParent)
def createHairMesh(profilesList,
                   name="hairMesh#",
                   cSet="hairCrease",
                   mat="",
                   lengthDivs=7,
                   widthDivs=4):
    '''create a Hair Tube with auto crease and material from list of Curve Profiles'''
    print profilesList
    if not profilesList or all(
            [type(o.getShape()) != pm.nodetypes.NurbsCurve for o in profilesList]):
        print "no Profiles"
        return
    pm.select(profilesList)
    pm.nurbsToPolygonsPref(pt=1, un=4, vn=7, f=2, ut=2, vt=2)
    HairMesh = pm.loft(n=name, po=1, ch=1, u=1, c=0, ar=1, d=3, ss=1, rn=0, rsn=True)
    ###
    #lock all Transform
    lockTransform(HairMesh[0])
    #custom Attribute add
    HairMesh[0].addAttr('lengthDivisions', min=1, at='long', dv=lengthDivs)
    HairMesh[0].addAttr('widthDivisions', min=4, at='long', dv=widthDivs)
    HairMesh[0].setAttr('lengthDivisions', e=1, k=1)
    HairMesh[0].setAttr('widthDivisions', e=1, k=1)
    HairTess = pm.listConnections(HairMesh)[-1]
    HairMesh[0].connectAttr('widthDivisions', HairTess+".uNumber")
    HairMesh[0].connectAttr('lengthDivisions', HairTess+".vNumber")
    HairMeshShape = HairMesh[0].getShape()
    ###
    #set Crease
    pm.select(HairMeshShape.e[0, 2], r=1)
    pm.runtime.SelectEdgeLoopSp()
    sideEdges = pm.selected()
    if bool(pm.ls(cSet, type=pm.nodetypes.CreaseSet)):
        hsSet = pm.ls(cSet, type=pm.nodetypes.CreaseSet)[0]
    else:
        hsSet = pm.nodetypes.CreaseSet(name=cSet)
        hsSet.setAttr('creaseLevel', 2.0)
    for e in sideEdges:
        pm.sets(hsSet, forceElement=e)
    #assign Texture
    HairUV = HairMeshShape.map
    pm.polyEditUV(HairUV, pu=0.5, pv=0.5, su=0.3, sv=1)
    pm.polyEditUV(HairUV, u=rand.uniform(-0.1, 0.1))
    ###
    #Add Vray OpenSubdiv
    pm.select(HairMesh[0], r=1)
    addVrayOpenSubdivAttr()
    ###
    #set Smoothness
    pm.displaySmoothness(po=3)
    ###
    #set Material
    if bool(pm.ls(mat, type=pm.nodetypes.ShadingEngine)):
        pm.sets(pm.ls(mat)[0], forceElement=HairMesh[0])
    return HairMesh

def makeHairMesh(name="HairMesh#",
                 mat="",
                 cSet="hairCrease",
                 reverse=False,
                 lengthDivs=7,
                 widthDivs=4,
                 Segments=4,
                 width=1,
                 curveDel=False,
                 cShape='triangle'):
    '''Create a Hair Tube From Select Curve line or Edge or IsoPram'''
    sel = pm.selected()
    if not sel:
        print "Select some Curves or Edges or isopram"
        return
    if type(sel[0]) == pm.general.MeshEdge:
        pm.runtime.CreateCurveFromPoly()
        pathTransform = pm.selected()[0]
    elif type(sel[0]) == pm.general.NurbsSurfaceIsoparm:
        pm.runtime.DuplicateCurve()
        pathTransform = pm.selected()[0]
    pathTransform = [t for t in pm.selected() if type(t) == pm.nodetypes.Transform]
    pm.select(pathTransform, r=1)
    pathShape = pm.listRelatives(shapes=True)
    if type(pathShape[0]) == pm.nodetypes.NurbsCurve:
        minscale = [0.001, 0.001, 0.001]
        pathCurve = [(i, pathShape[pathTransform.index(i)]) for i in pathTransform]
        if pm.objExists("HairBaseProfileCurve"):
            profileCurve = pm.ls("HairBaseProfileCurve")[0]
            #print profileCurve.listRelatives()[0].listConnections()[0]
            profileCurve.listRelatives()[0].listConnections()[0].setRadius(width)
            pm.showHidden(profileCurve, a=1)
        else:
            shapeType = {
                'circle':(3, 8),
                'triangle':(1, 3),
                'square':(1, 4)}
            profileCurve = pm.circle(c=(0, 0, 0),
                                     nr=(0, 1, 0),
                                     sw=360,
                                     r=width,
                                     d=shapeType[cShape][0],
                                     ut=0,
                                     tol=5.77201e-008,
                                     s=shapeType[cShape][1],
                                     ch=1,
                                     name="HairBaseProfileCurve")
            for a in [('overrideEnabled', 1),
                      ('overrideRGBColors', 1),
                      ('overrideColorRGB', (0.2, 0.5, 0.2))]:
                profileCurve[0].getShape().attr(a[0]).set(a[1])
        pm.select(d=1)
        for crv in pathCurve:
            print crv
            pm.rebuildCurve(crv[0], kep=1)
            if reverse:
                pm.reverseCurve(crv[0])
            #profileInstance = instance(profileCurve,n="pCrv_instance"+string(pathCurve.index(crv)))
            if pm.objExists("HairCtrlGroup"):
                hairOncsGroup = pm.ls("HairCtrlGroup")[0]
            else:
                hairOncsGroup = pm.group(name="HairCtrlGroup")
            #pm.parent(hairOncGroup,crv[0])
            mPath = pm.pathAnimation(profileCurve,
                                     crv[0], fa='y',
                                     ua='x',
                                     stu=1,
                                     etu=Segments*10,
                                     b=1)
            HairProfile = []
            hairOncGroup = pm.group(name="HairCtrls#")
            pm.parent(hairOncGroup, hairOncsGroup, r=1)
            for u in range(Segments+1):
                pm.currentTime(u*10)
                profileInstance = pm.duplicate(profileCurve,
                                               n=(crv[0]+"HairProFileCrv_"+str(u)),
                                               rr=1)[0]
                pm.parent(profileInstance, hairOncGroup, r=1)
                HairProfile.append(profileInstance)
                if u == 0 or u == Segments:
                    pm.scale(profileInstance, minscale, a=1, os=1)
            HairMesh = createHairMesh(
                HairProfile,
                name=name,
                cSet=cSet,
                mat=mat,
                lengthDivs=lengthDivs,
                widthDivs=widthDivs)
            pm.rename(hairOncGroup, hairOncGroup.name()+HairMesh[0].name())
            pm.delete(profileCurve, mp=1)
            pm.delete(profileCurve)
            pm.xform(
                hairOncsGroup,
                ws=1,
                piv=pm.xform(
                    hairOncsGroup.getChildren()[-1],
                    q=1, ws=1, piv=1)[:3])
        if curveDel:
            pm.delete(pathTransform, hi=1)

def selHair(
        selectTip=False,
        selectRoot=False,
        selectAll=False,
        pivot=0,
        setPivot=True,
        returnInfo=False,
        rebuild=[False, 7, 4], cShape=(False, 'circle', 1)):
    '''Select Hair Controls'''
    sel = pm.selected()
    if not sel:
        return
    ### check for right Selection
    hairMeshes = []
    for o in sel:
        #print o.getParent() == pm.ls('HairCtrlGroup')[0]
        if (type(o.getShape()) == pm.nodetypes.NurbsCurve or
                o.getParent() == pm.ls('HairCtrlGroup')[0]):
            try:
                if o.getParent() == pm.ls('HairCtrlGroup')[0]:
                    o = o.listRelatives(type=pm.nodetypes.Transform)[0]
                hairLoft = o.getShape().listConnections(type=pm.nodetypes.Loft)[0]
                hairTes = hairLoft.listConnections(type=pm.nodetypes.NurbsTessellate)[0]
                hair = hairTes.listConnections(type=pm.nodetypes.Transform)[0]
            except:
                continue
        elif (type(o.getShape()) == pm.nodetypes.Mesh and
              o.listConnections(type=pm.nodetypes.NurbsTessellate)):
            hair = o
            hairTes = o.listConnections(type=pm.nodetypes.NurbsTessellate)[0]
            hairLoft = hairTes.listConnections(type=pm.nodetypes.Loft)[0]
            print hair, hairTes, hairLoft
        else:
            continue
        if all([hair, hairTes, hairLoft]):
            hairMeshes.append((hair, hairTes, hairLoft))
        else:
            print "Something wrong with getting hair Tesselate and Loft"
            return
    if hairMeshes:
        #print hairMeshes
        ### getting all Controls
        Cgroups = []
        for hair in hairMeshes:
            try:
                #print hair
                hairLoft = hair[2]
                ctrls = [c for c in hairLoft.listConnections() if type(c) == pm.nt.Transform]
                ControlGroup = ctrls[0].getParent()
                #print ControlGroup
                if setPivot:
                    pm.xform(
                        ControlGroup,
                        ws=1,
                        piv=pm.xform(
                            ControlGroup.listRelatives(type=pm.nodetypes.Transform)[pivot],
                            q=1, ws=1, piv=1)[:3])
                if rebuild[0]:
                    NewControls = ControlGroup.listRelatives(type=pm.nodetypes.Transform)
                    print NewControls
                    if cShape[0]:
                        for c in NewControls:
                            rebuildControl(c, obshape=cShape[1], ra=cShape[2])
                    oldname = hair[0].name()
                    oldParent = hair[0].getParent()
                    curMaterial = hair[0].getShape().listConnections(
                        type=pm.nodetypes.ShadingEngine)[0].name()
                    pm.rename(hair[0], '_'.join([oldname, 'old']))
                    newHair = createHairMesh(
                        NewControls,
                        name=oldname,
                        mat=curMaterial,
                        lengthDivs=rebuild[1], widthDivs=rebuild[2])
                    pm.parent(newHair[0], oldParent)
                    #print hair[0]
                    #print hair[0].getShape().listConnections(type=pm.nt.PolyTweakUV)[0].listConnections(type=pm.nt.PolyNormal)
                    if hair[0].getShape().listConnections(
                        type=pm.nt.PolyTweakUV)[0].listConnections(
                            type=pm.nt.PolyNormal):
                        try:
                            pm.polyNormal(newHair[0], nm=3)
                        except:
                            print "can't reverse"
                    pm.delete(hair[0])
                    del hair
                    hair = newHair[0]
            except:
                continue
            if ControlGroup:
                #print ControlGroup
                Cgroups.append((hair, ControlGroup))
        ### select as Requested
        if Cgroups:
            #print Cgroups
            if not returnInfo:
                pm.select(d=1)
                for cGroup in Cgroups:
                    #print cGroup[1]
                    for c in cGroup[1].listRelatives(type=pm.nt.Transform):
                        c.show()
                    if selectTip:
                        hairTipsList = cGroup[1].listRelatives(type=pm.nt.Transform)[-1]
                        pm.select(hairTipsList, add=1)
                    elif selectRoot:
                        hairRootsList = cGroup[1].listRelatives(type=pm.nt.Transform)[0]
                        pm.select(hairRootsList, add=1)
                    elif selectAll:
                        pm.select(cGroup[1].listRelatives(type=pm.nt.Transform), add=1)
                    else:
                        pm.select(cGroup[1], add=1)
            else:
                return Cgroups

def splitHairCtrl(d='up'):
    '''add Hair Controls'''
    sel = pm.selected()
    if not sel:
        return
    directionDict = {
        'up':1,
        'down':-1}
    if not directionDict.has_key(d):
        return
    hairInfoAll = selHair(returnInfo=True)
    if not hairInfoAll:
        return
    #print hairInfo[0][0]
    #print hairInfo
    for selOb in sel:
        pm.select(selOb, r=1)
        hairInfo = hairInfoAll[sel.index(selOb)]
        ctrls = hairInfo[1].listRelatives(type=pm.nt.Transform)
        hair = hairInfo[0][0]
        for ctrl in ctrls:
            pm.rename(ctrl, '_'.join([ctrl.name(), "old"]))
        ctrlID = ctrls.index(selOb)
        if ctrlID == 0:
            directionDict[d] = 1
        elif ctrlID == (len(ctrls)-1):
            directionDict[d] = -1
        newCtrl = pm.duplicate(ctrls[ctrlID])[0]
        pm.move(
            newCtrl,
            (ctrls[ctrlID].getTranslation(space='world') +
             ctrls[ctrlID+directionDict[d]].getTranslation(space='world'))/2,
            a=1, ws=1)
        pm.scale(
            newCtrl,
            (ctrls[ctrlID].attr('scale').get() +
             ctrls[ctrlID+directionDict[d]].attr('scale').get())/2,
            a=1)
        ctrls.insert(ctrlID+(directionDict[d]+1)/2, newCtrl)
        for ctrl in ctrls:
            pm.rename(
                ctrl,
                '_'.join([ctrl.name().split('_')[0],
                          str(ctrls.index(ctrl)+1)]))
            pm.parent(ctrl, w=1)
            pm.parent(ctrl, hairInfo[1])
        oldname = hair.name()
        oldParent = hair.getParent()
        curMaterial = hair.getShape().listConnections(
            type=pm.nodetypes.ShadingEngine)[0].name()
        pm.rename(hair, '_'.join([oldname, 'old']))
        newHair = createHairMesh(
            ctrls,
            name=oldname,
            mat=curMaterial,
            lengthDivs=hair.attr('lengthDivisions').get(),
            widthDivs=hair.attr('widthDivisions').get())
        pm.parent(newHair[0], oldParent)
        pm.delete(hair)
        pm.select(newCtrl)
        pm.setToolTo('moveSuperContext')

def dupHairMesh(mirror=False,axis='x',space='world'):
    '''duplicate a HairTube'''
    hairInfoAll = selHair(returnInfo=True)
    if not hairInfoAll:
        return
    Cgroups = []
    for hair in hairInfoAll:
        pm.select(hair[0][0], hair[1])
        ctrls = hair[1].listRelatives(type=pm.nt.Transform)
        pm.duplicate(ic=1, un=1)
        if mirror:
            #mirrorTransform(hair[1])
            pm.polyNormal(hair[0][0], nm=3)
            oldPos = hair[1].getTranslation(space='world')
            print oldPos
            if not hair[1].isVisible():
                c.show()
            for c in ctrls:
                if not c.isVisible():
                    c.show()
                if space == 'world': 
                    pm.parent(c,w=1)
                    mirrorTransform(c,axis=axis)
                    pm.parent(c,hair[1])
                else:
                    mirrorTransform(c,axis=axis)
                #c.hide()
            #hair[1].hide()
        pm.select(hair[0][0], r=1)
        randU()
        selHair(setPivot=True)
        if mirror and space != 'world':
            hair[1].setTranslation(oldPos,space='world')
        Cgroups.append(hair[1])
    pm.select(Cgroups, r=1)

def delHair(dType='all', keepHair=False):
    ''' delete Hair with Controls or Control only'''
    sel = pm.selected()
    newAttr = ['lengthDivisions', 'widthDivisions']
    hairInfoAll = selHair(returnInfo=True)
    if not hairInfoAll:
        return
    Cgroups = [h[1] for h in hairInfoAll]
    hairMeshes = [h[0][0] for h in hairInfoAll]
    if not keepHair:
        pm.delete(hairMeshes)
        pm.delete(Cgroups)
    else:
        if dType == 'all':
            for hair in hairMeshes:
                pm.select(hair, r=1)
                selHair(setPivot=True)
                pm.xform(hair,
                         ws=1,
                         piv=pm.xform(Cgroups[hairMeshes.index(hair)],
                                      q=1, ws=1, piv=1)[:3])
                pm.delete(hair, ch=True)
                lockTransform(hair,lock=False)
                for a in newAttr:
                    if pm.attributeQuery(a, exists=1, node=hair):
                        pm.deleteAttr(hair+"."+a)
            pm.delete(Cgroups)
        elif dType == 'self' or dType == 'above' or dType == 'below':
            for ob in sel:
                ctrls = Cgroups[sel.index(ob)].listRelatives(type=pm.nt.Transform)
                if ctrls.count(ob):
                    if dType == 'self' or ctrls.index(ob) == 0 or ctrls.index(ob) == (len(ctrls)-1):
                        if ctrls.index(ob) == 0:
                            pm.scale(ctrls[1], [0.001, 0.001, 0.001], a=1)
                        elif ctrls.index(ob) == (len(ctrls)-1):
                            pm.scale(ctrls[-2], [0.001, 0.001, 0.001], a=1)
                        pm.delete(ob)
                    elif dType == 'above':
                        pm.delete(ctrls[ctrls.index(ob)+1:])
                        pm.scale(ctrls[ctrls.index(ob)], [0.001, 0.001, 0.001], a=1)
                    elif dType == 'below':
                        pm.delete(ctrls[:ctrls.index(ob)])
                        pm.scale(ctrls[ctrls.index(ob)], [0.001, 0.001, 0.001], a=1)
            for hair in hairMeshes:
                pm.select(hair)
                selHair(rebuild=[True,
                                 hair.attr('lengthDivisions').get(),
                                 hair.attr('widthDivisions').get()])

def cleanHairMesh():
    ''' remove All Hair Control in scene'''
    allMesh = pm.ls(g=1)
    allMeshTransform = [m.getParent() for m in allMesh]
    pm.select(allMeshTransform, r=1)
    delHair(keepHair=True)
    pm.select(d=1)
    if pm.objExists("HairCtrlGroup"):
        pm.delete("HairCtrlGroup", hi='below')
    if pm.objExists("HairBaseProfileCurve"):
        pm. delete("HairBaseProfileCurve")

def ToggleHairCtrlVis(state='switch'):
    hairCtrlsGroup = pm.ls('HairCtrlGroup')[0]
    if not hairCtrlsGroup:
        return
    if state == 'switch':
        pass
    elif state == 'show':
        pm.showHidden(hairCtrlsGroup, below=True)
    elif state == 'hide':
        pm.hide([ctrl.getChildren() for ctrl in hairCtrlsGroup.getChildren()])

def pickWalkHairCtrl(d='right', add=False):
    '''Pick Walk and hide Controls'''
    sel = pm.selected()
    hairInfoAll = selHair(returnInfo=True)
    if not hairInfoAll:
        return
    ToggleHairCtrlVis(state='hide')
    if d == 'up':
        pm.select([h[0][0] for h in hairInfoAll])
        selHair()
        for o in pm.selected():
            o.show()
    elif d == 'down':
        pm.select([h[0][0] for h in hairInfoAll])
        selHair(selectTip=True)
        for o in pm.selected():
            o.show()
    else:
        ctrlGroups = [h[1] for h in hairInfoAll]
        for ob in sel:
            ctrls = ctrlGroups[sel.index(ob)].listRelatives(type=pm.nt.Transform)
            if ctrls.count(ob):
                for c in ctrls:
                    c.show()
                pm.select(ob, add=1)
            else:
                selHair(selectTip=True)
                for c in ctrls:
                    c.show()
        pm.pickWalk(d=d)
