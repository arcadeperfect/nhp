import nuke

from nhp.pysequitur.file_sequence import SequenceFactory
from nhp.read_tools.read_wrapper import ReadWrapper



class Model:
    def __init__(self, node):
        self.node = node
        # self.file_sequence = SequenceFactory.from_nuke_node(node)
        self.read_wrapper = ReadWrapper(node) 


    

        print(self.read_wrapper.handler_type)

    