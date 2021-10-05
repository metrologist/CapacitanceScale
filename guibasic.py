"""
guibasci.py is the beginning of enabling guid management of the capacitance scale and impedance projects.
Using https://zetcode.com/wxpython/firststeps/ as a memory jog
"""

import wx
from wx import grid as wxgrid

class EXAMPLE(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(EXAMPLE, self).__init__(*args, **kwargs)
        self.InitUI()

    def InitUI(self):
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fileItem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.OnQuit, fileItem)

        self.pnl = wx.Panel(self)
        self.alpha_heading = wx.StaticText(self.pnl, pos=(30, 50))
        self.alpha_heading.SetLabel('alpha dial')

        self.beta_heading = wx.StaticText(self.pnl, pos=(250, 50))
        self.beta_heading.SetLabel('beta dial')
        self.enter_alpha = wx.TextCtrl(self.pnl, size=(200, 30), style=wx.TE_MULTILINE | wx.wxEVT_TOOL_ENTER, pos=(30, 100))
        self.enter_alpha.Bind(wx.EVT_TEXT_ENTER, self.on_enter_alpha)
        self.enter_beta = wx.TextCtrl(self.pnl, size=(200, 30), style=wx.TE_MULTILINE | wx.wxEVT_TOOL_ENTER, pos=(250, 100))
        self.enter_beta.Bind(wx.EVT_TEXT_ENTER, self.on_enter_beta)

        dial_size = (30, 30)
        step_x = dial_size[0]
        n = 6  # number of alpha dials
        m = 7  # number of beta dials
        start_xy = (30, 150)
        self.dial_box_alpha = []
        for i in range(n):
            self.dial_box_alpha.append(
                wx.TextCtrl(self.pnl, size=dial_size, style=wx.TE_CENTRE, pos=(start_xy[0] + i * step_x, start_xy[1])))

        start_xy = (250, 150)
        self.dial_box_beta = []  # a list of TextCtrl
        for i in range(m):
            self.dial_box_beta.append(
                wx.TextCtrl(self.pnl, size=dial_size, style=wx.TE_CENTRE, pos=(start_xy[0] + i * step_x, start_xy[1])))

        for digit in self.dial_box_alpha:
            digit.SetEditable(False)
            digit.SetBackgroundColour((204, 255, 204))
        for digit in self.dial_box_beta:
            digit.SetEditable(False)
            digit.SetBackgroundColour((204, 255, 204))

        self.misc_input_heading = wx.StaticText(self.pnl, pos=(30,220))
        self.misc_input_heading.SetLabel('Header comment')

        self.comment_box = wx.TextCtrl(self.pnl, size=(400, 100), style=wx.TE_MULTILINE, pos=(30, 250))

        self.hint = wx.StaticText(self.pnl, pos=(500, 70))
        self.hint.SetLabel('select cell and then right click to set row number')

        self.data_grid = wxgrid.Grid(self.pnl, size=(450,300), pos=(500,100))
        rows = 12
        cols = 4
        self.data_grid.CreateGrid(rows, cols)
        colLabels = ['alpha', 'beta', 'alpha', 'beta']
        for col in range(4):
            self.data_grid.SetColLabelValue(col, colLabels[col])

        self.data_grid.Bind(wxgrid.EVT_GRID_CELL_RIGHT_CLICK, self.on_grid)
        for i in range(rows):
            for j in range(cols):
                self.data_grid.SetReadOnly(i, j)

        self.spinControl = wx.SpinCtrl(self.pnl, -1, '', (100, 10), style=wx.SP_WRAP | wx.SP_ARROW_KEYS )
        self.spinControl.SetRange(1, 12)
        self.spinControl.SetValue(1)
        self.spin_heading = wx.StaticText(self.pnl, pos=(20, 10))
        self.spin_heading.SetLabel('row number')


        self.SetSize((1000, 600))
        self.Centre()

    def on_enter_alpha(self, e):
        pass

    def on_enter_beta(self, e):
        pass

    def OnQuit(self, e):
        self.Close()

    def on_grid(self, e):
        """
        First select a cell and then right click to set the spin control to the same row number.
        :param e:
        :return:
        """
        self.spinControl.SetValue(self.data_grid.GetGridCursorRow() + 1)

def main():
    app = wx.App()
    ex = EXAMPLE(None, title='Dial entry from IVDs')
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()

