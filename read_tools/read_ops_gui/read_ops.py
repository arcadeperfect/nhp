from typing import Optional
from nhp.read_tools.read_ops_gui import view
from nhp.read_tools.read_ops_gui import model
from nhp.read_tools.read_ops_gui import controller
from pathlib import Path


import nuke

# global to prevent from being removed
VIEW = None
CONTROLLER = None

def show(node: nuke.Node):
    global VIEW, CONTROLLER
    
    # If VIEW exists, close and delete it
    if VIEW is not None:
        VIEW.close()
        VIEW.deleteLater()
        
    VIEW = view.View()
    VIEW.raise_()
    VIEW.show()
    
    model_ = model.Model(node)
    CONTROLLER = controller.Controller(VIEW, model_)  

# def show_move():
#     global VIEW, CONTROLLER
    
#     if VIEW is not None:
#         VIEW.close()
#         VIEW.deleteLater()
        
#     VIEW = view.View()
#     VIEW.raise_()
#     VIEW.show()
    
#     model_ = model.Model()
#     CONTROLLER = controller.Controller(VIEW, model_)  
    