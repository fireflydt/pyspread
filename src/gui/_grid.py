#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2008 Martin Manns
# Distributed under the terms of the GNU General Public License
# generated by wxGlade 0.6 on Mon Mar 17 23:22:49 2008

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""
_grid
=====

Provides
--------
 1. Grid: The main grid of pyspread
 2. MainWindowEventHandlers: Event handlers for Grid

"""

import wx.grid

from _events import *


class Grid(wx.grid.Grid):
    """Pyspread's main grid"""

    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        
        wx.grid.Grid.__init__(self, parent, *args, **kwargs)
        
        self.handlers = GridEventHandlers(self)
        self.cell_handlers = GridCellEventHandlers(self)
        
        self._bind()
    
    def _bind(self):
        """Bind events to handlers"""
        
        parent = self.parent
        
        handlers = self.handlers
        c_handlers = self.cell_handlers
        
        # Cell code events
        
        # Cell attribute events
        
        
        
        parent.Bind(EVT_COMMAND_FONT, c_handlers.OnCellFont)
        parent.Bind(EVT_COMMAND_FONTSIZE, c_handlers.OnCellFontSize)
        parent.Bind(EVT_COMMAND_FONTBOLD, c_handlers.OnCellFontBold)
        parent.Bind(EVT_COMMAND_FONTITALICS, c_handlers.OnCellFontItalics)
        parent.Bind(EVT_COMMAND_FONTUNDERLINE, c_handlers.OnCellFontUnderline)
        parent.Bind(EVT_COMMAND_FONTSTRIKETHROUGH, 
                    c_handlers.OnCellFontStrikethrough)
        parent.Bind(EVT_COMMAND_FROZEN, c_handlers.OnCellFrozen)
        parent.Bind(EVT_COMMAND_JUSTIFICATION, c_handlers.OnCellJustification)
        parent.Bind(EVT_COMMAND_ALIGNMENT, c_handlers.OnCellAlignment)
        parent.Bind(EVT_COMMAND_BORDERCHOICE, c_handlers.OnCellBorderChoice)
        parent.Bind(EVT_COMMAND_BORDERWIDTH, c_handlers.OnCellBorderWidth)
        parent.Bind(EVT_COMMAND_BORDERCOLOR, c_handlers.OnCellBorderColor)
        parent.Bind(EVT_COMMAND_BACKGROUNDCOLOR, 
                    c_handlers.OnCellBackgroundColor)
        parent.Bind(EVT_COMMAND_TEXTCOLOR, c_handlers.OnCellTextColor)
        parent.Bind(EVT_COMMAND_TEXTROTATATION, c_handlers.OnCellTextRotation)
        
        # Cell selection events
        
        # File events
        
        parent.Bind(EVT_COMMAND_NEW, handlers.OnNew)
        parent.Bind(EVT_COMMAND_OPEN, handlers.OnOpen)
        parent.Bind(EVT_COMMAND_SAVE, handlers.OnSave)
        parent.Bind(EVT_COMMAND_SAVEAS, handlers.OnSaveAs)
        parent.Bind(EVT_COMMAND_IMPORT, handlers.OnImport)
        parent.Bind(EVT_COMMAND_EXPORT, handlers.OnExport)
        parent.Bind(EVT_COMMAND_APPROVE, handlers.OnApprove)
        
        # Print events
        
        parent.Bind(EVT_COMMAND_PRINT, handlers.OnPrint)
        
        # Clipboard events
        
        parent.Bind(EVT_COMMAND_CUT, handlers.OnCut)
        parent.Bind(EVT_COMMAND_COPY, handlers.OnCopy)
        parent.Bind(EVT_COMMAND_COPY_RESULT, handlers.OnCopyResult)
        parent.Bind(EVT_COMMAND_PASTE, handlers.OnPaste)
        
        # Grid view events
        
        parent.Bind(EVT_COMMAND_REFRESH_SELECTION, 
                    handlers.OnRefreshSelectedCells)
        parent.Bind(EVT_COMMAND_GOTO_CELL, handlers.OnGoToCell)
        parent.Bind(EVT_COMMAND_ZOOM, handlers.OnZoom)
        
        # Find events
        
        parent.Bind(EVT_COMMAND_FIND, handlers.OnFind)
        parent.Bind(EVT_COMMAND_REPLACE, handlers.OnShowFindReplace)
        
        # Grid change events
        
        parent.Bind(EVT_COMMAND_INSERT_ROWS, handlers.OnInsertRows)
        parent.Bind(EVT_COMMAND_INSERT_COLS, handlers.OnInsertCols)
        parent.Bind(EVT_COMMAND_INSERT_TABS, handlers.OnInsertTabs)
        
        parent.Bind(EVT_COMMAND_DELETE_ROWS, handlers.OnDeleteRows)
        parent.Bind(EVT_COMMAND_DELETE_COLS, handlers.OnDeleteCols)
        parent.Bind(EVT_COMMAND_DELETE_TABS, handlers.OnDeleteTabs)
        
        parent.Bind(EVT_COMMAND_RESIZE_GRID, handlers.OnResizeGrid)
        
        # Grid attribute events
        
        # Undo/Redo events

        parent.Bind(EVT_COMMAND_UNDO, handlers.OnUndo)
        parent.Bind(EVT_COMMAND_REDO, handlers.OnRedo)

