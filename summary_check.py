# Python 3.9 environment
"""
Summarises all the input and output data into a 'human readable' format in a single csv file. This summary file is also
appropriate for viewing with a spreadsheet program which can be used to support the checking process and plotting
of historical values. It can also provide an updated file LEAD and CAPACITOR objects for input to the next capacitance
calibration run.

"""
import csv
import os
from json import loads
from archive import COMPONENTSTORE
from datetime import datetime


class SUMMARY(object):
    def __init__(self, file_list):
        """
        SUMMARY creates a single csv file that contains all the input data and calculated results in a human readable
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

    def create_summary(self, update):
        """
        Step by step acquiring of data and results to put in the output csv file

        :param update: boolean set to True if an updated leads and caps file is also wanted
        :return: a summary csv placed in the working directory and named 'summary' + the 'Scale output' name and, if update is set to True, an updated file 'Leads and caps' name + 'updated' .csv.
        """
        if update:  # updated leads and caps wanted
            l_c_file_update = self.file_dict['Working directory'] + '/' + self.file_dict['Leads and caps'][:-4] + \
                              '_update.csv'
            print('Updated file will be', l_c_file_update)
            l_c_update = [['Leads']]  # header for the leads section

        store = COMPONENTSTORE()
        hr_file = os.path.join(self.file_dict['Working directory'], 'summary_' + self.file_list)
        hr_output = []
        # Files used to make this summary
        hr_output.append(['File information for this summary'])
        hr_output.append(['Summary produced', datetime.now()])
        working_directory = os.getcwd()
        master_file = working_directory + '\\' + self.file_list
        hr_output.append(['List of files held in', master_file])
        for x in self.file_dict:
            hr_output.append([x, self.file_dict[x]])
        hr_output.append([])
        # Input for calibrating the main dials
        compx = ['alpha1', 'beta1', 'alpha2', 'beta2']
        ucompx = ['z3']
        hr_output.append(['Input for calibrating the main dials'])
        data_in = self.file_dict['Working directory'] + '/' + self.file_dict['Dial input']
        with open(data_in, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0] in compx:
                    item = store.gs.dict_to_ureal(loads(row[1]))
                    hr_output.append([row[0], item.x, item.u])
                elif row[0] in ucompx:
                    item = store.gs.dict_to_ucomplex(loads(row[1]))
                    hr_output.append([row[0], item.real.x, item.real.u, item.imag.x, item.imag.u])
                else:
                    hr_output.append(row)
        hr_output.append([])  # just to space between the outputs
        # Calculated dial factors
        hr_output.append(['Calculated dial factors'])
        data_in = self.file_dict['Working directory'] + '/' + self.file_dict['Dial output']
        with open(data_in, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            header_flag = 0
            for row in reader:
                if row[0] in ['factora', 'factorb']:
                    if header_flag == 0:
                        hr_output.append(['Name', 'real', 'u', 'imag', 'u', 'df'])
                        header_flag = 1  # only need one header
                    factor = store.gs.dict_to_ucomplex(loads(row[1]))  # converts json string to ucomplex
                    hr_output.append([row[0], factor.real.x, factor.real.u, factor.imag.x, factor.imag.u, factor.df])
                else:
                    hr_output.append(row)
        hr_output.append([])  # just to space between the outputs
        # Input for calibrating the main 10:1 ratio with the permutable capacitor
        hr_output.append(['Input for calibrating the main 10:1 ratio'])
        data_in = self.file_dict['Working directory'] + '/' + self.file_dict['Permutable']
        with open(data_in, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) == 1:
                    hr_output.append(row)  # assumed header row
                    hr_output.append(['component', 'real', 'imaginary'])  # header for component list
                elif row[0] in ['pc1', 'pc2', 'pc3', 'pc4', 'pc5', 'pc6', 'pc7', 'pc8', 'pc9', 'pc10', 'pc11']:
                    hr_output.append([row[0], row[1]])
                else:
                    item = store.gs.dict_to_ucomplex(loads(row[1]))
                    hr_output.append([row[0], item.real.x, item.imag.x])
        hr_output.append([])  # just to space between the outputs
        # Permutable balance readings
        hr_output.append(['Balance readings'])
        data_in = self.file_dict['Working directory'] + '/' + self.file_dict['Ratio input']
        with open(data_in, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            for row in reader:
                hr_output.append(row)
        # The calculated 10:1 ratio
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
        # Dial readings for all the capacitor ratios
        hr_output.append([])  # just to space between the outputs
        hr_output.append(['Input for capacitance scale'])
        data_in = self.file_dict['Working directory'] + '/' + self.file_dict['Scale input']
        with open(data_in, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            for row in reader:
                hr_output.append(row)
        # Calculated capacitance values
        hr_output.append([])  # just to space between the outputs
        hr_output.append(['Calculated capacitance values'])
        hr_output.append(['Name', 'capacitance/pF', 'u/pF', 'conductance/nS', 'u/nS'])
        data_in = self.file_dict['Working directory'] + '/' + self.file_dict['Scale output']
        values = store.gs.read_gtc(data_in)
        for x in values:
            output = []
            # name = x[0]
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
        # Lead and capacitor component values put in to the calculation
        hr_output.append([])  # just to space between the outputs
        hr_output.append(['Leads and capacitors summary as at input (no updated best values)'])
        data_in = self.file_dict['Working directory'] + '/' + self.file_dict['Leads and caps']
        h1 = 0  # h1 and h2 are flags for if header 1 and header2 have been printed yet
        h2 = 0
        with open(data_in, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) == 1:
                    continue  # do nothing, it is a redundant header
                else:
                    jdata = loads(row[1])
                    try:  # components.CAPACITOR object
                        bb = store.dict_to_capacitor(jdata)  # components.CAPACITOR object
                        cap = (bb.best_value.imag / bb.w * 1e12).x  # in pF
                        unc = [bb.best_value.u[0] * 1.0e9, bb.best_value.u[1] / bb.w * 1e12]  # in nS and pF
                        cond = (bb.best_value.real.x * 1.0e9)  # conductance in nS
                        yhv = bb.y12
                        ylv = bb.y34
                        angf = bb.w
                        for_summary = [row[0], cap, unc[0], cond, unc[1], yhv.imag.x * 1e12 / angf, yhv.real.x * 1e9,
                                       ylv.imag.x * 1e12 / angf, ylv.real.x * 1e9, angf]
                        if h1 == 0:
                            hr_output.append(['Capacitors'])
                            hr_output.append(
                                ['Name', 'C pF', 'u pF', 'G nS', 'u nS', 'yhv pF', 'yhv nS', 'ylv pF', 'ylv nS',
                                 'ang freq'])
                            h1 += 1
                    except KeyError:  # components.LEAD object so not processed (lazy approach)
                        if h2 == 0:
                            hr_output.append(['Leads'])
                            hr_output.append(['Name', 'rel unc', 'ang freq', 'C pF', 'G nS', 'r ohm', 'l microH'])
                            h2 += 1
                            if update:
                                l_c_update.append(row)
                        elif update:  # adds unaltered leads to the update file
                            l_c_update.append(row)
                        bb = store.dict_to_lead(jdata)
                        angf = bb.w
                        for_summary = [row[0], bb.relu, bb.w, bb.y.imag.x / angf * 1e12, bb.y.real.x * 1e9, bb.z.real.x,
                                       bb.z.imag.x / angf * 1e6]
                    hr_output.append(for_summary)
        with open(hr_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for x in hr_output:
                writer.writerow(x)
        if update:  # leads already listed, now do capacitors
            print('update leads and caps')
            l_c_update.append(['Capacitors'])
            data_in = self.file_dict['Working directory'] + '/' + self.file_dict['Scale output']
            with open(data_in, newline='') as csvfile:  # format must be correct
                reader = csv.reader(csvfile)
                for row in reader:
                    new_row = [row[0], row[2]]  # miss out the pF value, just keep the ucomplex value
                    l_c_update.append(new_row)

            with open(l_c_file_update, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                for x in l_c_update:
                    writer.writerow(x)


if __name__ == '__main__':
    my_summary = SUMMARY('main_2.csv')
    my_summary.create_summary(False)
