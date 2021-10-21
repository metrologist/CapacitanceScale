"""
constraint.py sets an expected time dependence of the set of four AH11 capacitors that were calibrated in 2009 at the
BIPM and in 2019 at NMI Australia. It is asserted that the chosen drift model is correct and all results are built on
this assertion. The assertion can be expected to be modified over time as more external calibration data becomes
available. Ultimately a local realisation of the farad will remove the need to assert a constraint.

Certificate values have been summarised in
G:\Shared drives\MSL - Electricity\Ongoing\Farad\Traceability\traceability_2021.xlsx
"""

from GTC import ureal
from matplotlib import pyplot as plt
import numpy as np
from datetime import datetime as dt
from dateutil import parser
import time

class CONSTRAINT(object):
    def __init__(self, date, cap):
        """
        Uses two calibration points to provide a straight line prediction of the mean of the relative values (ppm
        relative error) of all four AH11x1 capacitors.

        :param date: a list of two decimal year dates, first for the BIPM and second for the NMIA calibrations
        :param cap:  a list of two ureals, first the average relative error from BIPM and the second from NMIA
        """
        self.slope = (cap[1] - cap[0]) / (date[1] - date[0])
        self.intercept = cap[0] - self.slope * date[0]
        self.cal = [cap[0].x, cap[1].x]
        self.ecal = [cap[0].u, cap[1].u]

    def line(self, date):
        """
        Returns the straight line value for the date
        :param x: date as a decimal year, e.g. 2021.344
        :return: the ppm relative error of the average of all four AH11x1 capacitors as an uncertain real.
        """
        return self.slope * date + self.intercept

    def year_fraction(self, date):
        """
        utility to convert a datetime.datetime object into a decimal year

        :param date: datetime object
        :return: decimal year
        """
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

    def predicted(self, date):
        """
        Predicts the restraint value at a date given by a string, e.g. '27-Sep-2021'

        :param date: string that can be interpreted as a datetime object
        :return: predicted ureal value of restraint on the date
        """
        proper_date = parser.parse(date)
        decimal_date = self.year_fraction(proper_date)
        return self.line(decimal_date)


if __name__ == '__main__':
    t = [2009.21435, 2019.54757]  # decimal year of calibrations
    c = [ureal(-4.64034, 0.04, label='BIPM'),
         ureal(-4.55899, 0.11 / 2, label='NMIA')]  # average of relative values of all
    traint = CONSTRAINT(t, c)  # set the CONSTRAINT object

    print(traint.line(2006.849))
    print(traint.line(2019.54757))
    print(traint.line(2025))
    print('slope =', traint.slope, traint.slope.x)
    print('intercept =', traint.intercept, traint.intercept.x)
    print(traint.year_fraction(dt.now()))

    now = dt.now()

    print(type(now))
    my_date = parser.parse('27-Sep-2021')  # typical date form in our csv files
    my_fraction = traint.year_fraction(my_date)
    print(repr(traint.line(my_fraction)))
    print(traint.predicted('27-Sep-2021'))


    # plotting the restraint

    # x = np.arange(2009, 2025, 0.1)
    # y1 = traint.line(x)
    # y2 = []
    # y3 = []
    # y4 = []
    # u = []
    # for item in y1:
    #     y2.append(item.x)
    #     y3.append(item.x - item.u)
    #     y4.append(item.x + item.u)
    # fig = plt.figure()
    # ax = fig.add_subplot(1, 1, 1)
    # ax.plot(x, y2)
    # ax.plot(x, y3, 'g', linestyle='dashed')
    # ax.plot(x, y4, 'g', linestyle='dashed')
    # ax.errorbar(t, traint.cal, yerr=traint.ecal, linestyle="None", fmt='o', capsize=10)
    # plt.show()
