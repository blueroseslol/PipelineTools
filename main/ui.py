#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
written by Nguyen Phi Hung 2017
email: josephkirk.art@gmail.com
All code written by me unless specify
"""
from __future__ import with_statement

import maya.cmds as cm
import maya.mel as mm
from pymel.core import *
import types
from .. import core
from ..project_specific import ns57

# core._reload()
ul = core.ul
ru = core.rul
rcl = core.rcl
# Global Var
# Function
def batch_export_cam():
    '''Export all Baked Cam to Fbx Files'''
    Filters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
    getFiles = fileDialog2(cap="Select Files", fileFilter=Filters, fm=4)
    if getFiles:
        mm.eval("paneLayout -e -m false $gMainPane")
        for f in getFiles:
            cm.file(
                f,
                open=True,
                loadSettings="Load no references",
                loadReferenceDepth='none',
                prompt=False, f=True)
            ul.export_cameras_to_fbx()
        cm.file(f=True, new=True)
        mm.eval("paneLayout -e -m true $gMainPane")

# UI Class
class RigTools(object):
    def __init__(self):
        self._name = 'Rig Tools'
        self._windowname = self._name.replace(' ','')+'Window'
        self.nodebase = []
        self.nodetrack = NodeTracker()
        self.fullbasetrack = []
        self.fullcreatedtrack = []
        self.ControlObClass = rcl.ControlObject()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, newname):
        self._name = newname
        self._windowname = self._name.replace(' ','')+'Window'

    @property
    def window(self):
        if window(self._windowname, exists=True):
            deleteUI(self._windowname)
            windowPref(self._windowname, remove=True)
        self._window = window(
            self._windowname, title=self._name,
            rtf=True)
        self._windowSize = (250, 10)
        self._uiElement = {}
        return self._window

    @window.setter
    def window(self,newSize):
        self._windowSize = newSize

    def reset_window_height(self):
        #self._window.setSizeable(True)
        self._window.setHeight(10)

    @property
    def template(self):
        self._uiTemplate = uiTemplate(self._windowname.replace('Window', 'UITemplate'), force=True)
        self._uiTemplate.define(
            button, width=5, height=30, align='left')
        self._uiTemplate.define(
            columnLayout, adjustableColumn=1, w=10)
        self._uiTemplate.define(
            frameLayout, borderVisible=True,
            collapsable=True, cc=Callback(self.reset_window_height), cl=True,
            labelVisible=True, width=self._windowSize[0])
        self._uiTemplate.define(
            rowColumnLayout,
            rs=[(1, 5), ],
            adj=True, numberOfColumns=2,
            cal=[(1, 'left'), ],
            columnWidth=[(1, 60), (2, 120)])
        return self._uiTemplate

    def get_hair_system(self):
        hairSystem = ls(type='hairSystem')
        if hairSystem:
            self._uiElement['Hair System'].setText(hairSystem[-1].getParent().name())
            select(hairSystem[-1])

    def _delete_tracknode(self):
        scriptJob(ka=True)
        self.nodetrack.endTrack()
        del self.nodetrack

    def _ui_update(self):
        self.nodetrack.reset()
        #self.nodetrack.startTrack()
        print self.nodetrack.getNodes()

    def do_func(self, func, **kws):
        for kw,value in kws.items():
            if isinstance(value,types.MethodType):
                kws[kw] = value()
        self.nodebase = []
        for i in selected():
            self.nodebase.append(i)
            self.nodebase.extend(i.listRelatives(type='transform',ad=True))
        self.nodetrack.reset()
        self.nodetrack.startTrack()
        #self.ControlObClass.createControl()'
        sel=selected()
        if hasattr(self.ControlObClass, '_uiName'):
            if window(self.ControlObClass._uiName + 'Window', ex=True):
                kws['customShape'] = self.ControlObClass.createControl
        select(sel)
        func(**kws)
        # delete(kws['customShape'])
        self.nodetrack.endTrack()
        self.fullbasetrack.extend(self.nodebase)
        self.fullcreatedtrack.extend(self.nodetrack.getNodes())
        
    def delete_created_nodes(self , all=False):
        if all:
            self.nodebase = self.fullbasetrack
            trackNodes = self.fullcreatedtrack
        else:
            trackNodes = self.nodetrack.getNodes()
        if trackNodes:
            try:
                for node in trackNodes:
                    print node
                    if objExists(node):
                        condition = any([c in self.nodebase for c in node.listRelatives(type='transform',ad=True)]) if hasattr(node,'listRelatives') else False
                        if condition:
                            continue
                        if hasattr(node,'listRelatives'):
                            for c in node.listRelatives(type='transform',ad=True):
                                if c in trackNodes:
                                    trackNodes.remove(c)
                        delete(node)
                for node in self.nodebase:
                    if not node.getParent():
                        continue
                    if node.getParent() in self.nodebase:
                        continue
                    if 'offset' in node.getParent().name().lower():
                        ru.remove_parent(node)
            except (MayaNodeError,TypeError) as why:
                warning(why)

    def defineUI(self,*args,**kws):
        self.template.define(*args, **kws)

    def create_rig_util_ui(self):
        with columnLayout(adjustableColumn=False):
            with frameLayout(label='Tools:',cl=False):
                with columnLayout():
                    with rowColumnLayout(rs=[(1,1),], numberOfColumns=1):
                        button(
                            label='Bone & Skin Tools',
                            c=Callback(SkinWeightSetter.show))

            with frameLayout(label='Create Control:',cl=False):
                with columnLayout():
                    center_text = ul.partial(text, align='center')
                    button(
                        label='Create Control Shape',
                        c=Callback(self.ControlObClass._showUI))
                    separator()
                    with frameLayout(
                            label='Options:',
                            collapsable=False,
                            borderVisible=False):
                        with rowColumnLayout( rs=[(1,1),], numberOfColumns=2):
                            text(label='Connect using Loc: ', align='right')
                            self._uiElement['useLoc'] = checkBox(label='')
                    separator()
                    center_text(label='Create Single Bone Control:')
                    with rowColumnLayout( rs=[(1,1),], numberOfColumns=2):
                        button(
                            label='Prop Control',
                            c=Callback(
                                self.do_func,
                                ru.create_prop_control,
                                useLoc=self._uiElement['useLoc'].getValue,
                                sl=True))
                        button(
                            label='Free Control',
                            c=Callback(
                                self.do_func,
                                ru.create_free_control,
                                useLoc=self._uiElement['useLoc'].getValue,
                                sl=True))
                    separator()
                    center_text(label='Create Bone Chain Controls:')
                    with rowColumnLayout(rs=[(1,1),], numberOfColumns=2):
                        button(
                            label='Parent Control',
                            c=Callback(
                                self.do_func,
                                ru.create_parent_control,
                                useLoc=self._uiElement['useLoc'].getValue,
                                sl=True))
                        button(
                            label='Aim Setup',
                            c=Callback(
                                self.do_func,
                                ru.aim_setup,
                                sl=True))
                    separator()
                    center_text(label='Create Long Hair Control:')
                    with rowColumnLayout(
                            rs=[(1,1),],
                            numberOfColumns=2,
                            columnWidth=[(1, 150), (2, 50)]):
                        self._uiElement['Hair System'] = textFieldGrp(
                            cl2=('right', 'right'),
                            co2=(80, 10),
                            cw2=(70, 110),
                            label='Hair System:', text='%s_hairSystem'%ns57.get_character_infos()[-1])
                        button(
                            label='Get',
                            h=20,
                            c=Callback(self.get_hair_system))
                    button(
                        label='Create',
                        c=Callback(
                            self.do_func,
                            ru.create_long_hair,
                            hairSystem=self._uiElement['Hair System'].getText,
                            sl=True))
                    separator()
                    center_text(label='Create Short Hair Control:')
                    with rowColumnLayout(
                            rs=[(1,1),],
                            numberOfColumns=2,
                            columnWidth=[(1, 150), (2, 50)]):
                        self._uiElement['SHctlparent'] = textFieldGrp(
                            cl2=('right', 'right'),
                            co2=(80, 10),
                            cw2=(70, 110),
                            label='Parent :', text='')
                        button(
                            label='Get',
                            h=20,
                            c=lambda x: \
                                self._uiElement['SHctlparent'].setText(
                                    selected()[-1].name()))
                    with rowColumnLayout(
                            rs=[(1,1),],
                            numberOfColumns=3,
                            columnWidth=[(1, 50),(2,30),(3,140)]):
                        text(label='Mid Controls:')
                        self._uiElement['SHctlcount'] = intField(
                            value=0, min=0)
                        button(
                            label='create',
                            c=Callback(
                                self.do_func,
                                ru.create_short_hair,
                                parent=self._uiElement['SHctlparent'].getText,
                                midCtls=self._uiElement['SHctlcount'].getValue,
                                sl=True))
                    separator()
                    button(
                        label='Delete Created Nodes',
                        c=Callback(
                            self.delete_created_nodes))
                    with popupMenu(b=3):
                        menuItem(
                            label='Delete All Created Nodes',
                            c=Callback(
                                self.delete_created_nodes,
                                all=True))

            with frameLayout(label='Control Tag:'):
                with rowColumnLayout(rs=[(1,0),]):
                    button(
                        label='Tag as controller',
                        c=Callback(
                            ru.control_tagging,
                            sl=True))
                    button(
                        label='Remove tag',
                        c=Callback(
                            ru.control_tagging,
                            remove=True,
                            sl=True))
                    button(
                        label='Select all controllers',
                        c=Callback(
                            ru.remove_all_control_tags,
                            select=True))
                    with popupMenu(b=3):
                        menuItem(
                            label='Select controller meta',
                            c=Callback(
                                ru.select_controller_metanode))
                    button(
                        label='Remove all tag',
                        c=Callback(
                            ru.remove_all_control_tags))
                button(
                        label='Reset all controllers transform',
                        c=Callback(
                            ru.reset_controller_transform))

            with frameLayout(label='Utilities:'):
                with rowColumnLayout(rs=[(1,0),]):
                    smallbutton = ul.partial(button,h=30)
                    smallbutton(
                        label='create Parent',
                        c=Callback(
                            ru.create_parent,
                            sl=True))
                    smallbutton(
                        label='delete Parent',
                        c=Callback(
                            ru.remove_parent,
                            sl=True))
                    smallbutton(
                        label='Parent Shape',
                        c=Callback(
                            ul.parent_shape,
                            sl=True))
                    smallbutton(
                        label='create Offset bone',
                        c=Callback(
                            ru.create_offset_bone,
                            sl=True))
                    smallbutton(
                        label='create Loc',
                        c=Callback(
                            ru.create_loc_control,
                            connect=False,sl=True))
                    smallbutton(
                        label='create Loc control',
                        c=Callback(
                            ru.create_loc_control,
                            all=True,
                            sl=True))
                    smallbutton(
                        label='connect with Loc',
                        c=Callback(
                            ru.connect_with_loc,
                            all=True,
                            sl=True))
                    with popupMenu(b=3):
                        menuItem(label='translate only', c=Callback(
                            ru.connect_with_loc,
                            translate=True,
                            sl=True))
                        menuItem(label='rotate only', c=Callback(
                            ru.connect_with_loc,
                            rotate=True,
                            sl=True))
                    smallbutton(
                        label='vertex to Loc',
                        c=Callback(
                            ru.create_loc_on_vert,
                            sl=True))
                    smallbutton(
                        label='Connect Transform',
                        c=Callback(
                            ru.connect_transform,
                            all=True,
                            sl=True))
                    with popupMenu(b=3):
                        menuItem(
                            label='Connect Translate',
                            c=Callback(
                                ru.connect_transform,
                                translate=True, rotate=False, scale=False,
                                sl=True))
                        menuItem(
                            label='Connect Rotate',
                            c=Callback(
                                ru.connect_transform,
                                translate=False, rotate=True, scale=False,
                                sl=True))
                        menuItem(
                            label='Connect Scale',
                            c=Callback(
                                ru.connect_transform,
                                translate=False, rotate=False, scale=True,
                                sl=True))
                    smallbutton(
                        label='Disconnect Transform',
                        c=Callback(
                            ru.disconnect_transform,
                            sl=True))
                    with popupMenu(b=3):
                        menuItem(
                            label='Disconnect Translate',
                            c=Callback(
                                ru.disconnect_transform,
                                attr='translate',
                                sl=True))
                        menuItem(
                            label='Disconnect Rotate',
                            c=Callback(
                                ru.disconnect_transform,
                                attr='rotate',
                                sl=True))
                        menuItem(
                            label='Disconnect Scale',
                            c=Callback(
                                ru.disconnect_transform,
                                attr='scale',
                                sl=True))
                smallbutton(
                    label='multi Parent Constraint',
                    c=Callback(
                        ru.contraint_multi,
                        constraintType='Parent',
                        sl=True))
                with popupMenu(b=3):
                    menuItem(
                        label='multi Point Constraint', c=Callback(
                            ru.contraint_multi,
                            constraintType='Point',
                            sl=True))
                    menuItem(
                        label='multi Orient Constraint', c=Callback(
                            ru.contraint_multi,
                            constraintType='Orient',
                            sl=True))
                    menuItem(
                        label='multi Point&Orient Constraint', c=Callback(
                            ru.contraint_multi,
                            constraintType='PointOrient',
                            sl=True))
                    menuItem(
                        label='multi Aim Constraint', c=Callback(
                            ru.contraint_multi,
                            constraintType='Aim',
                            sl=True))
                    menuItem(
                        label='multi Loc Point Constraint', c=Callback(
                            ru.contraint_multi,
                            constraintType='LocP',
                            sl=True))
                    menuItem(
                        label='multi Loc Orient Constraint', c=Callback(
                            ru.contraint_multi,
                            constraintType='LocO',
                            sl=True))
                    menuItem(
                        label='multi Loc Point&Orient Constraint', c=Callback(
                            ru.contraint_multi,
                            constraintType='LocOP',
                            sl=True))

            with frameLayout(label='Intergration:'):
                button(
                    label='Basic Intergration',
                    c=Callback(ns57.basic_intergration))
                with rowColumnLayout():
                    self._uiElement['visAtrName'] = textFieldGrp(
                        cl2=('left', 'right'),
                        co2=(0, 0),
                        cw2=(40, 100),
                        label='Vis Attribute Name:', text='FullRigVis')
                    smallbutton(
                        label='Connect Visibility', c=lambda x:ru.connect_visibility(
                            attrname= self._uiElement['visAtrName'].getText(), sl=True))
                with rowColumnLayout():
                    button(label='Channel History OFF', c=Callback(ru.toggleChannelHistory, False))
                    with popupMenu(b=3):
                        menuItem(label='Channel History ON', c=Callback(ru.toggleChannelHistory))
                    button(label='Deform Normal Off', c=Callback(ru.deform_normal_off))

    def _init_ui(self):
        with self.window:
            with self.template:
                self.create_rig_util_ui()
        self.nodetrack.startTrack()
        #self.ui_update()

    @classmethod
    def show(cls):
        cls()._init_ui()

class SendCurrentFile(object):
    def __init__(self):
        self._name = 'SendCurrentFileUI'
        self._title = 'Send Current File Window'
        self._set()

    def __call__(self):
        return self.window

    def __str__(self):
        return self._name

    def __repr__(self):
        return self._name

    def name(self):
        return self._name

    def window(self):
        if window(self._name, ex=True):
            deleteUI(self._name)
        self._window = window(self._name, title=self._title, rtf=True, width=10, height=10, sizeable=False)
        return self._window

    def info(self):
        print 'self:', self
        print '__str__:', self.__str__()
        print '__repr__:', self.__repr__()
        print 'window:', self.window(), type(self.window())
        print 'name:', self.name()
        if window(self.name(), ex=True):
            print self.name(), 'exists'

    def _set(self):
        self.window()
        self.template = uiTemplate('SendCurrentFileUITemplate', force=True)
        self.template.define(button, width=100, height=40, align='left')
        self.template.define(frameLayout, borderVisible=False, labelVisible=True)
        self.template.define(rowColumnLayout, numberOfColumns=3, columnWidth=[(1, 90), (2, 90), (3, 90)])
        self.elements = {}
        # self.window().closeCommand(self.window().delete)

    def get_state(self):
        pass

    def set_state(self, state):
        pass

    def restore(self):
        pass

    def save_state(self):
        pass

    def show(self):
        scene_name = sceneName()
        with self.window():
            with self.template:
                with frameLayout(label='Sending {}'.format(scene_name.dirname())):
                    with columnLayout(adjustableColumn=1):
                        with frameLayout(label='Scene Options'):
                            with rowColumnLayout():
                                self.elements['scene'] = checkBox(label='scene', value=True)
                                self.elements['lastest'] = checkBox(label='Get lastest', value=True)
                                self.elements['render'] = checkBox(label='render', value=True)
                        with frameLayout(label='SourceImages Options'):
                            with rowColumnLayout():
                                self.elements['tex'] = checkBox(label='tex', value=True)
                                self.elements['extras'] = {}
                                for label in ['psd',
                                              'zbr',
                                              'uv',
                                              'pattern']:
                                    self.elements['extras'][label] = checkBox(label=label, value=False)
                                self.elements['extras']['psd'].setValue(True)
                        with frameLayout(label='"to" folder number'):
                            with rowColumnLayout(numberOfColumns=2):
                                text(label='Suffix:')
                                self.elements['suffix'] = textField(text='_vn')
                                text(label='Number:')
                                self.elements['version'] = intField(value=1, min=1)
                        button(label="Send", c=Callback(self.send))
                        # self.window().setResizeToFitChildren(True)

    def get_value(self):
        self.results = {}
        for key, value in self.elements.items():
            if isinstance(value, dict):
                self.results[key] = []
                for subkey, subvalue in value.items():
                    if subvalue.getValue():
                        self.results[key].append(subkey)
            else:
                try:
                    self.results[key] = value.getValue()
                except:
                    self.results[key] = value.getText()
        return self.results

    def send(self, *args, **kwargs):
        kwargs = self.get_value()
        print kwargs
        ul.send_current_file(**kwargs)


class FacialRig(object):
    def __init__(self):
        self._name = 'FacialRigUI'
        self._title = 'Facial Rig Window'
        self.window = window(self._name, title=self._title)
        self.__set()

    def window(self):
        if window(self._name, ex=True):
            deleteUI(self._name)
        self._window = window(self._name, title=self._title, rtf=True, width=10, height=10, sizeable=False)
        return self._window

    def info(self):
        print 'self:', self
        print '__str__:', self.__str__()
        print '__repr__:', self.__repr__()
        print 'window:', self.window(), type(self.window())
        print 'name:', self.name()
        if window(self.name(), ex=True):
            print self.name(), 'exists'

    def _set(self):
        self.window()
        self.template = uiTemplate('SendCurrentFileUITemplate', force=True)
        self.template.define(button, width=100, height=40, align='left')
        self.template.define(frameLayout, borderVisible=False, labelVisible=True)
        self.template.define(rowColumnLayout, numberOfColumns=3, columnWidth=[(1, 90), (2, 90), (3, 90)])
        self.elements = {}

    def show(self):
        with self.window():
            with self.template:
                with frameLayout(label='Sending {}'.format(scene_name.dirname())):
                    with columnLayout(adjustableColumn=1):
                        button(label="Rig It", c=Callback(self.apply))

    def apply(*args, **kwargs):
        rig.create_facial_rig()


class SkinWeightSetter(object):
    '''Tools to set skin weight and transfer skinCluster
    '''
    def __init__(self):
        self.skin_type = 'Classic'
        self.last_selected = []
        self.weight_value = 1.0
        self.normalize = True
        self.hierachy = False
        self.dual_weight_value = 0.0
        self.interactive = False
        self.weight_threshold = (0.0, 0.1)
        self.dual_interactive = False
        self.weight_tick = 5
        self.ui = {}

    def last_selection(self):
        self.last_selected = selected()
        return self.last_selected

    def preview_skin_weight(self):
        get_joint = ls(self.last_selection(), type='joint', orderedSelection=True)
        if not get_joint:
            return
        if currentCtx() != 'artAttrSkinContext':
            mm.eval('artAttrSkinToolScript 3;')
        lastJoint = artAttrSkinPaintCtx(currentCtx(), query=True, influence=True)
        # artAttrSkinPaintCtx(currentCtx(), edit=True, influence=get_joint[0])
        mm.eval('''
        artAttrSkinToolScript 3;
        artSkinInflListChanging "%s" 0;
        artSkinInflListChanging "%s" 1;
        artSkinInflListChanged artAttrSkinPaintCtx;
        artAttrSkinPaintModePaintSelect 1 artAttrSkinPaintCtx;'''
                % (lastJoint, unicode(get_joint[0])))

    def autoUpdateUI(self):
        jobNum = scriptJob( e= ["SelectionChanged",self.update_ui], parent = 'SkinWeightSetterUI')

    def update_ui(self):
        sel = selected()
        msg = [i.name().split('|')[-1] for i in sel if hasattr(i,'name')]
        self.ui['messageLine'].setLabel(','.join(msg))
        componentList = [c for c in sel if c.nodeType()=='mesh']
        if componentList:
            self.ui['dualInfo'].setLabel(','.join(['%s: %s'%(i[0],str(i[1])) for i in ru.dual_weight_setter(componentList, query=True)]))
        try:
            skinClster = ul.get_skin_cluster(sel[0])
            if skinClster:
                skinTypeVal =  skinClster.getSkinMethod()+1
                self.ui['skinType'].setSelect(skinTypeVal)
        except:
            pass
        if not sel:
            self.ui['messageLine'].setLabel('')

    def set_weight_threshold(self, *args):
        self.weight_threshold = (args[0], args[1])

    def set_skin_type(*args):
        ru.switch_skin_type(type=args[1], sl=True)
        headsUpMessage("Skin type set to %s" % args[1], time=0.2)

    def set_interactive_state(self):
        self.interactive = False if self.interactive else True
        headsUpMessage("Interactive %s" % self.interactive, time=0.2)

    def set_dual_interactive_state(self):
        self.dual_interactive = False if self.dual_interactive else True
        headsUpMessage("Interactive %s" % self.dual_interactive, time=0.2)

    def set_weight(self, value):
        self.weight_value = round(value, 2)
        self.skin_weight_slider_ui.setValue(self.weight_value)
        if self.interactive:
            self.apply_weight()

    def set_normalize_state(self, value):
        self.normalize = False if self.normalize else True
        headsUpMessage("Normalize %s" % self.normalize, time=0.2)

    def set_hierachy_state(self, value):
        self.hierachy = False if self.hierachy else True
        headsUpMessage("Hierachy %s" % self.hierachy, time=0.2)

    def set_dual_weight(self, value):
        self.dual_weight_value = round(value, 2)
        self.dual_weight_slider_ui.setValue(self.dual_weight_value)
        if self.dual_interactive:
            self.dual_weight_setter()

    def select_skin_vertex(self):
        ru.skin_weight_filter(
            min=self.weight_threshold[0],
            max=self.weight_threshold[1],
            select=True,
            sl=True)

    @showsHourglass
    def apply_weight(self):
        #if currentCtx() == 'artAttrSkinContext':
        #    mm.eval('artAttrSkinPaintModePaintSelect 0 artAttrSkinPaintCtx')
        #if not selected():
        #    select(self.last_selected, r=True)
        ru.skin_weight_setter(
            skin_value=self.weight_value,
            normalized=self.normalize,
            hierachy=self.hierachy,
            sl=True)
        # self.last_selection()
        self.preview_skin_weight()
        headsUpMessage("Weight Set!", time=0.2)

    @showsHourglass
    def apply_dual_weight(self):
        ru.dual_weight_setter(
            weight_value=self.dual_weight_value,
            sl=True)
        # self.last_selection()
        headsUpMessage("Dual Quarternion Weight Set!", time=0.2)

    def init_ui(self):
        if window('SkinWeightSetterUI', ex=True):
            deleteUI('SkinWeightSetterUI', window=True)
            windowPref('SkinWeightSetterUI', remove=True)
        with window(
                'SkinWeightSetterUI',
                t="Skin Weight Setter",
                rtf=True):
            with frameLayout(
                label='Set Weight Tool',
                borderVisible=True):
                with columnLayout(adjustableColumn=1):
                    self.ui['skinType'] = optionMenu(
                        label='Skin Type:',
                        changeCommand=self.set_skin_type)
                    with self.ui['skinType']:
                        menuItem(label='Classis')
                        menuItem(label='Dual')
                        menuItem(label='Blend')
                    separator(height=10)

                    with rowColumnLayout(
                        numberOfColumns=2,
                        columnWidth=[(1, 320), (2, 120)]):
                        self.skin_weight_theshold = floatFieldGrp(
                            numberOfFields=2,
                            label='Weight Threshold:',
                            value1=self.weight_threshold[0], value2=self.weight_threshold[1],
                            cc=self.set_weight_threshold)
                        button(
                            label='Select Vertices',
                            annotation='Select Skin Vertex with weight within threshold',
                            c=Callback(self.select_skin_vertex))
                    separator(height=10)
                with columnLayout(
                    adjustableColumn=1):
                    with rowColumnLayout(
                        numberOfColumns=3,
                        columnWidth=[(1, 140), (2, 80)]):
                        text(label='Option: ', align='right')
                        checkBox(
                            label='Normalize',
                            annotation='if Normalize is uncheck, set all selected joint weight the same',
                            value=self.normalize,
                            cc=self.set_normalize_state)
                        checkBox(
                            label='Hierachy',
                            annotation='if Hierachy is check, set weight value for child Joint',
                            value=self.hierachy,
                            cc=self.set_hierachy_state)
                    self.skin_weight_slider_ui = floatSliderButtonGrp(
                        label='Skin Weight: ',
                        annotation='Click "Set" to set skin weight or use loop button to turn on interactive mode',
                        field=True, precision=2,
                        value=self.weight_value,
                        minValue=0.0, maxValue=1.0,
                        cc=self.set_weight,
                        buttonLabel='Set',
                        bc=Callback(self.apply_weight),
                        image='playbackLoopingContinuous.png',
                        sbc=self.set_interactive_state)
                    separator(height=5, style='none')
                with columnLayout(adjustableColumn=1):
                    with gridLayout(
                        numberOfColumns=self.weight_tick,
                        cellWidthHeight=(95, 30)):
                        weight_value = 1.0 / (self.weight_tick - 1)
                        for i in range(self.weight_tick):
                            button(
                                label=str(weight_value * i),
                                annotation='Set skin weight to %04.2f' % (
                                    weight_value * i),
                                c=Callback(
                                    self.set_weight, weight_value * i))
                    separator(height=10)

                    self.dual_weight_slider_ui = floatSliderButtonGrp(
                        label='Dual Quarternion Weight: ',
                        annotation='Click "Set" to set skin weight or use loop button to turn on interactive mode',
                        field=True, precision=2,
                        value=self.dual_weight_value,
                        minValue=0.0, maxValue=1.0,
                        cc=self.set_dual_weight,
                        buttonLabel='Set',
                        bc=Callback(self.apply_dual_weight),
                        image='playbackLoopingContinuous.png',
                        sbc=self.set_dual_interactive_state)
                    separator(height=5, style='none')

                    with gridLayout(
                        numberOfColumns=self.weight_tick,
                        cellWidthHeight=(95, 30)):
                        for i in range(self.weight_tick):
                            button(
                                label=str(weight_value * i),
                                annotation='Set dual quaternion weight to %04.2f' % (weight_value * i),
                                c=Callback(
                                    self.set_dual_weight, weight_value * i))
                        self.ui['dualInfo']=text(label='',align='left')
                    #separator(height=5, style='none')

            with frameLayout(label='Utils',borderVisible=True):
                with columnLayout():
                    text(label='Bone Naming Tool:')
                    with rowColumnLayout(
                        numberOfColumns=7,
                        columnWidth=[
                            (1,150),
                            (2,60),
                            (3,40),]):
                        self.ui['renameBone']=[]
                        self.ui['renameBone'].append(textField())
                        self.ui['renameBone'].append(optionMenu())
                        with self.ui['renameBone'][1]:
                            menuItem(label='')
                            menuItem(label='Front')
                            menuItem(label='Left')
                            menuItem(label='Right')
                            menuItem(label='Center')
                            menuItem(label='Back')
                            menuItem(label='Middle')
                        self.ui['renameBone'].append(intField(value=0))
                        self.ui['renameBone'].append(intField(value=1))
                        self.ui['renameBone'].append(textField(text='bon'))
                        button(
                            label='Rename',
                            c=lambda x:ru.rename_bone_Chain(
                                        self.ui['renameBone'][0].getText()+self.ui['renameBone'][1].getValue(),
                                        self.ui['renameBone'][2].getValue(),
                                        self.ui['renameBone'][3].getValue(),
                                        self.ui['renameBone'][4].getText(),
                                        sl=True))
                        button(
                            label='Label',
                            annotation='use joint name as label',
                            c=Callback(ru.label_joint, sl=True))
                with rowColumnLayout(
                    numberOfColumns=4,
                    columnWidth=[(1,100),]):
                    button(
                        label='add Influence',
                        annotation='add influence to skin mesh',
                        c=Callback(
                            ru.add_joint_influence,
                            sl=True))
                    button(
                        label='Freeze Skin Joint',
                        annotation='Freeze transform for joint connect to Skin Cluster',
                        c=Callback(
                            ru.freeze_skin_joint,
                            sl=True))
                    button(
                        label = 'Freeze Skin Joint Chain',
                        annotation='Freeze transform for joint Chain connect to Skin Cluster',
                        c = Callback(
                            ru.freeze_skin_joint,
                            hi=True,
                            sl=True))
                    button(
                        label = 'Transfer Weight',
                        annotation='*Select 2 bone*. Transfer skin weight from one bone to another',
                        c=Callback(
                            ru.move_skin_weight,
                            sl=True))
                    button(
                        label = 'Transfer Weight Chain',
                        annotation='*Select 2 bone root*. Transfer skin weight from one bone Chain to another',
                        c = Callback(
                                ru.move_skin_weight,
                                hi=True,
                                sl=True))
                    button(
                        label = 'Reset BindPose',
                        annotation='Reset skin bind pose',
                        c = Callback(
                            ru.reset_bindPose_all))
                separator(height=10, style='none')

            with frameLayout(label='Status',borderVisible=True):
                with columnLayout(adjustableColumn=1):
                    with rowColumnLayout(
                        numberOfColumns=2,
                        columnWidth=[(1,100), (2, 300)]):
                        text(label='Current Selection:',align='left')
                        self.ui['messageLine'] = text(
                            label='',
                            align='left')
                    separator(height=10, style='none')
                    self.ui['helpLine'] = helpLine(
                        annotation='copyright 2017 by Nguyen Phi Hung')
        self.autoUpdateUI()

    @classmethod
    def show(cls):
        cls().init_ui()

def mirror_uv():
    if window('MirrorUVUI', ex=True):
        deleteUI('MirrorUVUI', window=True)
        windowPref('MirrorUVUI', remove=True)
    window('MirrorUVUI', t="Mirror UI")
    columnLayout(adjustableColumn=1)
    rowColumnLayout(
        numberOfColumns=3,
        columnWidth=[(1, 90), (2, 90), (3, 60)])
    mirrorDirID = radioCollection()
    radioButton(label="Left", select=True)
    radioButton(label="Right")
    button(label="Mirror",
           c=lambda *arg: ul.mirrorUV(
               dir=radioButton(mirrorDirID.getSelect(),
                               q=1, l=1)))
    setParent('..')
    showWindow()
