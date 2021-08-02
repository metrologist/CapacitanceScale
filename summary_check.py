import csv
import os
from json import loads
from archive import COMPONENTSTORE
from datetime import datetime

class SUMMARY(object):
    def __init__(self, file_list):
        """
        SUMMARY provides a single csv file that contains all the input data and calculated results in a human readable
        format. This is a convenience for checking purposes noting that the full results are stored in csv files as
        json strings holding uncertain numbers.
        :param file_list: the list of input and output csv files identical to that used for the main calculation

        """
        self.file_dict = {}  # hold these directories/files in this dictionary
        with open(file_list, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.file_dict[row[0]] = row[1]

        self.file_list = file_list  # to make sure we are clear on the data source

    def create_summary(self):
        store = COMPONENTSTORE()
        hr_file = os.path.join(self.file_dict['Working directory'], 'summary_' + self.file_dict['Scale output'])
        hr_output = []

        hr_output.append(['File information for this summary'])
        hr_output.append(['Summary produced', datetime.now()])
        working_directory = os.getcwd()
        master_file = working_directory + '\\' + self.file_list
        hr_output.append(['List of files held in', master_file])
        for x in self.file_dict:
            hr_output.append([x, self.file_dict[x]])
        hr_output.append([])

        # read in the main balance calibration file
        hr_output.append(['Input for calibrating the main dials'])
        data_in = self.file_dict['Working directory'] + '/' + self.file_dict['Dial input']
        with open(data_in, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            for row in reader:
                hr_output.append(row)
        hr_output.append([])  # just to space between the outputs

        hr_output.append(['Calculated dial factors'])
        data_in = self.file_dict['Working directory'] + '/' + self.file_dict['Dial output']
        with open(data_in, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            header_flag = 0
            for row in reader:
                if row[0] in ['factora', 'factorb']:
                    if header_flag ==0:
                        hr_output.append(['Name', 'real', 'u', 'imag', 'u', 'df'])
                        header_flag = 1  #only need one header
                    factor = store.gs.dict_to_ucomplex(loads(row[1]))  # converts json string to ucomplex
                    hr_output.append([row[0], factor.real.x, factor.real.u, factor.imag.x, factor.imag.u, factor.df])
                else:
                    hr_output.append(row)
        hr_output.append([])  # just to space between the outputs

        hr_output.append(['Input for calibrating the main 10:1 ratio'])
        data_in = self.file_dict['Working directory'] + '/' + self.file_dict['Ratio input']
        with open(data_in, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            header_flag = 0
            for row in reader:
                if row[0] in ['za', 'ya', 'zinta', 'y3', 'y4Y2', 'zb', 'yb', 'zintb', 'y1', 'y2Y1']:
                    if header_flag ==0:
                        hr_output.append(['Name', 'real', 'u', 'imag', 'u', 'df'])
                        header_flag = 1  #only need one header
                    factor = store.gs.dict_to_ucomplex(loads(row[1]))  # converts json string to ucomplex
                    hr_output.append([row[0], factor.real.x, factor.real.u, factor.imag.x, factor.imag.u, factor.df])
                else:
                    hr_output.append(row)

        hr_output.append([])  # just to space between the outputs
        hr_output.append(['Calculated 10:1 ratio'])
        data_in = self.file_dict['Working directory'] + '/' + self.file_dict['Ratio output']
        with open(data_in, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0][0] == '{':  # name was not included in the csv file so rely on {
                    hr_output.append(['Name', 'real', 'u', 'imag', 'u', 'df'])
                    factor = store.gs.dict_to_ucomplex(loads(row[0]))  # converts json string to ucomplex
                    hr_output.append(['ratio', factor.real.x, factor.real.u, factor.imag.x, factor.imag.u, factor.df])
                else:
                    hr_output.append(row)

        hr_output.append([])  # just to space between the outputs
        hr_output.append(['Input for capacitance scale'])
        data_in = self.file_dict['Working directory'] + '/' + self.file_dict['Scale input']
        with open(data_in, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            for row in reader:
                    hr_output.append(row)

        hr_output.append([])  # just to space between the outputs
        hr_output.append(['Calculated capacitance values'])
        hr_output.append(['Name','capacitance/pF', 'u/pF', 'conductance/nS', 'u/nS'])
        data_in = self.file_dict['Working directory'] + '/' + self.file_dict['Scale output']
        values = store.gs.read_gtc(data_in)
        for x in values:
            output = []
            name = x[0]
            jdata = loads(x[2])
            bb = store.dict_to_capacitor(jdata)  # components.CAPACITOR object
            cap = (bb.best_value.imag / bb.w * 1e12).x  # in pF
            unc = [bb.best_value.u[0] * 1.0e9, bb.best_value.u[1] / bb.w * 1e12]  # in nS and pF
            output.append(bb.label)
            output.append(cap)
            output.append(unc[1])
            cond = (bb.best_value.real.x * 1.0e9)  # conductance in nS
            output.append(cond)
            output.append(unc[0])
            hr_output.append(output)

        hr_output.append([])  # just to space between the outputs
        hr_output.append(['Leads and capacitors summary'])
        data_in = self.file_dict['Working directory'] + '/' + self.file_dict['Leads and caps']
        h1 = 0  # h1 and h2 are flags for if header 1 and header2 have been printed yet
        h2 = 0
        with open(data_in, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            for row in reader:
                jdata = loads(row[1])
                try:  # components.CAPACITOR object
                    bb = store.dict_to_capacitor(jdata)  # components.CAPACITOR object
                    cap = (bb.best_value.imag / bb.w * 1e12).x  # in pF
                    unc = [bb.best_value.u[0] * 1.0e9, bb.best_value.u[1] / bb.w * 1e12]  # in nS and pF
                    cond = (bb.best_value.real.x * 1.0e9)  # conductance in nS
                    yhv = bb.y12
                    ylv = bb.y34
                    angf = bb.w
                    lv = bb.lvlead.label
                    hv = bb.hvlead.label
                    for_summary = [row[0], cap, unc[0], cond, unc[1], yhv, ylv, angf, lv, hv]
                    if h1 == 0:
                        hr_output.append(['Capacitors'])
                        hr_output.append(['Name', 'pF','u', 'nS', 'u', 'yhv', 'ylv', 'ang freq', 'lv lead', 'hv lead'])
                        h1 += 1
                except:  # components.LEAD object so not processed (lazy approach)
                    if h2 == 0:
                        hr_output.append(['Leads'])
                        hr_output.append(['Name', 'rel unc', 'ang freq', 'C', 'G', 'r', 'l'])
                        h2 += 1
                    bb = store.dict_to_lead(jdata)
                    for_summary = [row[0], bb.relu, bb.w, bb.y.real.x, bb.y.imag.x, bb.z.real.x, bb.z.imag.x]
                hr_output.append(for_summary)

        with open(hr_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for x in hr_output:
                writer.writerow(x)

if __name__ == '__main__':
    factora = 1.0
    factorb = 1.0
    final_ratio = 10.0
    cert = 10.0
    all_capacitors = {}
    main_results = [factora, factorb, final_ratio, cert, all_capacitors]
    # all_capacitors is a dictionary, so can generalise it for any number
    # factors, ratio and cert are fixed
    my_summary = SUMMARY('main.csv')
    my_summary.create_summary()