class GridCellEventHandlers(object):
    """Contains grid cell event handlers incl. attribute events"""
    
    def __init__(self, parent):
        self.main_window = parent
    
    # Cell code entry events
    
    def OnCellText(self, event):
        """Text entry event handler"""
        
        code = event.GetString()
        
        if code != "":
            try:
                post_entryline_text(self, code)
            except TypeError: 
                post_entryline_text(self, "")
        
        event.Skip()

    # Cell attribute events

    def OnCellFont(self, event):
        """Cell font event handler"""
        
        raise NotImplementedError
        
        event.Skip()
        
    def OnCellFontSize(self, event):
        """Cell font size event handler"""
        
        raise NotImplementedError
        
        event.Skip()
        
    def OnCellFontBold(self, event):
        """Cell font bold event handler"""
        
        raise NotImplementedError
        
        event.Skip()
        
    def OnCellFontItalics(self, event):
        """Cell font italics event handler"""
        
        raise NotImplementedError
        
        event.Skip()
        
    def OnCellFontUnderline(self, event):
        """Cell font underline event handler"""
        
        raise NotImplementedError
        
        event.Skip()
        
    def OnCellFontStrikethrough(self, event):
        """Cell font strike through event handler"""
        
        raise NotImplementedError
        
        event.Skip()
    
    def OnCellFrozen(self, event):
        """Cell frozen event handler"""
        
        raise NotImplementedError
        
        event.Skip()
    
    def OnCellJustification(self, event):
        """Horizontal cell justification event handler"""
        
        raise NotImplementedError
        
        event.Skip()
    
    def OnCellAlignment(self, event):
        """Vertical cell alignment event handler"""
        
        raise NotImplementedError
        
        event.Skip()
    
    def OnCellBorderChoice(self, event):
        """Cell border choice event handler"""
        
        raise NotImplementedError
        
        event.Skip()
    
    def OnCellBorderWidth(self, event):
        """Cell border width event handler"""
        
        raise NotImplementedError
        
        event.Skip()
        
    def OnCellBorderColor(self, event):
        """Cell border color event handler"""
        
        raise NotImplementedError
        
        event.Skip()
        
    def OnCellBackgroundColor(self, event):
        """Cell background color event handler"""
        
        raise NotImplementedError
        
        event.Skip()

    def OnCellTextColor(self, event):
        """Cell text color event handler"""
        
        raise NotImplementedError
        
        event.Skip()

    def OnCellTextRotation(self, event):
        """Cell text rotation event handler"""
        
        raise NotImplementedError
        
        event.Skip()
        
    # Cell edit event handlers
    
    def OnCellEditorShown(self, event):
        """Cell editor shown event handler"""
        
        raise NotImplementedError
        
        event.Skip()
        
    def OnCellEditorHidden(self, event):
        """Cell editor hidden event handler"""
        
        raise NotImplementedError
        
        event.Skip()
    
    # Cell selection event handlers
    
    def OnCellSelected(self, event):
        """Cell selection event handler"""
        
        raise NotImplementedError
        
        event.Skip()


