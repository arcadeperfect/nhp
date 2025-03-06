from nhp.read_tools.recursive_loader import view
from nhp.read_tools.recursive_loader import model
from nhp.read_tools.recursive_loader import controller

# global to prevent from being removed
VIEW = None
CONTROLLER = None

def show():
    global VIEW, CONTROLLER
    
    # If VIEW exists, close and delete it
    if VIEW is not None:
        VIEW.close()
        VIEW.deleteLater()
        
    VIEW = view.View()
    VIEW.raise_()
    VIEW.show()
    
    model_ = model.Model()
    CONTROLLER = controller.Controller(VIEW, model_)