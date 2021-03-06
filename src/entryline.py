# -*- coding: utf-8 -*-

# Copyright Martin Manns
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

from contextlib import contextmanager

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextOption

from src.commands import CommandSetCellCode
from src.lib.spelltextedit import SpellTextEdit


class Entryline(SpellTextEdit):
    """The entry line for pyspread"""

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        min_height = self.cursorRect().y() + self.cursorRect().height() + 20
        self.setMinimumHeight(min_height)

        self.setWordWrapMode(QTextOption.WrapAnywhere)

        # self.highlighter.setDocument(self.document())

    @contextmanager
    def disable_highlighter(self):
        """Disables highlighter"""

        doc = self.highlighter.document()
        self.highlighter.setDocument(None)
        yield
        self.highlighter.setDocument(doc)

    def keyPressEvent(self, event):
        """Key press event filter"""

        if event.key() in (Qt.Key_Enter, Qt.Key_Return) \
           and not event.modifiers() == Qt.ShiftModifier:
            self.store_data()
            self.main_window.grid.row += 1
        elif event.key() == Qt.Key_Tab:
            self.store_data()
            self.main_window.grid.column += 1
        else:
            super().keyPressEvent(event)

    def store_data(self):
        """Stores current entry line data in grid model"""

        index = self.main_window.grid.currentIndex()
        model = self.main_window.grid.model

        description = "Set code for cell {}".format(index)
        command = CommandSetCellCode(self.toPlainText(), model, index,
                                     description)
        self.main_window.undo_stack.push(command)

    def on_toggle_spell_check(self, signal):
        """Spell check toggle event handler"""

        self.highlighter.enable_enchant = True if signal else False

    def setPlainText(self, text):
        """Overides setPlainText

        Additionally shows busy cursor and disables highlighter on long texts,
        and omits identical replace.

        """

        is_long = (text is not None
                   and len(text) > self.main_window.settings.highlighter_limit)

        if text == self.toPlainText():
            return

        if is_long:
            with self.main_window.workflows.busy_cursor():
                self.highlighter.setDocument(None)
                super().setPlainText(text)
        else:
            super().setPlainText(text)
