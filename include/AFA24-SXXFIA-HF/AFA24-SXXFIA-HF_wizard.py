#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

from __future__ import division
import pcbnew
import wx

import FootprintWizardBase

class FPC_FootprintWizard(FootprintWizardBase.FootprintWizard):

    def GetName(self):
        return "FPC AFA24-SXXFIA-HF"

    def GetDescription(self):
        return "FPC AFA24-SXXFIA-HF Footprint Wizard"

    def GetValue(self):
        pins = self.parameters["Pads"]["n"]
        return ("FPC-SMD_%dP-P1.00_AFA24-S0%dFIA-HF" % (pins, pins)) if pins < 10 else ("FPC-SMD_%dP-P1.00_AFA24-S%dFIA-HF" % (pins, pins))

    def GenerateParameterList(self):
        self.AddParam( "Pads", "n", self.uInteger, 4 )              ##
        self.AddParam( "Pads", "pitch", self.uMM, 1.0 )             ##
        self.AddParam( "Pads", "width", self.uMM, 0.3 )             ##
        self.AddParam( "Pads", "height", self.uMM, 1.2)             ##

        self.AddParam( "Shield", "shield_to_pad", self.uMM, 2.15 )  ##
        self.AddParam( "Shield", "from_top", self.uMM, 3.15 )       ##
        self.AddParam( "Shield", "width", self.uMM, 1.8 )           ##
        self.AddParam( "Shield", "height", self.uMM, 2.0 )          ##

        self.AddParam( "Courtyard", "spacingX", self.uMM, 2.5 )
        self.AddParam( "Courtyard", "offsetY", self.uMM, 0.25 )     ##
        self.AddParam( "Courtyard", "height", self.uMM, 4.9 )       ##
        self.AddParam( "Courtyard", "line", self.uMM, 0.3 )         ##


    # build a rectangular pad
    def smdRectPad(self,module,size,pos,name):
        pad = pcbnew.PAD(module)
        pad.SetSize(size)
        pad.SetShape(pcbnew.PAD_SHAPE_RECT)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        pad.SetLayerSet( pad.SMDMask() )
        pad.SetPosition(pos)
        pad.SetName(name)
        return pad

    def CheckParameters(self):
        #TODO implement custom parameter checking
        pass

    def BuildThisFootprint(self):
        p = self.parameters
        pad_count       = int(p["Pads"]["n"])
        pad_width       = p["Pads"]["width"]
        pad_height      = p["Pads"]["height"]
        pad_pitch       = p["Pads"]["pitch"]

        shl_width       = p["Shield"]["width"]
        shl_height      = p["Shield"]["height"]
        shl_to_pad      = p["Shield"]["shield_to_pad"]
        shl_from_top    = p["Shield"]["from_top"]

        cty_spacingX    = p["Courtyard"]["spacingX"]
        cty_offsetY     = p["Courtyard"]["offsetY"]
        cty_height      = p["Courtyard"]["height"]
        cty_line        = p["Courtyard"]["line"]

        offsetX         = pad_pitch * ( pad_count-1 ) / 2
        size_pad = pcbnew.VECTOR2I( int(pad_width), int(pad_height) )
        size_shld = pcbnew.VECTOR2I(shl_width, shl_height)
        size_text = self.GetTextSize()  # IPC nominal

        # Gives a position and size to ref and value texts:
        textposy = pad_height/2 + pcbnew.FromMM(1) + self.GetTextThickness()
        angle_degree = 0.0
        self.draw.Reference( 0, textposy, size_text, angle_degree )

        textposy = textposy + size_text + self.GetTextThickness()
        self.draw.Value( 0, textposy, size_text )

        # create a pad array and add it to the module
        for n in range ( 0, pad_count ):
            xpos = (int)(pad_pitch*n - offsetX)
            pad = self.smdRectPad(self.module,size_pad, pcbnew.VECTOR2I( xpos, 0), str(n+1))
            self.module.Add(pad)


        # Mechanical shield pads: left pad and right pad
        xpos = -shl_to_pad-offsetX
        pad_s0_pos = pcbnew.VECTOR2I( int(xpos), int(shl_from_top) )
        pad_s0 = self.smdRectPad(self.module, size_shld, pad_s0_pos, "0")
        xpos = (pad_count-1) * pad_pitch+shl_to_pad - offsetX
        pad_s1_pos = pcbnew.VECTOR2I( int(xpos), int(shl_from_top) )
        pad_s1 = self.smdRectPad(self.module, size_shld, pad_s1_pos, "0")

        self.module.Add(pad_s0)
        self.module.Add(pad_s1)

        if cty_offsetY < pad_height / 2:
            self.draw.Line( -(offsetX + cty_spacingX), cty_offsetY, -(offsetX + (pad_width / 2) + (pad_pitch / 2)), cty_offsetY )
            self.draw.Line( (offsetX + cty_spacingX), cty_offsetY, (offsetX + (pad_width / 2) + (pad_pitch / 2)), cty_offsetY )
        else:
            self.draw.Line( -(offsetX + cty_spacingX), cty_offsetY, (offsetX + cty_spacingX), cty_offsetY )
            
        self.draw.Line( -(offsetX + cty_spacingX), cty_offsetY + cty_height, (offsetX + cty_spacingX), cty_offsetY + cty_height )

        
        outlineX = (offsetX + cty_spacingX)

        if outlineX > (xpos - shl_width / 2 - cty_line / 2) and outlineX < (xpos + shl_width / 2 + cty_line / 2):
            self.draw.Line( -(outlineX), cty_offsetY, -(outlineX), shl_from_top - shl_height / 2 - cty_line )
            self.draw.Line( -(outlineX), shl_from_top + shl_height / 2 + cty_line, -(outlineX), cty_offsetY + cty_height )
            self.draw.Line( (outlineX), cty_offsetY, (outlineX), shl_from_top - shl_height / 2 - cty_line )
            self.draw.Line( (outlineX), shl_from_top + shl_height / 2 + cty_line, (outlineX), cty_offsetY + cty_height )
        else:
            self.draw.Line( -(outlineX), cty_offsetY, -(outlineX), cty_offsetY + cty_height )
            self.draw.Line( (outlineX), cty_offsetY, (outlineX), cty_offsetY + cty_height )

        # Courtyard
        self.draw.SetLayer(pcbnew.F_CrtYd)
        self.draw.SetLineThickness(pcbnew.FromMM(0.05))
        self.draw.Line( -outlineX, cty_offsetY, outlineX, cty_offsetY )
        self.draw.Line( -outlineX, cty_offsetY + cty_height, outlineX, cty_offsetY + cty_height )
        self.draw.Line( -outlineX, cty_offsetY, -outlineX, cty_offsetY + cty_height )
        self.draw.Line( outlineX, cty_offsetY, outlineX, cty_offsetY + cty_height )

FPC_FootprintWizard().register()
