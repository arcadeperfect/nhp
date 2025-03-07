import nuke

from nhp.read_tools.read_wrapper import FileHandlerType

class Controller:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        
        padding = self.model.read_wrapper.handler_type == FileHandlerType.SEQUENCE
        
        self.view.initialize_fields(padding)
        self.view.set_fields(
            self.model.read_wrapper.name,
            self.model.read_wrapper.delimiter,
            self.model.read_wrapper.suffix,
            self.model.read_wrapper.padding,
            self.model.read_wrapper.extension
        )