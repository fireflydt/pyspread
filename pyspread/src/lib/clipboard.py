#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2011 Martin Manns
# Distributed under the terms of the GNU General Public License

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
clipboard
=========

Provides
--------

 * Clipboard: Clipboard interface class

"""

import wx

class Clipboard(object):
    """Clipboard access

    Provides:
    ---------
    get_clipboard: Get clipboard content
    set_clipboard: Set clipboard content
    grid_paste: Inserts data into grid target

    """

    clipboard = wx.TheClipboard

    def _convert_clipboard(self, datastring=None, sep='\t'):
        """Converts data string to iterable.

        Parameters:
        -----------
        datastring: string, defaults to None
        \tThe data string to be converted.
        \tself.get_clipboard() is called if set to None
        sep: string
        \tSeparator for columns in datastring

        """

        if datastring is None:
            datastring = self.get_clipboard()

        data_it = ((ele for ele in line.split(sep)) \
                            for line in datastring.splitlines())
        return data_it

    def get_clipboard(self):
        """Returns the clipboard text content"""

        textdata = wx.TextDataObject()
        if self.clipboard.Open():
            self.clipboard.GetData(textdata)
            self.clipboard.Close()
        else:
            wx.MessageBox("Can't open the clipboard", "Error")
        return textdata.GetText()

    def set_clipboard(self, data):
        """Writes data to the clipboard"""

        error_log = []

        textdata = wx.TextDataObject()
        try:
            textdata.SetText(data)
        except UnboundLocalError, err:
            error_log.append([err, "Error converting to string"])
        if self.clipboard.Open():
            self.clipboard.SetData(textdata)
            self.clipboard.Close()
        else:
            wx.MessageBox("Can't open the clipboard", "Error")
        return error_log

# end of class Clipboard