from ..Script import Script
from UM.Logger import Logger
import re

class CraftBotPauseAtLayer(Script):
    def __init__(self):
        super().__init__()

    # This function defines the plugin's appearance (i.e. name), and it's inputs in the Cura UI.
    # Settings contain the description of fields that show up in the plugin window.
    def getSettingDataString(self):
        return """{
            "name":"Pause at layer (CraftBot)",
            "description": "Triggers a pause before a specified layer.",
            "key": "CraftBotPauseAtLayer",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "pause_layer":
                {
                    "label": "Pause Layer",
                    "description": "The printer will pause before this layer is printed. This layer includes supports, and corresponds to the layers seen in the Cura viewer. Layer 1 is the first layer of the print.",
                    "type": "int",
                    "default_value": 1,
                    "minimum_value": 1
                },
                "message":
                {
                    "label": "Pause Message",
                    "description": "A message to display on the printer. The the string may contain python formatting literals for displaying the layer number.",
                    "type": "str",
                    "default_value": "User defined pause at layer {}"
                },
                "should_beep":
                {
                    "label": "Beep",
                    "description": "When ticked, the printer will emit a short tone when pausing.",
                    "type": "bool",
                    "default_value": true
                }
            }
        }"""

    # This function runs when the actual post processing takes place.
    #
    # Data consits of blocks, each containing a multi-line string of gcode.
    # Cura seems to write things as:
    #   Block 0: Start comments
    #   Block 1: Setup code
    #   Block 2: First layer of print
    #   Block 3: Second layer of pri nt
    #   ...
    #   Block N-1: ?
    #   Block N: Ending code
    #
    def execute(self, data):
        # Get the values inputted trough the cura UI
        pause_layer = self.getSettingValueByKey("pause_layer")
        message = self.getSettingValueByKey("message").format(pause_layer)
        should_beep = self.getSettingValueByKey("should_beep")

        # Construct gcode to insert
        gcode_block = [";TYPE:CUSTOM", ";pause added by post processing", ";script: PauseAtLayerCraftBot.py"]
        if should_beep:
            gcode_block.append("M300 P2000 S50 ;beep")
        gcode_block.append(self.putValue(G=197) + " " + message + " ;pause")
        # gcode_block.append(self.putValue(G=198) + " ;resume print")

        true_layer_cntr = 0

        # We iterate over each block, keeping track of the number of ;LAYER## comments, to find
        # the layer before which we will insert the gcode.
        for block_idx, block in enumerate(data):
            
            lines = block.strip().split("\n")
            
            for line_idx, line in enumerate(lines):
            
                if ";LAYER:" in line:
                    true_layer_cntr += 1

                if (true_layer_cntr == pause_layer) and not line.startswith(";"):
                    new_lines = lines[:line_idx]
                    new_lines.extend(gcode_block)
                    new_lines.extend(lines[line_idx:])

                    new_block = "\n".join(new_lines) + "\n"

                    data[block_idx] = new_block
                    
                    return data

        return data
