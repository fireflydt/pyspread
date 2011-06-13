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
_grid_actions.py
=======================

Module for main main grid level actions.
All non-trivial functionality that results from grid actions
and belongs to the grid only goes here.

Provides:
---------
  1. FileActions: Actions which affect the open grid
  2. TableRowActionsMixin: Mixin for TableActions
  3. TableColumnActionsMixin: Mixin for TableActions
  4. TableTabActionsMixin: Mixin for TableActions
  5. TableActions: Actions which affect table
  6. MacroActions: Actions on macros
  7. UnRedoActions: Actions on the undo redo system
  8. GridActions: Actions on the grid as a whole
  9. SelectionActions: Actions on the grid selection
  10. FindActions: Actions for finding and replacing
  11. AllGridActions: All grid actions as a bundle
  

"""

from config import ZOOM_FACTOR, MINIMUM_ZOOM, MAXIMUM_ZOOM
from config import default_cell_attributes

from gui._grid_table import GridTable
from gui._events import *
from lib._interfaces import sign, verify, is_pyme_present
from lib.selection import Selection

from actions._grid_cell_actions import CellActions
from actions._selection_actions import AttributeActions

class FileActions(object):
    """File actions on the grid"""
    
    def __init__(self):
        self.main_window.Bind(EVT_COMMAND_GRID_ACTION_OPEN, self.open) 
        self.main_window.Bind(EVT_COMMAND_GRID_ACTION_SAVE, self.save) 

    def validate_signature(self, filename):
        """Returns True if a valid signature is present for filename"""
        
        sigfilename = filename + '.sig'
        
        try:
            dummy = open(sigfilename)
            dummy.close()
        except IOError:
            # Signature file does not exist
            return False
        
        # Check if the sig is valid for the sigfile
        return verify(sigfilename, filename)

    def enter_save_mode(self):
        """Enters save mode"""
        
        self.code_array.safe_mode = True

    def leave_save_mode(self):
        """Leaves save mode"""
        
        self.code_array.safe_mode = False
        
    def approve(self, filepath):
        """Sets safe mode if signature missing of invalid"""
        
        if self.validate_signature(filepath):
            self.leave_save_mode()
            post_command_event(self.main_window, SaveModeExitMsg)
            
            statustext = "Valid signature found. File is trusted."
            post_command_event(self.main_window, StatusBarMsg, text=statustext)
            
        else:
            self.enter_save_mode()
            post_command_event(self.main_window, SaveModeEntryMsg)
            
            statustext = "File is not properly signed. Safe mode " + \
                         "activated. Select File -> Approve to leave safe mode."
            post_command_event(self.main_window, StatusBarMsg, text=statustext)

    def open(self, event):
        """Opens a file that is specified in event.attr
        
        Parameters
        ----------
        event.attr: Dict
        \tkey filepath contains file path of file to be loaded
        \tkey interface contains interface class for loading file
        
        """
        
        interface = event.attr["interface"]()
        filepath = event.attr["filepath"]
        
        try:
            interface.open(filepath)
            
        except IOError:
            statustext = "Error opening file " + filepath + "."
            post_command_event(self.main_window, StatusBarMsg, text=statustext)
            
            return False
        
        # Make loading safe
        self.approve(filepath)
        
        # Get cell values
        try:
            self.grid.code_array.dict_grid = interface.get_values()
            
        except IOError:
            statustext = "Error opening file " + filepath + "."
            post_command_event(self.main_window, StatusBarMsg, text=statustext)
            
            return False
        
        interface.close()
        
        _grid_table = GridTable(self.grid, self.grid.code_array)
        self.grid.SetTable(_grid_table, True)
    
    def sign_file(self, filepath):
        """Signs file if possible"""
        
        if is_pyme_present() and not self.main_window.safe_mode:
            signature = sign(filepath)
            signfile = open(filepath + '.sig','wb')
            signfile.write(signature)
            signfile.close()
        else:
            msg = 'Cannot sign the file. Maybe PyMe is not installed.'
            short_msg = 'Cannot sign file!'
            self.main_window.interfaces.display_warning(msg, short_msg)

    
    def save(self, event):
        """Saves a file that is specified in event.attr
        
        Parameters
        ----------
        event.attr: Dict
        \tkey filepath contains file path of file to be saved
        \tkey interface contains interface class for saving file
        
        """
        
        interface = event.attr["interface"]()
        filepath = event.attr["filepath"]
        
        interface.save(self.code_array.dict_grid, filepath)
        self.sign_file(filepath)


class TableRowActionsMixin(object):
    """Table row controller actions"""

    def set_row_height(self, row, height):
        """Sets row height"""
        
        tab = self.grid.current_table
        
        self.code_array.row_heights[(row, tab)] = height
        self.grid.SetRowSize(row, height)

    def insert_rows(self, row, no_rows=1):
        """Adds no_rows rows before row, appends if row > maxrows"""
        
        self.code_array.insert(row, no_rows, axis=0)

    def delete_rows(self, row, no_rows=1):
        """Deletes no_rows rows"""
        
        self.code_array.delete(row, no_rows, axis=0)


class TableColumnActionsMixin(object):
    """Table column controller actions"""

    def set_col_width(self, row, width):
        """Sets column width"""
        
        raise NotImplementedError

    def insert_cols(self, col, no_cols=1):
        """Adds no_cols columns before col, appends if col > maxcols"""
        
        self.code_array.insert(col, no_cols, axis=1)
        
    def delete_cols(self, col, no_cols=1):
        """Deletes no_cols column"""
        
        self.code_array.delete(col, no_cols, axis=1)


class TableTabActionsMixin(object):
    """Table tab controller actions"""

    def insert_tabs(self, tab, no_tabs=1):
        """Adds no_tabs tabs before table, appends if tab > maxtabs"""
        
        self.code_array.insert(tab, no_tabs, axis=2)

    def delete_tabs(self, tab, no_tabs=1):
        """Deletes no_tabs tabs"""
        
        self.code_array.delete(tab, no_tabs, axis=2)

class TableActions(TableRowActionsMixin, TableColumnActionsMixin, 
                   TableTabActionsMixin):
    """Table controller actions"""
    
    def __init__(self):
        
        # Action states
        
        self.pasting = False
        
        # Bindings
        
        self.main_window.Bind(wx.EVT_KEY_DOWN, self.on_key)
    
    def on_key(self, event):
        """Sets abort if pasting and if escape is pressed"""
        
        # If paste is running and Esc is pressed then we need to abort
        
        if self.pasting and event.GetKeyCode() == wx.WXK_ESCAPE:
            self.need_abort = True
        
        event.Skip()
    
    def _abort_paste(self, src_row):
        """Aborts import"""
        
        statustext = "Import aborted after importing " + \
                     str(src_row) + " rows."
        post_command_event(self.main_window, StatusBarMsg, 
                           text=statustext)
        
        self.pasting = False
        self.need_abort = False
    
    def _show_final_overflow_message(self, row_overflow, col_overflow):
        """Displays overflow message after import in statusbar"""
        
        if row_overflow and col_overflow:
            overflow_cause = "rows and columns"
        elif row_overflow:
            overflow_cause = "rows"
        elif col_overflow:
            overflow_cause = "columns"
        else:
            raise AssertionError, "Import cell overflow missing"
        
        statustext = "The imported data did not fit into the grid " + \
                     overflow_cause + ". It has been truncated. " + \
                     "Use a larger grid for full import."
        post_command_event(self.main_window, StatusBarMsg, text=statustext)
    
    def _show_paste_progress(self, src_row, abort_msg=False):
        """Shows progress in statusbar"""
        
        statustext = str(src_row) + " rows imported."
        if abort_msg:
            statustext += " Press <Esc> to abort."
        post_command_event(self.main_window, StatusBarMsg, text=statustext)
    
    def paste(self, tl_key, data):
        """Pastes data into grid table starting at top left cell tl_key
        
        Parameters
        ----------
        
        ul_key: Tuple
        \key of top left cell of paste area
        data: iterable of iterables where inner iterable returns string
        \tThe outer iterable represents rows
        
        """
        
        self.pasting = True
        
        set_cell_code = self.cell_actions.set_cell_code
        grid_rows, grid_cols, _ = self.grid.code_array.shape
        
        self.need_abort = False
        
        try:
            tl_row, tl_col, tl_tab = tl_key
        
        except ValueError:
            tl_row, tl_col = tl_key
            tl_tab = self.grid.current_table
        
        row_overflow = False
        col_overflow = False
        
        for src_row, col_data in enumerate(data):
            target_row = tl_row + src_row
            
            # Show progress in statusbar each 1000 rows
            
            if src_row % 1000 == 0:
                self._show_paste_progress(src_row, abort_msg=True)
                
                # Now wait for the statusbar update to be written on screen
                wx.Yield()
                
                # Abort if we have to
                if self.need_abort:
                    self._abort_paste(src_row)
                    return

            
            # Check if rows fit into grid
            if target_row > grid_rows:
                row_overflow = True
                break
            
            for src_col, cell_data in enumerate(col_data):
                target_col = tl_col + src_col
                
                if target_col > grid_cols:
                    col_overflow = True
                    break
                
                key = target_row, target_col, tl_tab
                
                set_cell_code(key, cell_data)
        
        if row_overflow or col_overflow:
            self._show_final_overflow_message(row_overflow, col_overflow)
        else:
            self._show_paste_progress(src_row)

        self.pasting = False

    def change_grid_shape(self, shape):
        """Grid shape change event handler"""
        
        self.grid.code_array.shape = shape

    
class MacroActions(object):
    """Macro controller actions"""
        
    def set_macros(selfself, macro_string):
        """Sets macro string"""
    
        raise NotImplementedError


class UnRedoActions(object):
    """Undo and redo operations"""
    
    def undo(self):
        """Calls undo in model.code_array.unredo"""
        
        self.code_array.unredo.undo()
        
    def redo(self):
        """Calls redo in model.code_array.unredo"""
        
        self.code_array.unredo.redo()


class GridActions(object):
    """Grid level grid actions"""
    
    def __init__(self):
        
        self.prev_rowcol = [] # Last mouse over cell
        
        self.main_window.Bind(EVT_COMMAND_GRID_ACTION_NEW, self.new)
        self.main_window.Bind(EVT_COMMAND_GRID_ACTION_TABLE_SWITCH, 
                              self.switch_to_table)
    
    def new(self, event):
        """Creates a new spreadsheet. Expects code_array in event."""
        
        # Grid table handles interaction to code_array
        self.grid.code_array.dict_grid = event.code_array.dict_grid
    
        _grid_table = GridTable(self.grid, self.grid.code_array)
        self.grid.SetTable(_grid_table, True)
    
    # Zoom actions
    
    def _zoom_rows(self, zoom):
        """Zooms grid rows"""
        
        self.grid.SetDefaultRowSize(self.grid.std_row_size * zoom, 
                                    resizeExistingRows=True)
        self.grid.SetRowLabelSize(self.grid.row_label_size * zoom)
        
        for row, tab in self.code_array.row_heights:
            if tab == self.grid.current_table:
                zoomed_row_size = self.code_array.row_heights[(row, tab)] * zoom
                self.grid.SetRowSize(row, zoomed_row_size)
    
    def _zoom_cols(self, zoom):
        """Zooms grid columns"""
        
        self.grid.SetDefaultColSize(self.grid.std_col_size * zoom, 
                                    resizeExistingCols=True)
        self.grid.SetColLabelSize(self.grid.col_label_size * zoom)
    
        for col, tab in self.code_array.col_widths:
            if tab == self.grid.current_table:
                zoomed_col_size = self.code_array.col_widths[(col, tab)] * zoom
                self.grid.SetColSize(col, zoomed_col_size)
    
    def _zoom_labels(self, zoom):
        """Adjust grid label font to zoom factor"""
        
        labelfont = self.grid.GetLabelFont()
        default_fontsize = default_cell_attributes["pointsize"]
        labelfont.SetPointSize(max(1, int(round(default_fontsize * zoom))))
        self.grid.SetLabelFont(labelfont)
    
    def zoom(self, zoom):
        """Zooms to zoom factor"""
        
        # Zoom factor for grid content
        self.grid.grid_renderer.zoom = zoom
        
        # Zoom grid labels
        self._zoom_labels(zoom)
        
        # Zoom rows and columns
        self._zoom_rows(zoom)
        self._zoom_cols(zoom)
        
        self.grid.ForceRefresh()
        
        statustext = u"Zoomed to {0:.2f}.".format(zoom)
            
        post_command_event(self.main_window, StatusBarMsg, text=statustext)
    
    def zoom_in(self):
        """Zooms in by ZOOM_FACTOR"""
        
        zoom = self.grid.grid_renderer.zoom
        
        target_zoom = zoom * (1 + ZOOM_FACTOR)
        
        if target_zoom < MAXIMUM_ZOOM:
            self.zoom(target_zoom)
        
    def zoom_out(self):
        """Zooms out by ZOOM_FACTOR"""
        
        zoom = self.grid.grid_renderer.zoom
        
        target_zoom = zoom * (1 - ZOOM_FACTOR)
        
        if target_zoom > MINIMUM_ZOOM:
            self.zoom(target_zoom)
    
    def on_mouse_over(self, key):
        """Displays cell code of cell key in status bar"""
        
        row, col, tab = key
        
        if (row, col) != self.prev_rowcol and row >= 0 and col >= 0:
            self.prev_rowcol[:] = [row, col]
            
            hinttext = self.grid.GetTable().GetSource(row, col, tab)
            
            if hinttext is None:
                hinttext = ''
            
            post_command_event(self.main_window, StatusBarMsg, text=hinttext)
    
    def get_visible_area(self):
        """Returns visible area
       
        Format is a tuple of the top left tuple and the lower right tuple
        
        """
        
        grid = self.grid
        
        top = grid.YToRow(grid.GetViewStart()[1] * grid.ScrollLineX)
        left = grid.XToCol(grid.GetViewStart()[0] * grid.ScrollLineY)
        
        # Now start at top left for determining the bottom right visible cell
        
        bottom, right = top, left 
        
        while grid.IsVisible(bottom, left, wholeCellVisible=False):
            bottom += 1
            
        while grid.IsVisible(top, right, wholeCellVisible=False):
            right += 1
            
        # The derived lower right cell is *NOT* visible
        
        bottom -= 1
        right -= 1
        
        return (top, left), (bottom, right)
    
    def switch_to_table(self, event):
        """Switches grid to table
        
        Parameters
        ----------
        
        event.newtable: Integer
        \tTable that the grid is switched to
        
        """
        
        newtable = event.newtable
        
        no_tabs = self.grid.code_array.shape[2]
        
        if 0 <= newtable <= no_tabs:
            self.grid.current_table = newtable
            
            ##self.grid.zoom_rows()
            ##self.grid.zoom_cols()
            ##self.grid.zoom_labels()
            
            ##post_entryline_text(self.grid, "")

    def get_cursor(self):
        """Returns current grid cursor cell (row, col, tab)"""
        
        return self.grid.GetGridCursorRow(), self.grid.GetGridCursorCol(), \
               self.grid.current_table

    def set_cursor(self, value):
        """Changes the grid cursor cell."""
        
        if len(value) == 3:
            row, col, tab = value
            
            if tab != self.cursor[2]:
                post_command_event(self.main_window, GridActionTableSwitchMsg, 
                                   newtable=tab)
        else:
            row, col = value
        
        if not (row is None and col is None):
            self.grid.MakeCellVisible(row, col)
            self.grid.SetGridCursor(row, col)
        
    cursor = property(get_cursor, set_cursor)
    

class SelectionActions(object):
    """Actions that affect the grid selection"""
    
    def get_selection(self):
        """Returns selected cells in grid as Selection object"""
        
        # GetSelectedCells: individual cells selected by ctrl-clicking
        # GetSelectedRows: rows selected by clicking on the labels
        # GetSelectedCols: cols selected by clicking on the labels
        # GetSelectionBlockTopLeft
        # GetSelectionBlockBottomRight: For blocks of cells selected by dragging
        # across the grid cells.
        
        block_top_left = self.grid.GetSelectionBlockTopLeft()
        block_bottom_right = self.grid.GetSelectionBlockBottomRight()
        rows = self.grid.GetSelectedRows()
        cols = self.grid.GetSelectedCols()
        cells = self.grid.GetSelectedCells()
        
        return Selection(block_top_left, block_bottom_right, rows, cols, cells)
    
    def select_cell(self, row, col, add_to_selected=False):
        self.grid.SelectBlock(row, col, row, col, addToSelected=add_to_selected)
    
    def select_slice(self, row_slc, col_slc, add_to_selected=False):
        """Selects a slice of cells
        
        Parameters
        ----------
         * row_slc: Integer or Slice
        \tRows to be selected
         * col_slc: Integer or Slice
        \tColumns to be selected
         * add_to_selected: Bool, defaults to False
        \tOld selections are cleared if False
        
        """
        
        if not add_to_selected:
            self.grid.ClearSelection()
        
        if row_slc == row_slc == slice(None, None, None):
            # The whole grid is selected
            self.grid.SelectAll()
            
        elif row_slc.stop is None and col_slc.stop is None:
            # A block is selcted:
            self.grid.SelectBlock(row_slc.start, col_slc.start, 
                                  row_slc.stop-1, col_slc.stop-1)
        else:
            for row in irange(row_slc.start, row_slc.stop, row_slc.step):
                for col in irange(col_slc.start, col_slc.stop, col_slc.step):
                    self.select_cell(row, col, add_to_selected=True)


class FindActions(object):
    """Actions for finding inside the grid"""
    
    def find(self, gridpos, find_string, flags):
        """Return next position of event_find_string in MainGrid
        
        Parameters:
        -----------
        gridpos: 3-tuple of Integer
        \tPosition at which the search starts
        find_string: String
        \tString to find in grid
        flags: Int
        \twx.wxEVT_COMMAND_FIND flags
        
        """
        
        findfunc = self.grid.code_array.findnextmatch
        
        if "DOWN" in flags:
            if gridpos[0] < self.grid.code_array.shape[0]:
                gridpos[0] += 1
            elif gridpos[1] < self.grid.code_array.shape[1]:
                gridpos[1] += 1
            elif gridpos[2] < self.grid.code_array.shape[2]:
                gridpos[2] += 1
            else:
                gridpos = (0, 0, 0)
        elif "UP" in flags:
            if gridpos[0] > 0:
                gridpos[0] -= 1
            elif gridpos[1] > 0:
                gridpos[1] -= 1
            elif gridpos[2] > 0:
                gridpos[2] -= 1
            else:
                gridpos = [dim - 1 for dim in self.grid.code_array.shape]
        
        return findfunc(tuple(gridpos), find_string, flags)
        
    def replace(self):
        raise NotImplementedError


class AllGridActions(FileActions, TableActions, MacroActions, UnRedoActions, 
                     GridActions, SelectionActions, FindActions):
    """All grid actions as a bundle"""
    
    def __init__(self, grid, code_array):
        self.main_window = grid.main_window
        self.grid = grid
        self.code_array = code_array
        
        self.attribute_actions = AttributeActions(grid, code_array)
        self.cell_actions = CellActions(grid, code_array)
        
        FileActions.__init__(self)
        TableActions.__init__(self)
        MacroActions.__init__(self)
        UnRedoActions.__init__(self)
        GridActions.__init__(self)
        SelectionActions.__init__(self)
        FindActions.__init__(self)
