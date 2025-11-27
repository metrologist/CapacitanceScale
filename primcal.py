"""
primcal.py sets an expected time dependence of the set of four AH11 capacitors that were calibrated in 2009 at the
BIPM and in 2019 at NMI Australia. It is asserted that the chosen drift model is correct and all results are built on
this assertion. The assertion can be expected to be modified over time as more external calibration data becomes
available. Ultimately a local realisation of the farad will remove the need to assert a constraint.

Certificate values have been summarised in
root \\MSL - Electricity\\Ongoing\\Farad\\Traceability\\traceability_2021.xlsx
"""

from GTC import ureal
from matplotlib import pyplot as plt
import numpy as np
from datetime import datetime as dt
from dateutil import parser
import time
from msl.nlf import Model
from dict_test import FUNCDICTL


class PRIMCAL():
    def __init__(self, cap, coefficients, std_temperature, equation, label, nompF, weight=False):
        """

        :param cap: list of tuples in the form of (date, value, standard uncertainty)
        :param coefficients: for now just a temperature coefficient in ppm/degree
        :param std_temperature: arbitrary common chassis temperature for all the measurements
        :param equation: FUNCDICT a string compatible with msl.nlf, such as 'a1 + a2*x + a3*x^2', using Delphi conventions
        :param label: name of capacitor
        :param weight: boolean True if fit is to be weighted by the uncertainty
        :param nompF: nominal value in pF
        """

        self.label = label
        self.nompF = nompF
        #  convert cap into lists
        self.cap = cap
        self.meas_date = []
        self.cap_value = []
        self.meas_temp = []
        for x in cap:
            self.meas_date.append(x[0])
            self.cap_value.append(ureal(x[1][0], x[1][1], x[1][2]))
            self.meas_temp.append(x[1][3])
        self.coefficients = coefficients  # ppm/degree
        self.std_temperature = std_temperature
        self.equation = equation  # could be FUNCDICT instead of a string
        self.cap_corrected = self.temp_corrected()  # capacitance values corrected to std_temperature
        self.model = Model(self.equation['nlf'])  # FUNCDICTL version
        self.time_axis = self.decimal_time_axis()
        self.gtcfit = 'NA'  # only available after fitting
        self.chisq = 'NA'  # only available after fitting
        try:  # consider how to report poor/failed fits
            self.gtcfit, self.chisq = self.fitting(weight=weight)  # will default to False if not set for the class
        except:
            print('fitting process failed')
        self.pltfn = []  # the fit line
        self.pltfn_plus_u = []  # fit plus standard uncertainty
        self.pltfn_minus_u = []  # fit minus standard uncertainty
        self.plt_x = 0  # will be an array of decimal dates
        self.plotable()  # prepare data for plotting

    def temp_corrected(self):
        """
        Apply temperature corrections so that all values are at the common standard temperature
        :return: list of the corrected capacitance values
        """
        cap_corrected = []
        for i in range(len(self.cap)):
            corrected = self.cap_value[i] * (1 - (self.meas_temp[i] - self.std_temperature) * self.coefficients * 1e-6)
            cap_corrected.append(corrected)
        return cap_corrected  # these are ureals, but note that no correlation is assumed between them

    def decimal_date(self, date):
        """
        utility to convert a string date into a decimal year

        :param date: string formatted as 'Dec 25 1025'
        :return: decimal year
        """
        date = parser.parse(date)  # convert string to datetime object

        def since_epoch(date):  # returns seconds since epoch
            return time.mktime(date.timetuple())

        s = since_epoch
        year = date.year
        startOfThisYear = dt(year=year, month=1, day=1)
        startOfNextYear = dt(year=year + 1, month=1, day=1)
        yearElapsed = s(date) - s(startOfThisYear)
        yearDuration = s(startOfNextYear) - s(startOfThisYear)
        fraction = yearElapsed / yearDuration
        return date.year + fraction

    def decimal_time_axis(self):
        """

        fitting is done against the decimal date
        :return:
        """
        time_axis = []
        for x in self.meas_date:
            time_axis.append(self.decimal_date(x))  # fit against decimal date
        return time_axis

    def fitting(self, weight=False):
        """

        Least-squares fit of the capacitance values to the selected function that defaults to unweighted unless
        it is set to True.
        :param weight: True if weighting is used
        :return: the correlated gtc fit and chisq
        """

        cap_values = []
        cap_u = []  # only used if weight is True
        for c in self.cap_corrected:
            cap_values.append(c.x)  # not using the uncertainty information
            if weight:
                cap_u.append(c.u)
        if weight:
            self.model.options(weighted=True)
            result = self.model.fit(self.time_axis, cap_values, params=self.equation['param'], uy=cap_u)
        else:
            self.model.options(weighted=False)  # as this is in self it pays to be clear it is either True or False
            result = self.model.fit(self.time_axis, cap_values, params=self.equation['param'])
        gtc_real_fit = result.to_ureal()  # fit coefficients as gtc ureals
        chisq = result.chisq
        self.gtcfit = gtc_real_fit
        self.chisq = chisq
        return gtc_real_fit, chisq

    def plotable(self):
        """

        Creates lists suitable for plotting
        :return:
        """
        overshoot = 12 / 365  # add 1 month to each end
        step = 12 / 365  # plot the fit roughly by month
        max_date = max(self.time_axis) + overshoot
        min_date  = min(self.time_axis) - overshoot
        self.plt_x = np.arange(min_date, max_date, step)
        for d in self.plt_x:
            val = self.equation['fn'](self.gtcfit, d)  # FUNCDICTL version
            self.pltfn.append(val.x)
            self.pltfn_plus_u.append(val.x + val.u)
            self.pltfn_minus_u.append(val.x - val.u)
        self.cap = []
        self.cap_u = []
        for x in self.cap_corrected:
            self.cap.append(x.x)
            self.cap_u.append(x.u)

    def plotcap(self):  # simple plot of this capacitor
        """

        :return:
        """

        y2 = self.pltfn
        y3 = self.pltfn_plus_u
        y4 = self.pltfn_minus_u
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(self.plt_x, y2)
        ax.plot(self.plt_x, y3, 'g', linestyle='dashed')
        ax.plot(self.plt_x, y4, 'g', linestyle='dashed')
        ax.errorbar(self.time_axis, self.cap, yerr=self.cap_u, linestyle="None", fmt='o', capsize=10)
        plt.title(self.label)
        plt.show()