class GridEventHandlers(object):
    """Contains grid event handlers"""
    
    def __init__(self, parent):
        self.main_window = parent
    
    def OnMouseMotion(self, event):
        """Mouse motion event handler"""
        
        raise NotImplementedError
        
        event.Skip()
    
    # File events
    
    def OnNew(self, event):
        """New grid event handler"""
        
        raise NotImplementedError
        
        event.Skip()

    def OnOpen(self, event):
        """File open event handler"""
        
        raise NotImplementedError
        
        event.Skip()
    
    def OnSave(self, event):
        """File save event handler"""
        
        raise NotImplementedError
        
        event.Skip()
    
    def OnSaveAs(self, event):
        """File save as event handler"""
        
        raise NotImplementedError
        
        event.Skip()
        
    def OnImport(self, event):
        """File import event handler"""
        
        raise NotImplementedError
        
        event.Skip()
        
    def OnExport(self, event):
        """File export event handler"""
        
        raise NotImplementedError
        
        event.Skip()
    
    def OnApprove(self, event):
        """File approve event handler"""
        
        raise NotImplementedError
        
        event.Skip()
    
    # Print events
    
    def OnPrint(self, event):
        """Print event handler"""
        
        raise NotImplementedError
        
        event.Skip()

    # Clipboard events

    def OnCut(self, event): 
        """Clipboard cut event handler"""
        
        raise NotImplementedError
        
        event.Skip()
    
    def OnCopy(self, event):
        """Clipboard copy event handler"""
        
        raise NotImplementedError
        
        event.Skip()
    
    def OnCopyResult(self, event):
        """Clipboard copy results event handler"""
        
        raise NotImplementedError
        
        event.Skip()
    
    def OnPaste(self, event):
        """Clipboard paste event handler"""
        
        raise NotImplementedError
        
        event.Skip()

    # Grid view events

    def OnGoToCell(self, event):
        """Shift a given cell into view"""
        
        raise NotImplementedError
        
        event.Skip()

    def OnRefreshSelectedCells(self, event):
        """Event handler for refreshing the selected cells via menu"""
        
        raise NotImplementedError
        
        event.Skip()
        
    def OnZoom(self, event):
        """Event handler for setting grid zoom via menu"""
        
        raise NotImplementedError
        
        event.Skip()
        
    def OnScroll(self, event):
        """Event handler for grid scroll event"""
        
        self.parent.MainGrid.view.clear()
        
        event.Skip()
    
    def OnContextMenu(self, event):
        """Context menu event handler"""
        
        raise NotImplementedError
        
        #self.PopupMenu(self.contextmenu)
        
        event.Skip()
    
    def OnMouseWheel(self, event):
        """Event handler for mouse wheel actions
        
        Invokes zoom when mouse when Ctrl is also pressed
        
        """
        
        if event.ControlDown():
            raise NotImplementedError
            
        event.Skip()
    
    # Find events

    def OnFind(self, event):
        """Find functionality should be in interfaces"""
        
        raise NotImplementedError
                
        event.Skip()
        
    def OnFindClose(self, event):
        """Refreshes the grid after closing the find dialog"""
        
        raise NotImplementedError
        
        event.Skip()

    def OnShowFindReplace(self, event):
        """Calls the find-replace dialog"""
        
        raise NotImplementedError
        
        event.Skip()

    # Grid change events
    
    def OnInsertRows(self, event):
        """Insert the maximum of 1 and the number of selected rows"""
        
        raise NotImplementedError
        
        event.Skip()
    
    def OnInsertCols(self, event):
        """Inserts the maximum of 1 and the number of selected columns"""
        
        raise NotImplementedError
        
        event.Skip()
    
    def OnInsertTabs(self, event):
        """Insert one table into MainGrid and pysgrid"""
        
        raise NotImplementedError
        
        event.Skip()
    
    def OnDeleteRows(self, event):
        """Deletes rows from all tables of the grid"""
        
        raise NotImplementedError
        
        event.Skip()
    
    def OnDeleteCols(self, event):
        """Deletes columnss from all tables of the grid"""
        
        raise NotImplementedError
        
        event.Skip()
    
    def OnDeleteTabs(self, event):
        """Deletes tables"""
        
        raise NotImplementedError
        
        event.Skip()
    
    def OnResizeGrid(self, event):
        """Resizes current grid by appending/deleting rows, cols and tables"""
        
        raise NotImplementedError
        
        event.Skip()

    # Grid attribute events

    def OnRowSize(self, event):
        """Row size event handler"""
        
        raise NotImplementedError
        
        event.Skip()
        
    def OnColSize(self, event):
        """Column size event handler"""
        
        raise NotImplementedError
        
        event.Skip()

    # Undo/Redo events

    def OnUndo(self, event):
        """Calls the gris undo method"""
        
        raise NotImplementedError
        
        event.Skip()
        
    def OnRedo(self, event):
        """Calls the gris redo method"""
        
        raise NotImplementedError
        
        event.Skip()

    
# End of class GridEventHandlers
