#!/usr/bin/python3
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

"""


pyspread
========

- Main Python spreadsheet application
- Run this script to start the application.

**Provides**

* MainApplication: Initial command line operations and application launch
* :class:`MainWindow`: Main windows class


"""

import os
import sys

from PyQt5.QtCore import Qt, pyqtSignal, QEvent, QTimer, QRectF
from PyQt5.QtWidgets import QMainWindow, QApplication, QSplitter, QMessageBox
from PyQt5.QtWidgets import QDockWidget, QUndoStack, QStyleOptionViewItem
try:
    from PyQt5.QtSvg import QSvgWidget
except ModuleNotFoundError:
    QSvgWidget = None
from PyQt5.QtGui import QColor, QFont, QPalette, QPainter, QBrush, QPen
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

from src import VERSION, APP_NAME
from src.cli import ArgumentParser
from src.settings import Settings
from src.icons import Icon, IconPath
from src.grid import Grid
from src.entryline import Entryline
from src.menus import MenuBar
from src.toolbar import MainToolBar, FindToolbar, FormatToolbar, MacroToolbar
from src.actions import MainWindowActions
from src.workflows import Workflows
from src.widgets import Widgets
from src.dialogs import ApproveWarningDialog, PreferencesDialog, ManualDialog
from src.dialogs import TutorialDialog, PrintAreaDialog, PrintPreviewDialog
from src.installer import DependenciesDialog
from src.panels import MacroPanel
from src.lib.hashing import genkey


LICENSE = "GNU GENERAL PUBLIC LICENSE Version 3"

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


