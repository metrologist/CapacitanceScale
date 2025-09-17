# cap_fit.py uses historical data to predict a future value
import csv
from json import loads
from msl.nlf import Model
from dict_test import FUNCDICTL
import numpy as np
from matplotlib import pyplot as plt

class CAPFIT():
    def load_file(self):
        """

        generic conversion of csv into a list of rows
        :param file_name:
        :return: a list of dictionaries
        """
        block = []
        with open('analysis_dict.csv', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                block.append(loads(row[0]))  # note the [0] to get a json compatible string to load as dictionary
        return block

    def fitting(self, selected_dict):  # starting with PRIMCAL version
        """

        Least-squares fit of the capacitance values to the selected function
        :return:
        """
        fn_set = FUNCDICTL()
        equation = fn_set.f_dict['func1']  # FUNCDICT version
        model = Model(equation['nlf'])  # FUNCDICTL version
        cap_values = []
        time_axis = []
        for val in selected_dict['std_ppm']:
            cap_values.append(val[1])
            time_axis.append(val[0])
        # result = self.model.fit(self.time_axis, cap_values, params=[0, 0])  # how do I automatically know the number of parameters?
        result = model.fit(time_axis, cap_values, params=equation['param'])  # FUNCDICT version
        gtc_real_fit = result.to_ureal()  # fit coefficients as gtc ureals
        chisq = result.chisq

        pltfn = []
        pltfn_plus_u = []
        pltfn_minus_u = []

        overshoot = 12 / 365  # add 1 month to each end
        step = 12 / 365  # plot the fit roughly by month
        max_date = max(time_axis) + overshoot
        min_date  = min(time_axis) - overshoot
        plt_x = np.arange(min_date, max_date, step)
        for d in plt_x:
            val = equation['fn'](gtc_real_fit, d)  # FUNCDICTL version
            pltfn.append(val.x)
            pltfn_plus_u.append(val.x + val.u)
            pltfn_minus_u.append(val.x - val.u)
        cap = []
        cap_u = []
        for x in selected_dict['std_ppm']:
            cap.append(x[1])
            cap_u.append(x[2])

        y2 = pltfn
        y3 = pltfn_plus_u
        y4 = pltfn_minus_u
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(plt_x, y2)
        ax.plot(plt_x, y3, 'g', linestyle='dashed')
        ax.plot(plt_x, y4, 'g', linestyle='dashed')
        ax.errorbar(time_axis, cap, yerr=cap_u, linestyle="None", fmt='o', capsize=10)
        plt.title(selected_dict['name'])
        plt.show()
        plt.close(fig)

if __name__ == '__main__':
    c =CAPFIT()
    dict_list = c.load_file()  # extract dictionaries
    index = 7  # will want to request by name
    print(dict_list[index]['name'])
    c.fitting(dict_list[index])


