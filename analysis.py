# analysis.py picks up a set of summary_main.csv files and normalises all capacitor values to a chosen constraint
# this replaces the need to copy and paste from csv into xlsx for generating lists and graphs
import csv
from constrained import REFERENCE
from matplotlib import pyplot as plt

class ANALYSE():
    def __init__(self, file_list):
        """

        :param file_list:
        """
        self.pred = REFERENCE()  # used for decimal date as well as the refence values
        self.file_list = file_list

        # 'vals' is list of (date, val pF, u pF, val S, uS) tuples
        self.ah11a1 = {'name': 'AH11A1', 'nompF': 10, 'vals': [], 'ppm': [], 'cppm': []}
        self.ah11b1 = {'name': 'AH11B1', 'nompF': 10, 'vals': [], 'ppm': [], 'cppm': []}
        self.ah11c1 = {'name': 'AH11C1', 'nompF': 100, 'vals': [], 'ppm': [], 'cppm': []}
        self.ah11d1 = {'name': 'AH11D1', 'nompF': 100, 'vals': [], 'ppm': [], 'cppm': []}
        self.ah11a2 = {'name': 'AH11A2', 'nompF': 10, 'vals': [], 'ppm': [], 'cppm': []}
        self.ah11b2 = {'name': 'AH11B2', 'nompF': 10, 'vals': [], 'ppm': [], 'cppm': []}
        self.ah11c2 = {'name': 'AH11C2', 'nompF': 100, 'vals': [], 'ppm': [], 'cppm': []}
        self.ah11d2 = {'name': 'AH11D2', 'nompF': 100, 'vals': [], 'ppm': [], 'cppm': []}
        self.es14 = {'name': 'ES14', 'nompF': 0.5, 'vals': [], 'ppm': [], 'cppm': []}
        self.es13 = {'name': 'ES13', 'nompF': 5, 'vals': [], 'ppm': [], 'cppm':[]}
        self.es16 = {'name': 'ES16', 'nompF': 5, 'vals': [], 'ppm': [], 'cppm':[]}
        self.gr10 = {'name': 'GR10', 'nompF': 10, 'vals': [], 'ppm': [], 'cppm':[]}
        self.gr100 = {'name': 'GR100', 'nompF': 100, 'vals': [], 'ppm': [], 'cppm':[]}
        self.gr1000a = {'name': 'GR1000A', 'nompF': 1000, 'vals': [], 'ppm': [], 'cppm':[]}
        self.gr1000b = {'name': 'GR1000B', 'nompF': 1000, 'vals': [], 'ppm': [], 'cppm':[]}
        self.es13es16 = {'name': 'ES13ES16', 'nompF': 10, 'vals': [], 'ppm': [], 'cppm':[]}
        self.dicts = ['AH11A1', 'AH11B1', 'AH11C1', 'AH11D1', 'AH11A2', 'AH11B2', 'AH11C2', 'AH11D2',
                 'ES14', 'ES13', 'ES16', 'GR10', 'GR100', 'GR1000A', 'GR1000B', 'ES13ES16']
        self.all_dict = {
            'AH11A1':self.ah11a1, 'AH11B1': self.ah11b1, 'AH11C1': self.ah11c1, 'AH11D1': self.ah11d1,
            'AH11A2': self.ah11a2, 'AH11B2': self.ah11b2, 'AH11C2': self.ah11c2, 'AH11D2': self.ah11d2,
            'ES14': self.es14, 'ES13': self.es13, 'ES16': self.es16, 'GR10': self.gr10, 'GR100': self.gr100,
            'GR1000A': self.gr1000a, 'GR1000B': self.gr1000b, 'ES13ES16': self.es13es16,
            }

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

        Asumme that the block is extracted from a 'standard' summary file
        Could just do it by line number but there should be some key word checking
        :param block:
        :return:
        """
        offset = -1  # as excel, notepad++ start at 1 not zero
        check_date = block[89 + offset]
        if check_date[0] == 'Date':
            date = check_date[1]
            print('Block aligned', date)
        else:
            print('Date not found')
            date ='NA'
        val_block = []  # just want the calculated values
        for i in range(109, 125):  # calculated values of the set
            val_block.append(block[i])
        return(val_block, date)

    def load_dict(self, val_block, date):
        """

        :param val_block:
        :return:
        """
        for x in val_block:
            x_d = self.all_dict[x[0]]  # x_d is the dictionary we want to add values to
            val_tp = (date, x[1], x[2], x[3], x[4])
            x_d['vals'].append(val_tp)
            aa = (float(x[1])  / float(x_d['nompF']) -1) * 1e6  # cap val in ppm
            bb = float(x[2]) / float(x[1]) * 1e6  # cap u in ppm
            ppm_tp = (date, aa, bb)
            x_d['ppm'].append(ppm_tp)

    def all_sumry(self):
        """
        all dictionaries are updated to include all measured values
        :return:
        """
        for x in self.file_list:
            block = self.load_file(x)
            values, date = self.extract_key_data(block)
            self.load_dict(values, date)

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
            a.append(self.ah11a1['ppm'][i][1])
            a_predicted_ppm.append(self.pred.con.predict(self.ah11a1['ppm'][i][0], 0.11))
            b.append(self.ah11b1['ppm'][i][1])
            b_predicted_ppm.append(self.pred.con.predict(self.ah11b1['ppm'][i][0], 0.11))
            c.append(self.ah11c1['ppm'][i][1])
            c_predicted_ppm.append(self.pred.con.predict(self.ah11c1['ppm'][i][0], 0.11))
            d.append(self.ah11d1['ppm'][i][1])
            d_predicted_ppm.append(self.pred.con.predict(self.ah11d1['ppm'][i][0], 0.11))
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

        put the fully corrected ppm values in the dictionaries
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
            y['cppm'] = cor_ppm  # the dictionary now has corrected ppm values loaded

    def for_plot_cor(self, cap_dict):
        """

        create lists for a capacitor that can be added to plots as required
        :param cap_dict: one of the capacitance dictionaries
        :return:
        """
        time = []  # x axis date
        c_ppm = []  # the raw measured cap value in ppm
        u_ppm = []  # uncertainty in ppm?
        for x in cap_dict['ppm']:
            time.append(self.pred.ah11a1.decimal_date(x[0]))
            c_ppm.append(x[1])
            u_ppm.append(x[2])
        cor_ppm = []
        for x in cap_dict['cppm']:
            cor_ppm.append(x[1])
        return time, c_ppm, cor_ppm, u_ppm

    def out_block(self):
        """

        create a list of lists making up the rows for a simple block of corrected results
        for all the capacitors
        :return:
        """
        output = []
        head_row = ['Date', 'AH11A1', 'AH11B1', 'AH11C1', 'AH11D1','AH11A2', 'AH11B2', 'AH11C2', 'AH11D2',
            'ES14', 'ES13', 'ES16', 'GR10', 'GR100', 'GR1000A', 'GR1000B', 'ES13ES16', 'uAH11A1', u'AH11B1', u'AH11C1',
            'uAH11D1','uAH11A2', 'uAH11B2', 'uAH11C2', 'uAH11D2', 'uES14', 'uES13', 'uES16', 'uGR10', 'uGR100',
            'uGR1000A', 'uGR1000B', 'uES13ES16']
        output.append(head_row)
        for i in range(len(self.ah11a1['cppm'])):
            line = []
            line.append(self.ah11a1['cppm'][i][0])
            for x in self.dicts:
                line.append(self.all_dict[x]['cppm'][i][1])  # corrected ppm
            for x in self.dicts:
                line.append(self.all_dict[x]['cppm'][i][2])  # uncertainty
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
            spec_dict = anal.all_dict[name]  # the specific dictionary
            x, y, z, u = anal.for_plot_cor(spec_dict)
            ax.errorbar(x, z, yerr=u, linestyle=line, fmt='o', capsize=10, color=cmap(count))
            ax.plot(x, z, label=spec_dict['name'] + '_corr', linestyle=line, color=cmap(count))
            count += 1
        fig.set_size_inches(11.69, 8.27)  # A4 landscape
        plt.title(title)
        plt.legend()
        plt.tight_layout()
        plt.savefig(title + '.pdf')
        plt.savefig(title + '.jpg')
        plt.show()

if __name__ == '__main__':
    anal = ANALYSE([
        r'new_datastore\nov2019\summary_main_2021-08-23_a.csv',
        r'new_datastore\dec2020\summary_main_2021-08-27_a.csv',
        r'new_datastore\sep2021\summary_main_2021-09-06_a.csv',
        r'new_datastore\sep2021\summary_main_2021-09-09.csv',
        r'new_datastore\sep2021\summary_main_2021-09-10.csv',
        r'new_datastore\sep2021\summary_main_2021-09-22.csv',
        r'new_datastore\sep2021\summary_main_2021-10-11_b.csv',
        r'new_datastore\June2025\summary_main_2025-07-03.csv',
        r'new_datastore\June2025\summary_main_2025-07-04.csv',
        r'new_datastore\June2025\summary_main_2025-07-07.csv',
        r'new_datastore\June2025\summary_main_2025-07-08.csv'
        ] )
    anal.all_sumry()  # loads the data
    anal.corrected_dict()  # applies constraint of the mean of AH11 set #1
    anal.plot(['AH11A1', 'AH11B1', 'AH11C1', 'AH11D1', 'AH11A2', 'AH11B2', 'AH11C2', 'AH11D2'], 'AH11 set')
    anal.plot( ['ES14', 'ES13', 'ES16', 'GR10', 'GR100', 'GR1000A', 'GR1000B', 'ES13ES16'], 'GR and S ball set')
    out_block = anal.out_block()  # prepares csv-friendly lists
    anal.file_block('test_analysis.csv', out_block)  # writes to csv file
