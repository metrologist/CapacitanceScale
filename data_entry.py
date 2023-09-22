import wx
from guibasic import EXAMPLE
from dial_read import READOUT
import time
import csv


class ENTRY(EXAMPLE):
    def __init__(self, *args, **kwargs):
        super(ENTRY, self).__init__(*args, **kwargs)
        pattern_ivd_a = {'number': 7, 'input_style': 'eleven_step', 'sign': True}
        pattern_ivd_b = {'number': 7, 'input_style': 'eleven_step', 'sign': True}
        self.readout_alpha = READOUT(pattern_ivd_a)
        self.readout_beta = READOUT(pattern_ivd_b)

    def on_enter_alpha(self, e):
        row = -1  # default so that time will not be set if a row is not defined
        alpha_string = self.enter_alpha.GetLineText(0)  # only using line 0, enter triggers event
        alpha = list(alpha_string)  # convert string to list
        for i in range(len(alpha)):
            if alpha[i] == 'x':
                alpha[i] = 'X'  # always return capital X
        alpha_string = ''  # now rebuild the string
        for x in alpha:
            alpha_string = alpha_string + x
        reading = self.readout_alpha.input_by_string(alpha_string)
        if reading[1]:
            count = 0
            for x in reading[0]:
                self.dial_box_alpha[count].SetBackgroundColour((205, 255, 204))
                self.dial_box_alpha[count].SetValue(x)
                count = count + 1
            converted = self.readout_alpha.convert_input(reading[0])
            # self.result_box.SetValue(str(converted))
            row = self.spinControl.GetValue() - 1
            self.data_grid.SetCellValue(row, 2, str(converted))
            self.data_grid.SetCellValue(row, 0, alpha_string)
        else:
            count = 0
            for x in range(7):  #reading[0]:
                self.dial_box_alpha[count].SetValue('_')
                self.dial_box_alpha[count].SetBackgroundColour((255, 51, 51))
                count = count + 1
        now = self.get_time()
        if row >= 0:
            self.data_grid.SetCellValue(row, 5, now)

    def on_enter_beta(self, e):
        beta_string = self.enter_beta.GetLineText(0)  # only using line 0, enter triggers event
        beta = list(beta_string)  # convert string to list
        for i in range(len(beta)):
            if beta[i] == 'x':
                beta[i] = 'X'  # always return capital X
        beta_string = ''  # now rebuild the string
        for x in beta:
            beta_string = beta_string + x
        reading = self.readout_beta.input_by_string(beta_string)
        if reading[1]:
            count = 0
            for x in reading[0]:
                self.dial_box_beta[count].SetBackgroundColour((205, 255, 204))
                self.dial_box_beta[count].SetValue(x)
                count = count + 1
            converted = self.readout_beta.convert_input(reading[0])
            # self.result_box.SetValue(str(self.readout_beta.convert_input(reading[0])))
            row = self.spinControl.GetValue() - 1
            self.data_grid.SetCellValue(row, 3, str(converted))
            self.data_grid.SetCellValue(row, 1, beta_string)
        else:
            count = 0
            for x in reading[0]:
                self.dial_box_beta[count].SetValue('_')
                self.dial_box_beta[count].SetBackgroundColour((255, 51, 51))
                count = count + 1

    def on_enter_comment(self, e):
        comment = self.comment_box.GetLineText(0)
        row = self.spinControl.GetValue() - 1
        self.data_grid.SetCellValue(row, 4, comment)

    def get_time(self):
        now = time.localtime()  # structured local time
        now_string = time.strftime("%H:%M:%S, %d/%m/%Y", now)
        return now_string

    def OnOpen(self, e):
        with wx.FileDialog(self, "Open XYZ file", wildcard="XYZ files (*.xyz)|*.xyz",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'r') as file:
                    data = self.doLoadDataOrWhatever(pathname)
                    self.load_wx_data(data)
            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)

    def doLoadDataOrWhatever(self, file):
        pass

    def OnSave(self, e):
        with wx.FileDialog(self, "Save XYZ file", wildcard="XYZ files (*.xyz)|*.xyz",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'w') as file:
                    self.doSaveData(pathname)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)

    def doSaveData(self, file):
        data = self.get_wx_data()
        with open(file, 'w', newline='') as csvfile:
            out_writer = csv.writer(csvfile)
            for x in data:
                out_writer.writerow(x)

    def get_wx_data(self):
        data = []  # squeeze everything into a list of lists
        # first the grid
        cols = self.data_grid.GetNumberCols()
        rows = self.data_grid.GetNumberRows()
        for i in range(rows):
            byrow = []  # each item in data is a list holding the row data
            for j in range(cols):
                byrow.append(self.data_grid.GetCellValue(i, j))
            data.append(byrow)
        # then the free text
        no_lines = self.freetext.GetNumberOfLines()
        text = []
        for i in range(no_lines):
            text.append(self.freetext.GetLineText(i))
        data.append(text)
        return data

    def load_wx_data(self, data):
        # inserts a list of lists back into the gui
        for i in range(12):
            for j in range(6):
                self.data_grid.SetCellValue(i, j, data[i][j])
        for x in data[i + 1]:  # this should be the free text
            self.freetext.WriteText(x)
            self.freetext.WriteText('\n')

    def doLoadDataOrWhatever(self, file):
        data = []
        with open(file, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            for row in reader:
                data.append(row)
        return data  # should be the reconstituted data list

def main():
    app = wx.App()
    ex = ENTRY(None, title='Permutable capacitor')
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
