import ui
import SkinSetter
import BSTools
import Renamer
import ControlsMaker
def _reload():
    for mod in [
        ui,
        SkinSetter,
        RebuildBS,
        Renamer,
        ControlsMaker]:
        reload(mod)