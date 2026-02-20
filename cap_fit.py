# cap_fit.py uses historical data to predict a future value
import csv
from json import loads
from msl.nlf import Model
from funcdictl import FUNCDICTL
import numpy as np
from matplotlib import pyplot as plt
import pickle
from intertime import INTERTIME
from GTC import reporting, ureal
from scipy.stats import chi2

class CAPFIT():
    def __init__(self, target_date):
        """


        :param target_date: string e.g. '19 July 2026'
        """
        self.target_date = target_date
        t = INTERTIME('Pacific/Auckland')
        seconds = t.date_to_sec(target_date)  # multistep just to use the methods that are already available
        time_date = t.sec_to_date(seconds)
        self.decimal_target = t.datetime_to_decimal_year(time_date)
        self.predictions = [['Date', 'Decimal Date', 'Name', 'ppm value', 'uncertainty', 'k' ]]  # a list of predicted values

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
        model.options(weighted=True)
        cap_values = []
        cap_u = []  # used with weighting
        time_axis = []
        # base_u = selected_dict['std_ppm'][0][2]  # build up uncertainty of first point
        # print('base_u =', base_u)
        for val in selected_dict['std_ppm']:
            cap_u.append(val[2])
            cap_values.append(val[1])
            time_axis.append(val[0])
        result = model.fit(time_axis, cap_values, params=equation['param'], uy=cap_u)
        gtc_real_fit = result.to_ureal()  # fit coefficients as gtc ureals
        chisq = result.chisq
        print('chisq =', chisq)
        dof = len(cap_values) - len(equation['param'])  # slope and intercept for now
        print('dof =', dof)

        # analyse the fit
        response = self.fit_qual(chisq, dof)
        print('response =', response)
        av_cal_u = 0  # default value if not needed
        if response == 'overly good fit, add calibration uncertainty' or response == 'good fit, no change to uncertainty':
            # need the average calibration uncertainty...likely all points are near equal u
            var_sum = 0
            count = 0
            for x in selected_dict['std_ppm']:
                var_sum += x[2] ** 2
                count += 1
            av_cal_u = np.sqrt(var_sum / count)  # a typical uncertainty for all the buildup results

        # organise the plot
        pltfn = []
        pltfn_plus_u = []
        pltfn_minus_u = []

        overshoot = 30 / 365  # add 1 month to each end
        step = 30 / 365  # plot the fit roughly by month
        max_date = max(time_axis) + 60 * overshoot  # adjust the 60 factor as desired
        min_date  = min(time_axis) - overshoot
        plt_x = np.arange(min_date, max_date, step)
        for d in plt_x:
            val = equation['fn'](gtc_real_fit, d)  # FUNCDICTL version
            pltfn.append(val.x)
            if response == 'overly good fit, add calibration uncertainty':
                temp_val = val + ureal(0, av_cal_u)  # adding minimum calibration uncertainty
                modified_u = temp_val.u

            elif response == 'bad fit, add scatter to fit uncertainty':
                modified_u = ((val.u * (chisq)**0.5))  # is a factor of root-chisq sensible?

            elif response == 'good fit, no change to uncertainty':
                # modified_u = val.u # i.e. not modified at all
                temp_val = val + ureal(0, av_cal_u)  # adding minimum calibration uncertainty
                modified_u = temp_val.u

            else:
                print('Problem with response from fit_qual')
                modified_u = 0  # this is so the graph will clearly be seen as wrong

            pltfn_plus_u.append(val.x + modified_u)
            pltfn_minus_u.append(val.x - modified_u)
        cap = []
        cap_u = []
        for x in selected_dict['std_ppm']:
            cap.append(x[1])
            cap_u.append(x[2])

        y2 = pltfn
        y3 = pltfn_plus_u
        y4 = pltfn_minus_u
        # fig = plt.figure()
        # ax = fig.add_subplot(1, 1, 1)
        fig,ax = plt.subplots()
        ax.plot(plt_x, y2)
        ax.plot(plt_x, y3, 'g', linestyle='dashed')
        ax.plot(plt_x, y4, 'g', linestyle='dashed')
        ax.errorbar(time_axis, cap, yerr=cap_u, linestyle="None", fmt='o', capsize=10)
        plt.title(selected_dict['name'])
        plt.show()
        with open(r'graphs/' + selected_dict['name'] + '.pkl', 'wb') as f:  # for view.py
            pickle.dump(fig, f)
        plt.savefig(r'graphs/' + selected_dict['name'] + '.jpg')
        plt.pause(2)
        plt.close()

        value_at_date = equation['fn'](gtc_real_fit, self.decimal_target)
        if response == 'overly good fit, add calibration uncertainty':
            temp_val = value_at_date + ureal(0, av_cal_u)  # adding minimum calibration uncertainty
            modified_u = temp_val.u

        elif response == 'bad fit, add scatter to fit uncertainty':
            modified_u = ((value_at_date.u * (chisq) ** 0.5))  # is a factor of root-chisq sensible?

        elif response == 'good fit, no change to uncertainty':
            modified_u = value_at_date.u  # i.e. not modified at all

        else:
            print('Problem with response from fit_qual')
            modified_u = 0  # this is so the graph will clearly be seen as wrong


        print(self.decimal_target, value_at_date.x, modified_u, reporting.k_factor(len(cap_values)))
        self.predictions.append([self.target_date, self.decimal_target, selected_dict['name'], value_at_date.x, modified_u, reporting.k_factor(len(cap_values))])

    def fit_qual(self,chisq, dof):
        """

        modified from MIEcalc3, functions.py
        Checks the chi-square of the fit and returns comments on the quality of the fit
        and whether the prediction uncertainty of the fit needs to be modified.
        The decision is based on the hard-coded value of 'prob', currently set at 0.1.

        If the chi-square has a probability of less than *prob* of being so
        small, then it is identified as an "overly good fit, add calibration uncertainty"

        If the chi-square has a probability of less than *prob* of being so
        large, then it is identified as a "bad fit, add scatter to fit uncertainty"

        If the chi-square is seen as likely (1-*prob*), then the fit is
        identified as a "good fit, no change to uncertainty".

        :param chisq: chisquare value from the fit (not reduced chi-square)
        :param dof: degrees of freedom, no. of points minus number of fitted coefficients
        :return: comment on quality of fit
        """
        prob = 0.1  # for now this is the trigger level determined to give acceptable long-run success
        fit_check = 1 - chi2.cdf(chisq, dof)
        if fit_check > 1 - prob:
            comment = 'overly good fit, add calibration uncertainty'
        elif fit_check < prob:  # a bad fit to data!
            comment = 'bad fit, add scatter to fit uncertainty'
        else:
            comment = 'good fit, no change to uncertainty'
        return comment

    def file_block(self, file_name, block):
        with open(file_name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for x in block:
                writer.writerow(x)

if __name__ == '__main__':
    date_for_prediction = '19 July 2030'
    c =CAPFIT(date_for_prediction)
    dict_list = c.load_file()  # extract dictionaries
    plt.ion()  # the interactive mode must be on for close() to work
    for index in range(len(dict_list)):
        print(dict_list[index]['name'])
        c.fitting(dict_list[index])
    print(c.predictions)
    c.file_block(r'Predicted/' + date_for_prediction + '.csv', c.predictions)



