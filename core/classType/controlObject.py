import os
import pymel.core as pm
import general_utils as ul
import rigging_utils as ru
import logging
# ------------------------
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)
# ------------------------
class ControlObject(object):
    '''Class to create Control'''

    def __init__(
            self,
            name='ControlObject',
            suffix='ctl',
            radius=1,
            res='high',
            length=2.0,
            axis='XY',
            offset=0.0,
            color='red'):
        self._suffix = suffix
        self._name = '{}_{}'.format(name, suffix)
        self._radius = radius
        self._length = length
        self._axis = axis
        self._offset = offset
        self._step = res
        self._color = color
        self.controls = {}
        self.controls['all'] = []
        self.controlGps = []

        self._resolutions = {
            'low': 4,
            'mid': 8,
            'high': 24
        }
        self._axisList = ['XY', 'XZ', 'YZ']
        self._axisList.extend([a[::-1] for a in self._axisList])  ## add reverse asxis
        self._axisList.extend(['-%s' % a for a in self._axisList])  ## add minus axis
        self._colorData = {
            'white': pm.dt.Color.white,
            'red': pm.dt.Color.red,
            'green': pm.dt.Color.green,
            'blue': pm.dt.Color.blue,
            'yellow': [1, 1, 0, 0],
            'cyan': [0, 1, 1, 0],
            'violet': [1, 0, 1, 0],
            'orange': [1, 0.5, 0, 0],
            'pink': [1, 0, 0.5, 0],
            'jade': [0, 1, 0.5, 0]
        }
        self._controlType = {
            'Pin': self.Pin,
            'Circle': self.Circle,
            'Octa': self.Octa,
            'Cylinder': self.Cylinder,
            'Sphere': self.Sphere,
            'NSphere': self.NSphere,
            'Rectangle': self.Rectangle
        }
        self._currentType = self._controlType.keys()[0]
        self._uiOption = {
            'group':True,
            'pre':False
        }
        self._uiElement = {}
        log.info('Control Object class name:{} initialize'.format(name))
        log.debug('\n'.join(['{}:{}'.format(key, value) for key, value in self.__dict__.items()]))

    ####Define Property
    @property
    def name(self):
        if self._suffix not in self._name:
            self._name = '{}_{}'.format(self._name.split('_')[0], self._suffix)
        return self._name

    @name.setter
    def name(self, newName):
        if self._suffix not in newName:
            self._name = '{}_{}'.format(newName, self._suffix)

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, newradius):
        assert any([isinstance(newradius, typ) for typ in [float, int]]), "radius must be of type float"
        self._radius = newradius

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, newlength):
        assert any([isinstance(newlength, typ) for typ in [float, int]]), "length must be of type float"
        self._length = newlength

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, newoffset):
        if any([isinstance(newoffset, typ) for typ in [list, set, tuple]]):
            assert (len(newoffset) == 3), 'offset must be a float3 of type list,set or tuple'
            self._offset = newoffset

    @property
    def color(self):
        return pm.dt.Color(self._color)

    @color.setter
    def color(self, newcolor):
        if isinstance(newcolor, str):
            assert (self._colorData.has_key(newcolor)), "color data don't have '%s' color.\nAvailable color:%s" % (
                newcolor, ','.join(self._colorData))
            self._color = self._colorData[newcolor]
        if any([isinstance(newcolor, typ) for typ in [list, set, tuple]]):
            assert (len(newcolor) >= 3), 'color must be a float4 or float3 of type list,set or tuple'
            self._color = pm.dt.Color(newcolor)

    @property
    def axis(self):
        return self._axis

    @axis.setter
    def axis(self, newaxis):
        if isinstance(newaxis, str) or isinstance(newaxis, unicode):
            assert (newaxis in self._axisList), "axis data don't have '%s' axis.\nAvailable axis:%s" % (
                newaxis, ','.join(self._axisData))
            self._axis = newaxis

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, newres):
        assert (
            self._resolutions.has_key(newres)), "step resolution value not valid.\nValid Value:%s" % self._resolutions
        self._step = self._resolutions[newres]

    # @ul.error_alert
    def __setProperty__(func):
        '''Wraper that make keywords argument of control type function
        to tweak class Attribute'''

        @ul.wraps(func)
        def wrapper(self, *args, **kws):
            # store Class Attribute Value
            oldValue = {}
            oldValue['offset'] = self.offset
            oldValue['res'] = self.step
            oldValue['color'] = self.color
            fkws = func.__defaults__[0]
            # Assign Keyword Argument value to Class Property value
            log.debug('Assign KeyWord to ControlObject Class Propety')
            if 'offset' in kws:
                self.offset = kws['offset']
                log.debug('{} set to {}'.format('offset', offset))
            if 'res' in kws:
                self.step = kws['res']
                log.debug('{} set to {}'.format('res', res))
            if 'color' in kws:
                self.color = kws['color']
                log.debug('{} set to {}'.format('color', color))

            for key, value in kws.items():
                if self.__dict__.has_key(key):
                    oldValue[key] = self.__dict__[key]
                    self.__dict__[key] = value
                    log.debug('{} set to {}'.format(key, value))
                if fkws.has_key(key):
                    fkws[key] = value

            if kws.has_key('group'):
                groupControl = kws['group']
            elif kws.has_key('grp'):
                groupControl = kws['grp']
            else:
                groupControl = True

            if kws.has_key('prefixControlName'):
                prefixName = kws['prefixControlName']
            elif kws.has_key('pre'):
                prefixName = kws['pre']
            else:
                prefixName = False

            #### Create and Modify Control object
            control = func(self, mode=fkws)
            if prefixName is True:
                control.rename('_'.join([func.__name__, self.name]))
            self.controls['all'].append(control)
            if not self.controls.has_key(func.__name__):
                self.controls[func.__name__] = []
            self.controls[func.__name__].append(control)
            if kws.has_key('setAxis') and kws['setAxis'] is True:
                self.setAxis(control, self.axis)
            self.setColor(control, self.color)
            control.setTranslation(self.offset, 'world')
            pm.makeIdentity(control, apply=True)
            log.info('Control of type:{} name {} created along {}'.format(func.__name__, control.name(), self._axis))
            if groupControl is True:
                Gp = ru.group(control)
                self.controlGps.append(Gp)
            else:
                pm.xform(control, pivots=(0, 0, 0), ws=True, dph=True, ztp=True)

            #### reset Class Attribute Value to __init__ value
            for key, value in oldValue.items():
                self.__dict__[key] = value
                if key == 'offset':
                    self._offset = value
                if key == 'res':
                    self._step = value
                if key == 'color':
                    self._color = value
            return control

        return wrapper

    #### Control Type
    @__setProperty__
    def Octa(self, mode={}):
        crv = ru.createPinCircle(
            self.name,
            step=4,
            sphere=True,
            radius=self.radius,
            length=0)
        print self
        return crv

    @__setProperty__
    def Pin(self, mode={'mirror': False, 'sphere': False}):
        newAxis = self._axis
        if mode['mirror']:
            newAxis = 'm' + self._axis
        else:
            newAxis = self._axis.replace('m', '')
        crv = ru.createPinCircle(
            self.name,
            axis=newAxis,
            sphere=mode['sphere'],
            radius=self.radius,
            step=self.step,
            length=self.length)
        return crv

    @__setProperty__
    def Circle(self, mode={}):
        crv = ru.createPinCircle(
            self.name,
            axis=self._axis,
            radius=self.radius,
            step=self.step,
            sphere=False,
            length=0)
        return crv

    @__setProperty__
    def Cylinder(self, mode={}):
        crv = ru.createPinCircle(
            self.name,
            axis=self._axis,
            radius=self.radius,
            step=self.step,
            cylinder=True,
            height=self.length,
            length=0,
        )
        return crv

    @__setProperty__
    def NSphere(self, mode={'shaderName': 'control_mtl'}):
        crv = pm.sphere(r=self.radius, n=self.name)
        #### set invisible to render
        crvShape = crv[0].getShape()
        crvShape.castsShadows.set(False)
        crvShape.receiveShadows.set(False)
        crvShape.motionBlur.set(False)
        crvShape.primaryVisibility.set(False)
        crvShape.smoothShading.set(False)
        crvShape.visibleInReflections.set(False)
        crvShape.visibleInRefractions.set(False)
        crvShape.doubleSided.set(False)
        #### set Shader
        shdr_name = '{}_{}'.format(mode['shaderName'], self.name)
        sg_name = '{}{}'.format(shdr_name, 'SG')
        if pm.objExists(shdr_name) or pm.objExists(sg_name):
            try:
                pm.delete(shdr_name)
                pm.delete(sg_name)
            except:
                pass
        shdr, sg = pm.createSurfaceShader('surfaceShader')
        pm.rename(shdr, shdr_name)
        pm.rename(sg, sg_name)
        shdr.outColor.set(self.color.rgb)
        shdr.outTransparency.set([self.color.a for i in range(3)])
        pm.sets(sg, fe=crv[0])
        return crv[0]

    @__setProperty__
    def Sphere(self, mode={}):
        crv = ru.createPinCircle(
            self.name,
            axis=self._axis,
            radius=self.radius,
            step=self.step,
            sphere=True,
            length=0)
        return crv

    @__setProperty__
    def Rectangle(self, mode={}):
        crv = ru.create_square(
            self.name,
            length=self.radius,
            width=self.length,
            offset=self.offset)
        return crv
    #### control method
    def getControls(self):
        msg = ['{} contain controls:'.format(self.name)]
        for key, ctls in self.controls.items():
            msg.append('+' + key)
            for ctl in ctls:
                msg.append('--' + ctl)
        log.info('\n'.join(msg))
        return self.controls

    def setAxis(self, control, axis='XY'):
        axisData = {}
        axisData['XY'] = [0, 0, 90]
        axisData['YX'] = [0, 0, -90]
        axisData['XZ'] = [0, 90, 0]
        axisData['ZX'] = [0, -90, 0]
        axisData['YZ'] = [90, 0, 0]
        axisData['ZY'] = [-90, 0, 0]
        assert (axis in axisData), "set axis data don't have '%s' axis.\nAvailable axis:%s" % (axis, ','.join(axisData))
        control.setRotation(axisData[axis])
        # print control.getRotation()
        pm.makeIdentity(control, apply=True)
        if not control:
            for control in self.controls:
                self.setAxis(control)

    def setColor(self, control, newColor=None):
        print control.name
        if newColor:
            self.color = newColor
        try:
            control.overrideEnabled.set(True)
            control.overrideRGBColors.set(True)
            control.overrideColorRGB.set(self.color)
            sg = control.shadingGroups()[0] if control.shadingGroups() else None
            if sg:
                shdr = sg.inputs()[0]
                shdr.outColor.set(self.color.rgb)
                shdr.outTransparency.set([self.color.a for i in range(3)])
        except AttributeError as why:
            log.error(why)

    def deleteControl(self, id=None, deleteGp=False):
        if id and id < len(self.controls):
            pm.delete(self.controls[id])
            return self.control[id]
        pm.delete(self.controls)
        if deleteGp:
            pm.delete(self.controlGps)

    def createControl(self):
        newCtl = self._controlType[self._currentType](**self._uiOption)
        return newCtl

    def changeControlShape(self, selectControl, *args):
        temp = self.createControl()
        #temp.setParent(selectControl.getParent())
        ru.xformTo(temp, selectControl)
        pm.delete(selectControl.getShape(), shape=True)
        pm.parent(temp.getShape(), selectControl, r=True, s=True)
        pm.delete(temp)
        return selectControl