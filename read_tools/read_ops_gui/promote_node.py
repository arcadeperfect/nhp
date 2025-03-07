import nuke
def add_options(node):
    tab = nuke.Tab_Knob('custom_tab', 'Custom Tab')
    node.addKnob(tab)
    python_button = nuke.PyScript_Knob('python_button', 'Run Python', 'print("Button clicked!")')
    node.addKnob(python_button)