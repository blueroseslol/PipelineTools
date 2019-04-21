import pymel.core as pm
import inspect

class AbstractMeta(object):
    _mNode = None
    _instance = None
    def __new__(cls):
        print cls._mNode, cls._instance
        if not cls._mNode:
            cls._mNode = pm.nt.Network()
        if not cls._instance:
            cls._instance = super(AbstractMeta, cls).__new__(cls)
            #cls.clsInstance.__init__()
            #cls.clsInstance.__dict__ = cls.mNode.__dict__
            for methodname, method in inspect.getmembers(cls._mNode, inspect.ismethod):
                object.__setattr__(cls._instance, methodname, method)
            #object.__setattr__(cls._instance, "__getattribute__", cls._mNode.__getattribute__)
        return cls._instance

    def __init__(self):
        self.ref = None
        self.rename("abc")
        self.addAttr("Type", dt="string")
        self.setAttr("Type", "AbstractMeta")

    def __getattr__(self, atr):
        return self._mNode.__getattr__(atr)