if __name__ == '__main__':
    # Input data
    # Start with AH11A1 with data from Electricity\Ongoing\Farad\LabShift\AH2700A checks KJ_GH.xlsx
    # Note the dummy Jul 20 values to give one degree of freedom
    fn_set = FUNCDICTL()
    std_temperature = 29

    cap1 = [('Mar 19 2009', (9.999950922, 0.000000400, 50, 31.4)),
            ('Jul 20 2019', (9.9999500, 0.000000550, 50, 27.0)),
            ('Jul 31 2025', (9.9999513, 0.00000070, 50, 27.75))  # weight most recent point?
            ]

    coefficient1 = 0.003086584

    # equation1 = 'a1 + a2 * x'
    equation1 = fn_set.f_dict['func1']  # FUNCDICT version

    cap2 = [('Mar 19 2009', (9.999953022, 0.000000400, 50, 31.4)),
            ('Jul 20 2019', (9.9999526, 0.000000550, 50, 27.0)),
            ('Jul 31 2025', (9.9999540, 0.00000070, 50, 27.75))
            ]

    coefficient2 = 0.004026581
    # equation2 = 'a1 + a2 * x'
    equation2 = fn_set.f_dict['func1']  # FUNCDICT version

    cap3 = [('Mar 19 2009', (99.999557221, 0.000004000, 50, 31.4)),
            ('Jul 20 2019', (99.999580, 0.000005500, 50, 27.0)),
            ('Jul 31 2025', (99.999564, 0.0000070, 50, 27.75))
            ]

    coefficient3 = -0.001883384
    # equation3 = 'a1 + a2 * x'
    equation3 = fn_set.f_dict['func1']  # FUNCDICT version

    cap4 = [('Mar 19 2009', (99.999548221, 0.000004000, 50, 31.4)),
            ('Jul 20 2019', (99.999567, 0.000005500, 50, 27.0)),
            ('Jul 31 2025', (99.999584, 0.0000070, 50, 27.75))
            ]

    coefficient4 = -0.003210803
    # equation4 = 'a1 + a2 * x'
    equation4 = fn_set.f_dict['func1']  # FUNCDICT version

    # Create instances of PRIMCAL
    # Can compare the weighted and unweigted fits
    # Altering the input uncertainties could be justified, e.g. stronger weighting on the most recent value
    ah11a1 = PRIMCAL(cap1, coefficient1, std_temperature, equation1, '#1 AH11A 10 pF', 10, weight=True)
    ah11a1.plotcap()
    ah11a1 = PRIMCAL(cap1, coefficient1, std_temperature, equation1, '#1 AH11A 10 pF', 10)
    ah11a1.plotcap()
    ah11b1 = PRIMCAL(cap2, coefficient2, std_temperature, equation2, '#1 AH11B 10 pF', 10, weight=True)
    ah11b1.plotcap()
    ah11b1 = PRIMCAL(cap2, coefficient2, std_temperature, equation2, '#1 AH11B 10 pF', 10)
    ah11b1.plotcap()
    ah11c1 = PRIMCAL(cap3, coefficient3, std_temperature, equation3, '#1 AH11C 100 pF', 100, weight=True)
    ah11c1.plotcap()
    ah11c1 = PRIMCAL(cap3, coefficient3, std_temperature, equation3, '#1 AH11C 100 pF', 100)
    ah11c1.plotcap()
    ah11d1 = PRIMCAL(cap1, coefficient4, std_temperature, equation4, '#1 AH11D 100 pF', 100, weight=True)
    ah11d1.plotcap()
    ah11d1 = PRIMCAL(cap1, coefficient4, std_temperature, equation4, '#1 AH11D 100 pF', 100)
    ah11d1.plotcap()
