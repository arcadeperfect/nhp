from nhp.read_tools.recursive_loader import view
from nhp.read_tools.recursive_loader import model
from nhp.read_tools.recursive_loader import controller


# global to prevent from being removed
VIEW = None

def show():
    
    global VIEW # global to prevent from being removed
    
    VIEW = view.View()
    VIEW.raise_()
    VIEW.show()
    
    model_ = model.Model()
    controller.Controller(VIEW, model_)