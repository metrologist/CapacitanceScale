import wx
from guibasic import EXAMPLE
from dial_read import READOUT


class ENTRY(EXAMPLE):
    def __init__(self, *args, **kwargs):
        super(ENTRY, self).__init__(*args, **kwargs)
        pattern_ivd_a = {'number': 6, 'input_style': 'twelve_step', 'sign': False}
        pattern_ivd_b = {'number': 7, 'input_style': 'twelve_step', 'sign': False}
        self.readout_alpha = READOUT(pattern_ivd_a)
        self.readout_beta = READOUT(pattern_ivd_b)

    def on_enter_alpha(self, e):
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
            for x in reading[0]:
                self.dial_box_alpha[count].SetValue('_')
                self.dial_box_alpha[count].SetBackgroundColour((255, 51, 51))
                count = count + 1

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
        print(comment)
        self.data_grid.SetCellValue(row, 4, comment)


def main():
    app = wx.App()
    ex = ENTRY(None, title='Data entry from Universal Bridge')
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
