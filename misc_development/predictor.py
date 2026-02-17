from constraint import CONSTRAINT as con
from GTC import ureal
from datetime import datetime as dt
from dateutil import parser
import time


class PREDICT(object):
    def __init__(self):
        """
        Uses two calibration points to provide a straight line prediction of the mean of the relative values (ppm
        relative error) of all four AH11x1 capacitors.
        These are fixed at instantiation but could be read from a file.

        """
        AH11A1 = {'date1': '19-Mar-2009', 'value1': ureal(-4.915, 0.04, label='AH11A1_1'),
                  'date2': '20-Jul-2019', 'value2': ureal(-4.994, 0.11, label='AH11A1_2')}
        AH11B1 = {'date1': '19-Mar-2009', 'value1': ureal(-4.707, 0.04, label='AH11B1_1'),
                  'date2': '20-Jul-2019', 'value2': ureal(-4.722, 0.11, label='AH11B1_2')}
        AH11C1 = {'date1': '19-Mar-2009', 'value1': ureal(-4.423, 0.04, label='AH11C1_1'),
                  'date2': '20-Jul-2019', 'value2': ureal(-4.194, 0.11, label='AH11C1_2')}
        AH11D1 = {'date1': '19-Mar-2009', 'value1': ureal(-4.510, 0.04, label='AH11D1_1'),
                  'date2': '20-Jul-2019', 'value2': ureal(-4.326, 0.11, label='AH11D1_2')}

        self.a = con([self.dec_date(AH11A1['date1']), self.dec_date(AH11A1['date2'])], [AH11A1['value1'], AH11A1['value2']])
        self.b = con([self.dec_date(AH11B1['date1']), self.dec_date(AH11B1['date2'])], [AH11B1['value1'], AH11B1['value2']])
        self.c = con([self.dec_date(AH11C1['date1']), self.dec_date(AH11C1['date2'])], [AH11C1['value1'], AH11C1['value2']])
        self.d = con([self.dec_date(AH11D1['date1']), self.dec_date(AH11D1['date2'])], [AH11D1['value1'], AH11D1['value2']])

    def dec_date(self,date):
        """

        decimal year from a string representation of date
        :param date: string that can be interpreted as a datetime object
        :return: decimal year
        """
        proper_date = parser.parse(date)
        year = proper_date.year
        startOfThisYear = dt(year=year, month=1, day=1)
        startOfNextYear = dt(year=year + 1, month=1, day=1)
        yearElapsed = time.mktime(proper_date.timetuple()) - time.mktime(startOfThisYear.timetuple())
        yearDuration = time.mktime(startOfNextYear.timetuple()) - time.mktime(startOfThisYear.timetuple())
        fraction = yearElapsed / yearDuration
        decimal_date = proper_date.year + fraction
        return decimal_date

if __name__ == '__main__':
    pre = PREDICT()
    print('Test dates')
    check_dates = ['7-Apr-2022', '11-Apr-2022','30-May-2022', '31-May-2022', '2-Jun-2022', '20-Jun-2022','21-Jun-2022',
                   '4-Jul-2022', '11-Jul-2022', '5-Jul-2022', '1-Aug-2022', '23-Sep-2023', '25-Oct-2022', '11-Nov-22',
                   '16-Jan-2023', '28-Mar-2023', '8-May-2023', '16-May-2023', '17-May-2023', '23-May-2023', '29-Sep-2023',
                   '2-Oct-2023', '18-Dec-2023', '5-Aug-2025', '28-Oct-2025']
    # check_dates = ['5-Aug-2025']
    for x in check_dates:
        # print(pre.d.predicted(x))
        # print(x, pre.dec_date(x), pre.d.predicted(x))
        a = pre.a.predicted(x)
        b = pre.b.predicted(x)
        c = pre.c.predicted(x)
        d = pre.d.predicted(x)
        print(x,'average =', (a + b +c +d) / 4, a, b, c, d)