import os
import sys
# import site
import core
# import etc
import main
# import project_specific
import os
basePath = os.path.dirname(__file__)
################################################################



#======================================================#
#Init Maya Path
#======================================================#

# os.environ["MAYA_LOCATION"] = "C:\Program Files\Autodesk\Maya2018"
# os.environ["PYTHONHOME"]    = "C:\Program Files\Autodesk\Maya2018\Python"
# os.environ["PATH"] = "C:\\Program Files\\Autodesk\\Maya2018\\bin;" + os.environ["PATH"]

# sys.path.append("C:\Program Files\Autodesk\Maya2018\Python\lib\site-packages\setuptools-0.6c9-py2.6.egg")
# sys.path.append("C:\Program Files\Autodesk\Maya2018\Python\lib\site-packages\pymel-1.0.0-py2.6.egg")
# sys.path.append("C:\Program Files\Autodesk\Maya2018\Python\lib\site-packages\ipython-0.10.1-py2.6.egg")
# sys.path.append("C:\Program Files\Autodesk\Maya2018\Python\lib\site-packages\ply-3.3-py2.6.egg")                         
# sys.path.append("C:\Program Files\Autodesk\Maya2018\\bin\python26.zip")
# sys.path.append("C:\Program Files\Autodesk\Maya2018\Python\DLLs")
# sys.path.append("C:\Program Files\Autodesk\Maya2018\Python\lib")
# sys.path.append("C:\Program Files\Autodesk\Maya2018\Python\lib\plat-win")
# sys.path.append("C:\Program Files\Autodesk\Maya2018\Python\lib\lib-tk")
# sys.path.append("C:\Program Files\Autodesk\Maya2018\\bin")
# sys.path.append("C:\Program Files\Autodesk\Maya2018\Python")
# sys.path.append("C:\Program Files\Autodesk\Maya2018\Python\lib\site-packages")

# import maya.standalone
# maya.standalone.initialize(name='python')

################################################################
# installPackages = []
# installPackages.append('packages')
# for package in installPackages:
#     installpath = os.path.join(basePath, package)
#     if os.path.isdir(installpath):
#         site.addsitedir(installpath)
#     else:
#         print installpath, 'does not exists'
# print 'third Party packages iniliazize'
def _reload():
    for mod in [core,main]:
        reload(mod)
        if hasattr(mod,'_reload'):
            mod._reload()
        # print mod.__name__, 'reload'