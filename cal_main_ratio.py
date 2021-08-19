#  python 3.9 environment
from archive import COMPONENTSTORE
from pathlib import Path
import csv
from json import loads
from GTC import ucomplex
from GTC.reporting import budget  # just for checks

class PERMUTE(object):
    def __init__(self, file_path, input_file_names, output_file_name, **kwargs):
        """

        Takes the balance values of a Permutable Capacitor run and returns an uncertain complex value for the main
        10:1 ratio.
        :param file_path: working directlory
        :param input_file_names: list of csv files, order sensitive, [balances s1 ... s12, leads and caps, cal factors
        for the main dial (factora, factorb), model compenents as ucomplex impedance/admittance and values in pF of
        each of the 11 capacitors]
        :param output_file_name:
        :param kwargs:  'afactor' and 'bfactor to overide any csv file input values for factora and factorb (redundant?)
        """
        self.output_name = output_file_name  # optional store in a csv file
        self.store = COMPONENTSTORE()
        self.data_folder = Path(file_path)
        self.r = 0.0001  # for 10:1 transformer injection through 10 pF
        data_in = self.data_folder / input_file_names[0]
        with open(data_in, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            counter = 0
            self.balance_dict = {}
            switches = ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 's12']
            for row in reader:
                counter += 1
                if row[0] == 'Date':
                    self.date_string = row[1]
                elif row[0] == 'Reference':
                    self.reference_string = row[1]
                elif row[0] == 'w':  # radians per second
                    self.w = float(row[1])
                elif row[0] in switches:  # each switch setting has an (alpha, beta) tuple
                    self.balance_dict[row[0]] = (float(row[1]), float(row[2]))

        data_in = self.data_folder / input_file_names[2]
        with open(data_in, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0] == 'factora':
                    self.factora = self.store.gs.json_to_ucomplex(row[1])
                elif row[0] == 'factorb':
                    self.factorb = self.store.gs.json_to_ucomplex(row[1])

        data_in = self.data_folder / input_file_names[3]
        pc = ['pc1', 'pc2', 'pc3', 'pc4', 'pc5', 'pc6', 'pc7', 'pc8', 'pc9', 'pc10', 'pc11']
        pc_dict = {}
        with open(data_in, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0] in pc:
                    pc_dict[row[0]] = row[1]
                elif row[0] == 'za':
                    self.za = self.store.gs.json_to_ucomplex(row[1])
                elif row[0] == 'ya':
                    self.ya = self.store.gs.json_to_ucomplex(row[1])
                elif row[0] == 'zinta':
                    self.zinta = self.store.gs.json_to_ucomplex(row[1])
                elif row[0] == 'y3':
                    self.y3 = self.store.gs.json_to_ucomplex(row[1])
                elif row[0] == 'y4Y2':
                    self.y4Y2 = self.store.gs.json_to_ucomplex(row[1])
                elif row[0] == 'zb':
                    self.zb = self.store.gs.json_to_ucomplex(row[1])
                elif row[0] == 'yb':
                    self.yb = self.store.gs.json_to_ucomplex(row[1])
                elif row[0] == 'zintb':
                    self.zintb = self.store.gs.json_to_ucomplex(row[1])
                elif row[0] == 'y1':
                    self.y1 = self.store.gs.json_to_ucomplex(row[1])
                elif row[0] == 'y2Y1':
                    self.y2Y1 = self.store.gs.json_to_ucomplex(row[1])

        data_in = self.data_folder / input_file_names[1]
        with open(data_in, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0] == 'gr10':
                    cgr10 = loads(row[1])  # a components.CAPACITOR object
        # temporary alternative ...
        for arg in kwargs.keys():
            if arg == 'afactor':
                self.factora = kwargs[arg]
            if arg == 'bfactor':
                self.factorb = kwargs[arg]

        cstore = COMPONENTSTORE()  # to access COMPONENTSTORE methods
        admit_GR10 = cstore.dict_to_capacitor(cgr10).best_value  # admittance at 10000 rad/s
        self.GR10 = admit_GR10/(1j * self.w)
        pcsum=0
        for x in pc_dict:
            pcsum = pcsum + float(pc_dict[x])
        self.PC = pcsum * 1e-12

    def calc_raw_ratio(self):
        """

        Implements equations 37 and 46 of E.005.03
        :return: 10:1 voltage ratio as calculated before correcting for lead and internal impedance effects
        """
        d = []  # list of corrected balance dials as ucomplex
        for x in self.balance_dict:  # build the list of corrected complex value balances
            if x != 's12':  # repeat of s1 (i.e. s12) is not used for calculation
                alpha = self.balance_dict[x][0]
                beta = self.balance_dict[x][1]
                d.append(self.factora * alpha + 1j * self.factorb * beta)  # complex value with corrected alpha and beta
        assert len(d) == 11, "do not have 11 balance values: %r" % len(d)
        dsum = 0  # the sum of the complex value balances
        for x in d:
            dsum = dsum + x
        raw_ratio = (11-1)/(1 + (self.GR10/self.PC) * dsum * self.r)  # 0.0001 accounts for injection ratio
        return raw_ratio

    def correct_ratio(self, uncorrected_ratio):
        """

        Implements equation 45 of E.005.003, applying the correction for the external leads and internal components
        of the permutable capacitor model.
        :param uncorrected_ratio:
        :return:
        """
        top = 1 + self.zb*(self.y2Y1 + (self.yb/2 + self.y1)*(1+self.zintb*self.y2Y1)) + self.zintb*self.y2Y1
        bottom = 1 + self.za*(self.y4Y2 + (self.ya/2 + self.y3)*(1+self.zinta*self.y4Y2)) + self.zinta*self.y4Y2
        corrected = uncorrected_ratio * top / bottom
        return corrected

    def file_ratio(self, corrected_ratio):
        """

        Stores a ucomplex value of the 10:1 ratio in the csv output file
        :param corrected_ratio: ucomplex value of the 10:1 ratio
        :return: ratio is stored in the output files together with meta data
        """
        output_file = self.data_folder / self.output_name
        with open(output_file, 'w', newline='') as csvfile:
            outwriter = csv.writer(csvfile)
            outwriter.writerow(['Date', self.date_string])
            outwriter.writerow(['Reference', self.reference_string])
            outwriter.writerow([self.store.gs.ucomplex_to_json(corrected_ratio, new_label='main_ratio')])


if __name__ == '__main__':
    print('Testing cal_main_ratio.py')
    ratio_cal = PERMUTE('G:\\My Drive\\KJ\\PycharmProjects\\CapacitanceScale\\data_store_test',
                        ['perm2.csv', 'leads_and_caps.csv', 'out_test3.csv', 'comp_permute.csv'], 'out_perm2.csv')
    print(ratio_cal.balance_dict)
    raw_ratio = ratio_cal.calc_raw_ratio()
    print(repr(raw_ratio))
    print((raw_ratio/10-1) * 1e6)
    print('budget')
    for l, u in budget(raw_ratio.real, trim=0):
        print(l, u)
    main_ratio = ratio_cal.correct_ratio(raw_ratio)
    print(main_ratio)
    final_ratio = ratio_cal.correct_ratio(main_ratio)
    print('final ratio ', repr(final_ratio))

    store = ratio_cal.store
    ratio_for_file = store.gs.ucomplex_to_json(final_ratio, new_label='main_ratio')
    main_ratio = store.gs.json_to_ucomplex(ratio_for_file)
    print('main ratio', repr(main_ratio))
    print('budget')
    for l, u in budget(final_ratio.real, trim=0):
        print(l, u)

    ratio_cal.file_ratio(final_ratio)
