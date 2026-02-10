# analysis.py picks up a set of summary_main.csv files and normalises all capacitor values to a chosen constraint
# this replaces the need to copy and paste from csv into xlsx for generating lists and graphs
import csv
from reference import REFERENCE
from matplotlib import pyplot as plt
from conditions import CONDITIONS
from GTC import ureal
from json import dumps
import pickle
import mpld3

class ANALYSE():
    def __init__(self, file_list):
        """

        :param file_list:
        """
        self.pred = REFERENCE()  # used for decimal date as well as the reference values
        self.file_list = file_list

        # 'vals' is list of (date, val pF, u pF, val S, uS) tuples
        self.ah11a1 = {'name': 'AH11A1', 'nompF': 10, 'vals': [], 'ppm': [], 'cppm': [], 'conduct': []}
        self.ah11b1 = {'name': 'AH11B1', 'nompF': 10, 'vals': [], 'ppm': [], 'cppm': [], 'conduct': []}
        self.ah11c1 = {'name': 'AH11C1', 'nompF': 100, 'vals': [], 'ppm': [], 'cppm': [], 'conduct': []}
        self.ah11d1 = {'name': 'AH11D1', 'nompF': 100, 'vals': [], 'ppm': [], 'cppm': [], 'conduct': []}
        self.ah11a2 = {'name': 'AH11A2', 'nompF': 10, 'vals': [], 'ppm': [], 'cppm': [], 'conduct': []}
        self.ah11b2 = {'name': 'AH11B2', 'nompF': 10, 'vals': [], 'ppm': [], 'cppm': [], 'conduct': []}
        self.ah11c2 = {'name': 'AH11C2', 'nompF': 100, 'vals': [], 'ppm': [], 'cppm': [], 'conduct': []}
        self.ah11d2 = {'name': 'AH11D2', 'nompF': 100, 'vals': [], 'ppm': [], 'cppm': [], 'conduct': []}
        self.es14 = {'name': 'ES14', 'nompF': 0.5, 'vals': [], 'ppm': [], 'cppm': [], 'conduct': []}
        self.es13 = {'name': 'ES13', 'nompF': 5, 'vals': [], 'ppm': [], 'cppm':[], 'conduct': []}
        self.es16 = {'name': 'ES16', 'nompF': 5, 'vals': [], 'ppm': [], 'cppm':[], 'conduct': []}
        self.gr10 = {'name': 'GR10', 'nompF': 10, 'vals': [], 'ppm': [], 'cppm':[], 'conduct': []}
        self.gr100 = {'name': 'GR100', 'nompF': 100, 'vals': [], 'ppm': [], 'cppm':[], 'conduct': []}
        self.gr1000a = {'name': 'GR1000A', 'nompF': 1000, 'vals': [], 'ppm': [], 'cppm':[], 'conduct': []}
        self.gr1000b = {'name': 'GR1000B', 'nompF': 1000, 'vals': [], 'ppm': [], 'cppm':[], 'conduct': []}
        self.es13es16 = {'name': 'ES13ES16', 'nompF': 10, 'vals': [], 'ppm': [], 'cppm':[], 'conduct': []}
        self.dicts = ['AH11A1', 'AH11B1', 'AH11C1', 'AH11D1', 'AH11A2', 'AH11B2', 'AH11C2', 'AH11D2',
                 'ES14', 'ES13', 'ES16', 'GR10', 'GR100', 'GR1000A', 'GR1000B', 'ES13ES16']
        self.all_dict = {
            'AH11A1':self.ah11a1, 'AH11B1': self.ah11b1, 'AH11C1': self.ah11c1, 'AH11D1': self.ah11d1,
            'AH11A2': self.ah11a2, 'AH11B2': self.ah11b2, 'AH11C2': self.ah11c2, 'AH11D2': self.ah11d2,
            'ES14': self.es14, 'ES13': self.es13, 'ES16': self.es16, 'GR10': self.gr10, 'GR100': self.gr100,
            'GR1000A': self.gr1000a, 'GR1000B': self.gr1000b, 'ES13ES16': self.es13es16,
            }
        self.add_influence()  # loads best estimates of temperature and pressure coefficients
        self.cond_dict = {'AH1': [], 'AH2': [], 'GRin': [], 'GRout': [], 'AB1': [], 'Sball': [], 'Perm': [], 'Barom': []}
        # 'ppm' is the raw ppm value, 'cppm' is corrected to the constraint, 'std_ppm' is 'cppm' at standard conditions

    def add_influence(self):
        """

        Add influence coefficients (temperature and pressure) and standard conditions for each capacitor.
        :return:
        """
        # from Electricity\Ongoing\Farad\LabShift\AH2700A checks KJ_GH.xlsx inferred from AH2700A measurements
        es14_tc = ureal(4.21, 0.5)
        es16_tc = ureal(2.46, 0.5)
        es13_tc = ureal(2.89, 0.5)
        gr10_tc = ureal(4.96, 0.2)
        gr100_tc = ureal(2.30, 0.2)
        gr1000A_tc = ureal(1.37, 0.2)
        gr1000B_tc = ureal(1.01, 0.2)
        gr10_pc = ureal(-4.6e-2, 0.5e-2)
        gr100_pc = ureal(-4.5e-3, 0.5e-2)
        gr1000a_pc = ureal(1.04e-2, 0.5e-2)
        gr1000b_pc =ureal(2.41e-2, 0.5e-2)

        # add the above to dictionaries
        self.es14['tempco'] = es14_tc
        self.es16['tempco'] = es16_tc
        self.es13['tempco'] =es13_tc
        self.es13es16['tempco'] = (es13_tc + es16_tc) / 2
        self.gr10['tempco'] = gr10_tc
        self.gr100['tempco'] = gr100_tc
        self.gr1000a['tempco'] = gr1000A_tc
        self.gr1000b['tempco'] = gr1000B_tc
        self.gr10['pc'] = gr10_pc
        self.gr100['pc'] = gr100_pc
        self.gr1000a['pc'] = gr1000a_pc
        self.gr1000b['pc'] = gr1000b_pc

        # note we have no tc for AH2 and no pc for either AH11 set
        # AH1 already has temperature coefficients in self.pred, an instance of constrained.REFERENCE, without uncertainty
        ah11a1_tc = ureal(self.pred.ah11a1.coefficients, 0.1 * abs(self.pred.ah11a1.coefficients))  # assume 10% u
        ah11b1_tc = ureal(self.pred.ah11b1.coefficients, 0.1 * abs(self.pred.ah11b1.coefficients))  # abs to make u +ve
        ah11c1_tc = ureal(self.pred.ah11c1.coefficients, 0.1 * abs(self.pred.ah11c1.coefficients))
        ah11d1_tc = ureal(self.pred.ah11d1.coefficients, 0.1 * abs(self.pred.ah11d1.coefficients))
        self.ah11a1['tempco'] = ah11a1_tc
        self.ah11b1['tempco'] = ah11b1_tc
        self.ah11c1['tempco'] = ah11c1_tc
        self.ah11d1['tempco'] = ah11d1_tc

        # choose standard conditions of 1000 mbar, 29 deg for AH11, 23 deg for GR and sapphire ball caps
        temp29 = ['AH11A1', 'AH11B1', 'AH11C1', 'AH11D1', 'AH11A2', 'AH11B2', 'AH11C2', 'AH11D2']
        temp23 = ['ES14', 'ES13', 'ES16', 'GR10', 'GR100', 'GR1000A', 'GR1000B', 'ES13ES16']
        p1000 = ['GR10', 'GR100', 'GR1000A', 'GR1000B', 'ES13ES16']
        for x in temp29:
            self.all_dict[x]['stdtemp'] = 29
        for x in temp23:
            self.all_dict[x]['stdtemp'] = 23
        for x in p1000:
            self.all_dict[x]['stdpres'] = 1000

    def load_file(self, file_name):
        """

        generic conversion of csv into a list of rows
        :param file_name:
        :return: block
        """
        block = []
        with open(file_name, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                block.append(row)
        return block

    def extract_key_data(self, block):
        """

        Improve to avoid use of row numbers and to also pick up the environmental conditions
        :param block:
        :return:
        """
        keyheadings = {'Date': 0, 'Conditions': 0, 'Calculated capacitance values': 0}
        for i in range(len(block)):
            a = block[i]
            if len(a) > 0:  # otherwise no zeroth element to print
                if a[0] in keyheadings:
                    keyheadings[a[0]] = i  # in the case of 'Date' it will index the last one, for the buildup

        val_block = []  # for picking up the calculated capacitance values
        start = keyheadings['Calculated capacitance values']
        if start > 0:
            for i in range(start + 2, start + 18):  # assumes fixed number of capacitors
                val_block.append(block[i])
        else:
            print('Capacitance values not found, error in csv file.')

        cond_block = []  # for picking up the conditions
        start1 = keyheadings['Conditions']
        if start > 0:
            for i in range(start1 + 1, start -1):  # counts back from capacitance values
                cond_block.append(block[i])
        else:
            print('Conditions data not found, error in csv file.')

        date_index = keyheadings['Date']
        if date_index > 0:
            date = block[date_index][1]
        else:
            print('Date not found, error in csv file')
            date = 'NA'
        return (val_block, date, cond_block)

    def load_dict(self, val_block, date, cond_block):
        """

        :param val_block:
        :param date:
        :param cond_block:
        :return: sets values for self.all_dict and self.cond_dict
        """
        for x in val_block:
            x_d = self.all_dict[x[0]]  # x_d is the dictionary we want to add values to
            val_tp = (date, x[1], x[2], x[3], x[4])
            x_d['vals'].append(val_tp)
            aa = (float(x[1])  / float(x_d['nompF']) -1) * 1e6  # cap val in ppm
            bb = float(x[2]) / float(x[1]) * 1e6  # cap u in ppm
            ppm_tp = (date, aa, bb)
            x_d['ppm'].append(ppm_tp)
            x_d['conduct'].append((float(x[3]), float(x[4])))  # conductance added directly as nS

        expected = ['AH1', 'AH2', 'GRin', 'GRout', 'AB1', 'Sball', 'Perm', 'Barom']
        cd = CONDITIONS(expected)  # an instance of CONDITIONS
        cd.build_dict_from_block(cond_block)
        this_cond_dict = cd.cond_dict  # a dictionary of ureals for the environmental conditions
        for x in expected:  # the keys of the conditions dictionary
            self.cond_dict[x].append(this_cond_dict[x])  # adds to the dictionary for all the runs

    def all_sumry(self):
        """
        all dictionaries are updated to include all measured values
        :return:
        """
        for x in self.file_list:
            block = self.load_file(x)
            values, date, cond = self.extract_key_data(block)
            self.load_dict(values, date, cond)

    def std_temp_correct(self, std_val, act_temp, temp_co):
        """

        For converting the constraint values of AH1 to the value at the build-up temperature.
        Capcitance value is in ppm and the temperature coefficient is in ppm/ degree celsius
        :param std_val: value at the standard temperature.
        :act_temp: actual temperature
        :param temp_co: temperature coefficient of capacitor.
        :return: value at the scale build-up temperature
        """
        std_temp = self.pred.ah11a1.std_temperature  # same for all AH1 capacitors
        act_value = std_val + (act_temp - std_temp) * temp_co  # value and temp coeff in ppm
        return act_value

    def find_correction(self):
        """
        invoke the constraint put on AH11 set 1 to shift the values of all capacitors
        assumes that the dictionaries are already loaded with the summary results
        assumes that the dates are common for the whole capacitor set
        :return: a list of ppm corrections that should be applied to all the caps
        """
        date = []
        d_date = []
        for x in self.ah11a1['ppm']:
            date.append(x[0])
            dec_date =self.pred.ah11a1.decimal_date(x[0])
            d_date.append(dec_date)
        a = []
        b = []
        c = []
        d = []
        a_predicted_ppm = []
        b_predicted_ppm = []
        c_predicted_ppm = []
        d_predicted_ppm = []

        for i in range(len(date)):
            temperature = self.cond_dict['AH1'][i]  # same for all AH1
            a.append(self.ah11a1['ppm'][i][1])
            temp_co = self.pred.ah11a1.coefficients
            std_value = self.pred.con.predict(self.ah11a1['ppm'][i][0], 0.11)  # predicted value at standard temperature
            act_value = self.std_temp_correct(std_value, temperature, temp_co)  # value and temp coeff in ppm
            a_predicted_ppm.append(act_value)

            b.append(self.ah11b1['ppm'][i][1])
            temp_co = self.pred.ah11b1.coefficients
            std_value = self.pred.con.predict(self.ah11b1['ppm'][i][0], 0.11)  # predicted value at standard temperature
            act_value = self.std_temp_correct(std_value, temperature, temp_co)  # value and temp coeff in ppm
            b_predicted_ppm.append(act_value)

            c.append(self.ah11c1['ppm'][i][1])
            temp_co = self.pred.ah11c1.coefficients
            std_value = self.pred.con.predict(self.ah11c1['ppm'][i][0], 0.11)  # predicted value at standard temperature
            act_value = self.std_temp_correct(std_value, temperature, temp_co)  # value and temp coeff in ppm
            c_predicted_ppm.append(act_value)

            d.append(self.ah11d1['ppm'][i][1])
            temp_co = self.pred.ah11d1.coefficients
            std_value = self.pred.con.predict(self.ah11d1['ppm'][i][0], 0.11)  # predicted value at standard temperature
            act_value = self.std_temp_correct(std_value, temperature, temp_co)  # value and temp coeff in ppm
            d_predicted_ppm.append(act_value)

        # next we want to have a list of corrections based on the predicted values
        corrections = []
        predicted_av = []
        for i in range(len(date)):
            actual_average = (a[i] + b[i] + c[i] + d[i]) / 4
            predicted_average =  (a_predicted_ppm[i].x + b_predicted_ppm[i].x + c_predicted_ppm[i].x + d_predicted_ppm[i].x) / 4
            predicted_av.append(predicted_average)
            corrections.append(predicted_average - actual_average)
        return corrections

    def corrected_dict(self):
        """

        put the corrected ppm values (at the buildup conditions) in the dictionaries
        :return:
        """
        ppm_corrections = self.find_correction()
        for x in self.dicts:  # x is the name of the dictionary
            y = self.all_dict[x]  # y is the actual dictionary
            time = []  # x axis date
            c_ppm = []  # the raw measured cap value in ppm
            u_ppm = []  # uncertainty in ppm?
            for z in y['ppm']:  # z is the ppm tuple
                time.append(self.pred.ah11a1.decimal_date(z[0]))
                c_ppm.append(z[1])
                u_ppm.append(z[2])
            cor_ppm = []
            for i in range(len(ppm_corrections)):
                cor_ppm.append((time[i], c_ppm[i] + ppm_corrections[i], u_ppm[i]))
            y['cppm'] = cor_ppm  # the dictionary now has corrected ppm values (at actual temp, pressure) loaded

    # correct each capacitor back to standard temperature and pressure
    def corrected_to_std(self, meas, meas_con, std_con, coeff):
        """

        generic method for any linear sensitivity
        :param meas: the measured value in ppm
        :param meas_con: the temperature or pressure at measurement
        :param std_con: the standard temperature or pressure we want to report at
        :param coeff:  the sensitivity coefficient in ppm per unit
        :return: the ppm value at standard conditions
        """
        corrected = (meas - coeff * (meas_con - std_con))
        return corrected

    def corrected_to_std_con(self):
        """

        Takes the dictionary 'cppm' values (corrected for restraint) and adds a 'std_value' to the dictionary.
        The standard value is the ppm capacitance value at the standard temperature and pressure for that component.
        :return: updates the component dictionaries in this class
        """
        # the conditions are common to a single build up, need these available as matching lists with the ppm values
        pressure = self.cond_dict['Barom']  # the list of barometric pressure in mbar, same for all caps
        for x in self.dicts:  # x is the name of the capacitor dictionary
            y = self.all_dict[x]  # y is the dictionary
            corrected = y['cppm']  # the list of (dec_year, ppm value, ppm uncertainty)
            if x in ['AH11A1', 'AH11B1', 'AH11C1', 'AH11D1']:
                temp_list = self.cond_dict['AH1']
            elif x in ['AH11A2', 'AH11B2', 'AH11C2', 'AH11D2']:
                temp_list = self.cond_dict['AH2']
            elif x in ['GR10', 'GR100', 'GR1000A', 'GR1000B']:
                temp_list = self.cond_dict['GRin']
            elif x in ['ES14', 'ES13', 'ES16', 'ES13ES16']:
                temp_list = self.cond_dict['Sball']
            else:
                print('capacitor not recognised')
                temp_list = []

            full_corrected = []  # this will be the list of values (as tuples) corrected to standard conditions
            i = 0
            for val in corrected:
                cap_val = ureal(float(val[1]), float(val[2]))
                if 'tempco' in y:  # does it have a temperature coefficient
                    cap_val = self.corrected_to_std(cap_val, temp_list[i], y['stdtemp'], y['tempco'])  # cap_val is modified
                if 'pc' in y:
                    cap_val = self.corrected_to_std(cap_val, pressure[i], y['stdpres'], y['pc'])  # cap_val is modified again
                i += 1
                full_corrected.append((val[0], cap_val.x, cap_val.u))
            # print('full_corrected =', full_corrected)
            y['std_ppm'] = full_corrected

    def fully_corrected_dict(self):
        """

        Correct all values back to standard temperature and pressure.
        :return:
        """
        print('Starting to plan the fully corrected version')
        for x in self.dicts:
            print(self.all_dict[x])

    def for_plot_cor(self, cap_dict):
        """

        create lists for a capacitor that can be added to plots as required
        :param cap_dict: one of the capacitance dictionaries
        :return:
        """
        # selected_ppm = 'cppm'  # for corrected to constraint at actual conditions !!!!!!!!!!!!!!!!!!!!
        selected_ppm = 'std_ppm'  # for fully corrected to standard conditions
        time = []  # x axis date
        c_ppm = []  # the raw measured cap value in ppm
        u_ppm = []  # uncertainty in ppm?
        for x in cap_dict['ppm']:
            time.append(self.pred.ah11a1.decimal_date(x[0]))
            c_ppm.append(x[1])
            u_ppm.append(x[2])
        cor_ppm = []
        for x in cap_dict[selected_ppm]:  # assuming it has been created
            cor_ppm.append(x[1])
        return time, c_ppm, cor_ppm, u_ppm

    def out_block(self):
        """

        create a list of lists making up the rows for a simple block of corrected results
        for all the capacitors
        :return:
        """
        # selected_ppm = 'cppm'  # for corrected to constraint at actual conditions !!!!!!!!!!!!!!!!!!!!
        selected_ppm = 'std_ppm'  # for fully corrected to standard conditions
        output = []
        head_row = ['Date', 'AH11A1', 'AH11B1', 'AH11C1', 'AH11D1','AH11A2', 'AH11B2', 'AH11C2', 'AH11D2',
            'ES14', 'ES13', 'ES16', 'GR10', 'GR100', 'GR1000A', 'GR1000B', 'ES13ES16', 'uAH11A1', 'uAH11B1', 'uAH11C1',
            'uAH11D1','uAH11A2', 'uAH11B2', 'uAH11C2', 'uAH11D2', 'uES14', 'uES13', 'uES16', 'uGR10', 'uGR100',
            'uGR1000A', 'uGR1000B', 'uES13ES16',
            'gAH11A1', 'gAH11B1', 'gAH11C1', 'gAH11D1', 'gAH11A2', 'gAH11B2', 'gAH11C2', 'gAH11D2',
            'gES14', 'gES13', 'gES16', 'gGR10', 'gGR100', 'gGR1000A', 'gGR1000B', 'gES13ES16', 'ugAH11A1', 'ugAH11B1',
            'ugAH11C1',
            'ugAH11D1', 'ugAH11A2', 'ugAH11B2', 'ugAH11C2', 'ugAH11D2', 'ugES14', 'ugES13', 'ugES16', 'ugGR10', 'ugGR100',
            'ugGR1000A', 'ugGR1000B', 'ugES13ES16'
            ]
        output.append(head_row)
        for i in range(len(self.ah11a1[selected_ppm])):
            line = []
            line.append(self.ah11a1['cppm'][i][0])  # this is the date, the same for all capacitors
            for x in self.dicts:
                line.append(self.all_dict[x][selected_ppm][i][1])  # corrected ppm
            for x in self.dicts:
                line.append(self.all_dict[x][selected_ppm][i][2])  # uncertainty
            for x in self.dicts:
                line.append(self.all_dict[x]['conduct'][i][0])  # conductance in nS
            for x in self.dicts:
                line.append(self.all_dict[x]['conduct'][i][1])  # uncertainty of conductance in nS
            output.append(line)
        return output

    def file_block(self, file_name, block):
        with open(file_name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for x in block:
                writer.writerow(x)

    def plot(self, set, title):
        """

        :param set:
        :return:
        """
        lines = ['-', '--', '-.', ':']
        cmap = plt.get_cmap('tab20')
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        count = 0
        for name in set:  # x is the name string
            if count < 4:
                line = lines[0]
            else:
                line = lines[1]
            spec_dict = self.all_dict[name]  # the specific dictionary
            x, y, z, u = self.for_plot_cor(spec_dict)
            ax.errorbar(x, z, yerr=u, linestyle=line, fmt='o', capsize=10, color=cmap(count))
            ax.plot(x, z, label=spec_dict['name'] + '_corr', linestyle=line, color=cmap(count))
            count += 1
        fig.set_size_inches(11.69, 8.27)  # A4 landscape
        plt.title(title)
        plt.legend()
        plt.tight_layout()
        plt.savefig(title + '.pdf')
        plt.savefig(title + '.jpg')
        with open(title + '.pkl', 'wb') as f:  # use view.py to interact later
            pickle.dump(fig, f)
        # html_fig = mpld3.fig_to_html(fig)
        # with open(title +'.html', "w") as f:
        #     f.write(html_fig)
        plt.show()

    def store_dicts(self):
        """

        Stores the capacitor dictionaries for use by cap_fit.py, converting temperature and pressure coefficients
        from simple ureal to a tuple (x, u).
        :return:
        """
        block = []  # for assembling the dictionaries
        for x in self.dicts:
            this_dict = self.all_dict[x]
            new_dict = {}  # replicate this_dict to cope with changing simple ureal to tuple
            for y in this_dict:
                if y == 'tempco' or y == 'pc':
                    # new_dict[y] = gs.ureal_to_json(this_dict[y])
                    new_dict[y] = (this_dict[y].x, this_dict[y].u)
                else:
                    new_dict[y] = this_dict[y]
            out_json = dumps(new_dict)
            block.append([out_json])
        with open('analysis_dict.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for x in block:
                writer.writerow(x)



if __name__ == '__main__':
    # anal = ANALYSE([
    #     r'new_datastore\nov2019\summary_main_2021-08-23_a.csv',
    #     r'new_datastore\dec2020\summary_main_2021-08-27_a.csv',
    #     r'new_datastore\sep2021\summary_main_2021-09-06_a.csv',
    #     r'new_datastore\sep2021\summary_main_2021-09-09.csv',
    #     r'new_datastore\sep2021\summary_main_2021-09-10.csv',
    #     r'new_datastore\sep2021\summary_main_2021-09-22.csv',
    #     r'new_datastore\sep2021\summary_main_2021-10-11_b.csv',
    #     r'new_datastore\June2025\summary_main_2025-07-03.csv',
    #     r'new_datastore\June2025\summary_main_2025-07-04.csv',
    #     r'new_datastore\June2025\summary_main_2025-07-07.csv',
    #     r'new_datastore\June2025\summary_main_2025-07-08.csv'
    #     ] )
    anal = ANALYSE([
        r'old_datastore\nov2019\summary_main_2021-08-23_a.csv',
        r'old_datastore\dec2020\summary_main_2021-08-27_a.csv',
        r'old_datastore\sep2021\summary_main_2021-09-06_a.csv',
        r'old_datastore\sep2021\summary_main_2021-09-09.csv',
        r'old_datastore\sep2021\summary_main_2021-09-10.csv',
        r'old_datastore\sep2021\summary_main_2021-09-22.csv',
        r'old_datastore\sep2021\summary_main_2021-10-11_b.csv',
        r'old_datastore\June2025\summary_main_2025-07-03.csv',
        r'old_datastore\June2025\summary_main_2025-07-04.csv',
        r'old_datastore\June2025\summary_main_2025-07-07.csv',
        r'old_datastore\June2025\summary_main_2025-07-08.csv'
        ])
    anal.all_sumry()  # loads the data
    anal.corrected_dict()  # applies constraint of the mean of AH11 set #1
    anal.plot(['AH11A1', 'AH11B1', 'AH11C1', 'AH11D1', 'AH11A2', 'AH11B2', 'AH11C2', 'AH11D2'], 'AH11 set')
    anal.plot( ['ES14', 'ES13', 'ES16', 'GR10', 'GR100', 'GR1000A', 'GR1000B', 'ES13ES16'], 'GR and S ball set')
    out_block = anal.out_block()  # prepares csv-friendly lists
    anal.file_block('test_analysis.csv', out_block)  # writes to csv file
