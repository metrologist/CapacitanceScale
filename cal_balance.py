#  python3.9
"""
Calibrates the dials used for the alpha and beta values of all ratio measurements.

"""
from archive import GTCSTORE, COMPONENTSTORE
from pathlib import Path
import csv
from json import loads
from GTC import ureal
from GTC.reporting import budget  # just for checks

class DIALCAL(object):
    def __init__(self, file_path, input_file_names, output_file_name):
        """
        Calibration of the main balance amplifier requires two sets of input data. The first set primarily balances the
        alpha dial at full scale. The second set primarily balances the beta dial at full scale. Calibration is at the
        single frequency of 10000 radians per second. See Appendix A1 of E.005.03.
        Each data set comprises

        k: the setting of the 7 dial IVD
        r: the ratio of the injection transformer used
        Y1: the capacitor connected to the 7 dial IVD
        Y2 or Y3: the capacitor or resistor connected to the balance dials (alpha at 1, beta at 1 respectively)
        alpha and beta dial settings for balance

        :param file_path: directory for data in/out
        :param input_file_names: list of csv files [dial settings and component names, components]
        :param output_file_name: output can be stored in this csv file (same directory)
        """
        self.output_name = output_file_name  # optional store in a csv file
        self.store = GTCSTORE()
        self.data_folder = Path(file_path)
        data_in = self.data_folder / input_file_names[0]
        label_y3 = 'y3 label not in csv file'  # avoiding 'label_y3 referenced before assignment' error
        with open(data_in, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            counter = 0
            for row in reader:
                counter += 1
                if row[0] == 'Date':
                    self.date_string = row[1]
                elif row[0] == 'Reference':
                    self.reference_string = row[1]
                elif row[0] == 'w':  # radians per second
                    self.w = float(row[1])
                elif row[0] == 'alpha1':  # with Y2
                    self.alpha1 = self.store.json_to_ureal(row[1])
                elif row[0] == 'beta1':  # with Y2
                    self.beta1 = self.store.json_to_ureal(row[1])
                elif row[0] == 'alpha2':  # with Y3
                    self.alpha2 = self.store.json_to_ureal(row[1])
                elif row[0] == 'beta2':  # with Y3
                    self.beta2 = self.store.json_to_ureal(row[1])
                elif row[0] == 'r':  # injection transformer ratio
                    self.r = float(row[1])
                elif row[0] == 'k':  # 7 dial IVD setting
                    self.k = float(row[1])
                elif row[0] == 'c1':
                    c1 = row[1]  #self.store.json_to_ucomplex(row[1])
                elif row[0] == 'c2':
                    c2 = row[1]  #self.store.json_to_ucomplex(row[1])
                elif row[0] == 'label z3':
                    label_y3 = row[1]
                elif row[0] == 'r3':
                    r3 = float(row[1])
                elif row[0] == 'ur3':
                    ur3 = float(row[1])
                elif row[0] == 'c3':
                    c3 = float(row[1])
                elif row[0] == 'uc3':
                    uc3 = float(row[1])
                else:
                    print('This row does not match. Wrong csv file? ', row)
        assert counter == 16, "csv file incorrect length, should be 16 rows:  %r" % counter
        # get the latest values of c1 and c2 from 'leads_and_caps.csv'
        data_in = self.data_folder / input_file_names[1]
        with open(data_in, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0] == c1:
                    c1 = row[1]
                elif row[0] == c2:
                    c2 = row[1]
        cstore = COMPONENTSTORE()
        r3 = ureal(r3, ur3, label=label_y3 + 'r3_resistance')
        c3 = ureal(c3, uc3, label=label_y3 + 'r3_capacitance')
        self.Y1 = cstore.dict_to_capacitor(loads(c1)).best_value  # loads(c1) is a components.CAPACITOR object
        self.Y2 = cstore.dict_to_capacitor(loads(c2)).best_value  # loads(c1) is a components.CAPACITOR object
        self.Y3 = 1 / r3 + 1j * self.w * c3  # G + jwC form

    def dialfactors(self, **kwargs):
        """
        This contains the critical calculation.

        :param kwargs: booleans file_output and append give a choice on whether to produce a file, either append or new
        :return: returns the two uncertain complex values of the two dial factors
        """
        file_output = False
        behaviour = 'w'
        append = False  # to write a new csv file
        for arg in kwargs.keys():
            if arg == 'file_output':
                file_output = kwargs[arg]
            if arg == 'append':
                append = kwargs[arg]
        x = self.k / (1e-2 * self.r) * (self.Y1 / self.Y2)
        y = self.k / (1e-2 * self.r) * (self.Y1 / self.Y3)
        # equation 38 of E.005.003
        a = (self.beta2 * x - self.beta1 * y) / (self.alpha1 * self.beta2 - self.alpha2 * self.beta1)
        b = -1j * (self.alpha2 * x - self.alpha1 * y) / (self.alpha2 * self.beta1 - self.alpha1 * self.beta2)
        if file_output:
            data_out = self.data_folder / self.output_name
            if append:
                behaviour = 'a'
            with open(data_out, behaviour, newline='') as csvfile:
                outwriter = csv.writer(csvfile)
                outwriter.writerow(['Date', self.date_string])
                outwriter.writerow(['Reference', self.reference_string])
                outwriter.writerow(['factora', self.store.ucomplex_to_json(a, new_label='factora')])
                outwriter.writerow(['factorb', self.store.ucomplex_to_json(b, new_label='factorb')])
        return a, b


if __name__ == '__main__':
    print('Testing cal_balance.py')
    cal_dials = DIALCAL('G:\\My Drive\\KJ\\PycharmProjects\\CapacitanceScale\\datastore_12_2020',
                        ['test3.csv', 'leads_and_caps.csv'], 'out_test3.csv')
    factora, factorb = cal_dials.dialfactors(file_output=True, append=False)
    print('factora', factora, type(factora))
    print('factorb', factorb, type(factorb))
    keith = factora.imag
    print(repr(keith))
    print('budget')
    print(factorb.imag)
    print(factorb.imag.u)
    for l, u in budget(factorb.imag, trim=0):
        print(l, u)