class MainWindow(QMainWindow):
    """Pyspread main window

    :application: QApplication
    :args: Command line arguments object from argparse
    :unit_test: If True then the application runs in unit_test mode
    :type unit_test: bool, defaults to False

    """

    gui_update = pyqtSignal(dict)

    def __init__(self, application, args, unit_test=False):
        super().__init__()

        self._loading = True
        self.application = application
        self.unit_test = unit_test

        self.settings = Settings(self)
        self.workflows = Workflows(self)
        self.undo_stack = QUndoStack(self)
        self.refresh_timer = QTimer()

        self._init_widgets()

        self.main_window_actions = MainWindowActions(self)

        self._init_window()
        self._init_toolbars()

        self.settings.restore()
        if self.settings.signature_key is None:
            self.settings.signature_key = genkey()

        # Update recent files in the file menu
        self.menuBar().file_menu.history_submenu.update()

        if not self.unit_test:
            self.show()

        self._update_action_toggles()

        # Update the GUI so that everything matches the model
        cell_attributes = self.grid.model.code_array.cell_attributes
        attributes = cell_attributes[self.grid.current]
        self.on_gui_update(attributes)

        self._loading = False
        self._previous_window_state = self.windowState()

        # Open initial file if provided by the command line
        if args.file is not None:
            if self.workflows.filepath_open(args.file):
                self.workflows.update_main_window_title()
            else:
                msg = "File '{}' could not be opened.".format(args.file)
                self.statusBar().showMessage(msg)

    def _init_window(self):
        """Initialize main window components"""

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(Icon.pyspread)

        self.safe_mode_widget = QSvgWidget(str(IconPath.warning), self)
        msg = "%s is in safe mode.\nExpressions are not evaluated." % APP_NAME
        self.safe_mode_widget.setToolTip(msg)
        self.statusBar().addPermanentWidget(self.safe_mode_widget)
        self.safe_mode_widget.hide()

        # Disable the approve fiel menu button
        self.main_window_actions.approve.setEnabled(False)

        self.setMenuBar(MenuBar(self))

    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)
        if self._loading:
            return

    def closeEvent(self, event=None):
        """Overloaded close event, allows saving changes or canceling close"""

        if event:
            event.ignore()
        self.workflows.file_quit()  # has @handle_changed_since_save decorator

    def _init_widgets(self):
        """Initialize widgets"""

        self.widgets = Widgets(self)

        self.entry_line = Entryline(self)
        self.grid = Grid(self)

        self.macro_panel = MacroPanel(self, self.grid.model.code_array)

        self.main_splitter = QSplitter(Qt.Vertical, self)
        self.setCentralWidget(self.main_splitter)

        self.main_splitter.addWidget(self.entry_line)
        self.main_splitter.addWidget(self.grid)
        self.main_splitter.addWidget(self.grid.table_choice)
        self.main_splitter.setSizes([self.entry_line.minimumHeight(),
                                     9999, 20])

        self.macro_dock = QDockWidget("Macros", self)
        self.macro_dock.setObjectName("Macro Panel")
        self.macro_dock.setWidget(self.macro_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, self.macro_dock)

        self.macro_dock.installEventFilter(self)

        self.gui_update.connect(self.on_gui_update)
        self.refresh_timer.timeout.connect(self.on_refresh_timer)

    def eventFilter(self, source, event):
        """Event filter for handling QDockWidget close events

        Updates the menu if the macro panel is closed.

        """

        if event.type() == QEvent.Close \
           and isinstance(source, QDockWidget) \
           and source.windowTitle() == "Macros":
            self.main_window_actions.toggle_macro_panel.setChecked(False)
        return super().eventFilter(source, event)

    def _init_toolbars(self):
        """Initialize the main window toolbars"""

        self.main_toolbar = MainToolBar(self)
        self.macro_toolbar = MacroToolbar(self)
        self.find_toolbar = FindToolbar(self)
        self.format_toolbar = FormatToolbar(self)

        self.addToolBar(self.main_toolbar)
        self.addToolBar(self.macro_toolbar)
        self.addToolBar(self.find_toolbar)
        self.addToolBarBreak()
        self.addToolBar(self.format_toolbar)

    def _update_action_toggles(self):
        """Updates the toggle menu check states"""

        self.main_window_actions.toggle_main_toolbar.setChecked(
                self.main_toolbar.isVisible())

        self.main_window_actions.toggle_macro_toolbar.setChecked(
                self.macro_toolbar.isVisible())

        self.main_window_actions.toggle_format_toolbar.setChecked(
                self.format_toolbar.isVisible())

        self.main_window_actions.toggle_find_toolbar.setChecked(
                self.find_toolbar.isVisible())

        self.main_window_actions.toggle_entry_line.setChecked(
                self.entry_line.isVisible())

        self.main_window_actions.toggle_macro_panel.setChecked(
                self.macro_dock.isVisible())

    @property
    def safe_mode(self):
        """Returns safe_mode state. In safe_mode cells are not evaluated."""

        return self.grid.model.code_array.safe_mode

    @safe_mode.setter
    def safe_mode(self, value):
        """Sets safe mode.

        This triggers the safe_mode icon in the statusbar.

        If safe_mode changes from True to False then caches are cleared and
        macros are executed.

        """

        if self.grid.model.code_array.safe_mode == bool(value):
            return

        self.grid.model.code_array.safe_mode = bool(value)

        if value:  # Safe mode entered
            self.safe_mode_widget.show()
            # Enable approval menu entry
            self.main_window_actions.approve.setEnabled(True)
        else:  # Safe_mode disabled
            self.safe_mode_widget.hide()
            # Disable approval menu entry
            self.main_window_actions.approve.setEnabled(False)
            # Clear result cache
            self.grid.model.code_array.result_cache.clear()
            # Execute macros
            self.macro_panel.on_apply()

    def on_print(self):
        """Print event handler"""

        # Create printer
        printer = QPrinter(mode=QPrinter.HighResolution)

        # Get print area
        self.print_area = PrintAreaDialog(self, self.grid).area
        if self.print_area is None:
            return

        # Create print dialog
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            self.on_paint_request(printer)

    def on_preview(self):
        """Print preview event handler"""

        # Create printer
        printer = QPrinter(mode=QPrinter.HighResolution)

        # Get print area
        self.print_area = PrintAreaDialog(self, self.grid).area
        if self.print_area is None:
            return

        # Create print preview dialog
        dialog = PrintPreviewDialog(printer)

        dialog.paintRequested.connect(self.on_paint_request)
        dialog.exec_()

    def on_paint_request(self, printer):
        """Paints to printer"""

        painter = QPainter(printer)
        option = QStyleOptionViewItem()
        painter.setRenderHints(QPainter.SmoothPixmapTransform
                               | QPainter.SmoothPixmapTransform)

        page_rect = printer.pageRect()

        rows = list(self.workflows.get_paint_rows(self.print_area))
        columns = list(self.workflows.get_paint_columns(self.print_area))
        if not rows or not columns:
            return

        zeroidx = self.grid.model.index(0, 0)
        zeroidx_rect = self.grid.visualRect(zeroidx)

        minidx = self.grid.model.index(min(rows), min(columns))
        minidx_rect = self.grid.visualRect(minidx)

        maxidx = self.grid.model.index(max(rows), max(columns))
        maxidx_rect = self.grid.visualRect(maxidx)

        grid_width = maxidx_rect.x() + maxidx_rect.width() - minidx_rect.x()
        grid_height = maxidx_rect.y() + maxidx_rect.height() - minidx_rect.y()
        grid_rect = QRectF(minidx_rect.x() - zeroidx_rect.x(),
                           minidx_rect.y() - zeroidx_rect.y(),
                           grid_width, grid_height)

        self.settings.print_zoom = min(page_rect.width() / grid_width,
                                       page_rect.height() / grid_height)

        with self.grid.delegate.painter_save(painter):
            painter.scale(self.settings.print_zoom, self.settings.print_zoom)

            # Translate so that the grid starts at upper left paper edge
            painter.translate(zeroidx_rect.x() - minidx_rect.x(),
                              zeroidx_rect.y() - minidx_rect.y())

            # Draw grid cells
            self.workflows.paint(painter, option, grid_rect, rows, columns)

            painter.setPen(QPen(QBrush(Qt.gray), 2))
            painter.drawRect(grid_rect)

        self.settings.print_zoom = None

    def on_fullscreen(self):
        """Fullscreen toggle event handler"""

        if self.windowState() == Qt.WindowFullScreen:
            self.setWindowState(self._previous_window_state)
        else:
            self._previous_window_state = self.windowState()
            self.setWindowState(Qt.WindowFullScreen)

    def on_approve(self):
        """Approve event handler"""

        if ApproveWarningDialog(self).choice:
            self.safe_mode = False

    def on_clear_globals(self):
        """Clear globals event handler"""

        self.grid.model.code_array.result_cache.clear()

        # Clear globals
        self.grid.model.code_array.clear_globals()
        self.grid.model.code_array.reload_modules()

    def on_preferences(self):
        """Preferences event handler (:class:`dialogs.PreferencesDialog`) """

        data = PreferencesDialog(self).data

        if data is not None:
            max_file_history_changed = \
                self.settings.max_file_history != data['max_file_history']

            # Dialog has been approved --> Store data to settings
            for key in data:
                if key == "signature_key" and not data[key]:
                    data[key] = genkey()
                self.settings.__setattr__(key, data[key])

            # Immediately adjust file history in menu
            if max_file_history_changed:
                self.menuBar().file_menu.history_submenu.update()

    def on_dependencies(self):
        """Dependancies installer (:class:`installer.InstallerDialog`) """

        dial = DependenciesDialog(self)
        dial.exec_()

    def on_undo(self):
        """Undo event handler"""

        self.undo_stack.undo()

    def on_redo(self):
        """Undo event handler"""

        self.undo_stack.redo()

    def on_toggle_refresh_timer(self, toggled):
        """Toggles periodic timer for frozen cells"""

        if toggled:
            self.refresh_timer.start(self.settings.refresh_timeout)
        else:
            self.refresh_timer.stop()

    def on_refresh_timer(self):
        """Event handler for self.refresh_timer.timeout

        Called for periodic updates of frozen cells.
        Does nothing if either the entry_line or a cell editor is active.

        """

        if not self.entry_line.hasFocus() \
           and self.grid.state() != self.grid.EditingState:
            self.grid.refresh_frozen_cells()

    def _toggle_widget(self, widget, action_name, toggled):
        """Toggles widget visibility and updates toggle actions"""

        if toggled:
            widget.show()
        else:
            widget.hide()

        self.main_window_actions[action_name].setChecked(widget.isVisible())

    def on_toggle_main_toolbar(self, toggled):
        """Main toolbar toggle event handler"""

        self._toggle_widget(self.main_toolbar, "toggle_main_toolbar", toggled)

    def on_toggle_macro_toolbar(self, toggled):
        """Macro toolbar toggle event handler"""

        self._toggle_widget(self.macro_toolbar, "toggle_macro_toolbar",
                            toggled)

    def on_toggle_format_toolbar(self, toggled):
        """Format toolbar toggle event handler"""

        self._toggle_widget(self.format_toolbar, "toggle_format_toolbar",
                            toggled)

    def on_toggle_find_toolbar(self, toggled):
        """Find toolbar toggle event handler"""

        self._toggle_widget(self.find_toolbar, "toggle_find_toolbar", toggled)

    def on_toggle_entry_line(self, toggled):
        """Entryline toggle event handler"""

        self._toggle_widget(self.entry_line, "toggle_entry_line", toggled)

    def on_toggle_macro_panel(self, toggled):
        """Macro panel toggle event handler"""

        self._toggle_widget(self.macro_dock, "toggle_macro_panel", toggled)

    def on_manual(self):
        """Show manual browser"""

        dialog = ManualDialog(self)
        dialog.show()

    def on_tutorial(self):
        """Show tutorial browser"""

        dialog = TutorialDialog(self)
        dialog.show()

    def on_about(self):
        """Show about message box"""

        about_msg_template = "<p>".join((
            "<b>%s</b>" % APP_NAME,
            "A non-traditional Python spreadsheet application",
            "Version {version}",
            "Created by:<br>{devs}",
            "Documented by:<br>{doc_devs}",
            "Copyright:<br>Martin Manns",
            "License:<br>{license}",
            '<a href="https://pyspread.gitlab.io">pyspread.gitlab.io</a>',
            ))

        devs = "Martin Manns, Jason Sexauer<br>Vova Kolobok, mgunyho, " \
               "Pete Morgan"

        doc_devs = "Martin Manns, Bosko Markovic, Pete Morgan"

        about_msg = about_msg_template.format(
                    version=VERSION, license=LICENSE,
                    devs=devs, doc_devs=doc_devs)
        QMessageBox.about(self, "About %s" % APP_NAME, about_msg)

    def on_gui_update(self, attributes):
        """GUI update event handler.

        Emitted on cell change. Attributes contains current cell_attributes.

        """

        widgets = self.widgets
        menubar = self.menuBar()

        is_bold = attributes["fontweight"] == QFont.Bold
        self.main_window_actions.bold.setChecked(is_bold)

        is_italic = attributes["fontstyle"] == QFont.StyleItalic
        self.main_window_actions.italics.setChecked(is_italic)

        underline_action = self.main_window_actions.underline
        underline_action.setChecked(attributes["underline"])

        strikethrough_action = self.main_window_actions.strikethrough
        strikethrough_action.setChecked(attributes["strikethrough"])

        renderer = attributes["renderer"]
        widgets.renderer_button.set_current_action(renderer)
        widgets.renderer_button.set_menu_checked(renderer)

        freeze_action = self.main_window_actions.freeze_cell
        freeze_action.setChecked(attributes["frozen"])

        lock_action = self.main_window_actions.lock_cell
        lock_action.setChecked(attributes["locked"])
        self.entry_line.setReadOnly(attributes["locked"])

        button_action = self.main_window_actions.button_cell
        button_action.setChecked(attributes["button_cell"] is not False)

        rotation = "rotate_{angle}".format(angle=int(attributes["angle"]))
        widgets.rotate_button.set_current_action(rotation)
        widgets.rotate_button.set_menu_checked(rotation)
        widgets.justify_button.set_current_action(attributes["justification"])
        widgets.justify_button.set_menu_checked(attributes["justification"])
        widgets.align_button.set_current_action(attributes["vertical_align"])
        widgets.align_button.set_menu_checked(attributes["vertical_align"])

        border_action = self.main_window_actions.border_group.checkedAction()
        if border_action is not None:
            icon = border_action.icon()
            menubar.format_menu.border_submenu.setIcon(icon)
            self.format_toolbar.border_menu_button.setIcon(icon)

        border_width_action = \
            self.main_window_actions.border_width_group.checkedAction()
        if border_width_action is not None:
            icon = border_width_action.icon()
            menubar.format_menu.line_width_submenu.setIcon(icon)
            self.format_toolbar.line_width_button.setIcon(icon)

        if attributes["textcolor"] is None:
            text_color = self.grid.palette().color(QPalette.Text)
        else:
            text_color = QColor(*attributes["textcolor"])
        widgets.text_color_button.color = text_color

        if attributes["bgcolor"] is None:
            bgcolor = self.grid.palette().color(QPalette.Base)
        else:
            bgcolor = QColor(*attributes["bgcolor"])
        widgets.background_color_button.color = bgcolor

        if attributes["textfont"] is None:
            widgets.font_combo.font = QFont().family()
        else:
            widgets.font_combo.font = attributes["textfont"]
        widgets.font_size_combo.size = attributes["pointsize"]

        merge_cells_action = self.main_window_actions.merge_cells
        merge_cells_action.setChecked(attributes["merge_area"] is not None)


def main():
    parser = ArgumentParser()
    args = parser.parse_args()

    app = QApplication(sys.argv)
    main_window = MainWindow(app, args)

    app.exec_()


if __name__ == '__main__':
    main()
