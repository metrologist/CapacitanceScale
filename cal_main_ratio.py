#  python3.8 som environment
from archive import GTCSTORE, COMPONENTSTORE
from pathlib import Path
import csv
from json import loads
from GTC import ucomplex
from GTC.reporting import budget  # just for checks

"""
Takes results of a Permutable Capacitor run and returns an uncertain complex value for the main 10:1 ratio. 
"""
class PERMUTE(object):
    def __init__(self, file_path, input_file_names, output_file_name):
        self.output_name = output_file_name  # optional store in a csv file
        self.store = GTCSTORE()
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
                elif row[0] == 'factora':
                    self.factora = self.store.json_to_ucomplex(row[1])
                elif row[0] == 'factorb':
                    self.factorb = self.store.json_to_ucomplex(row[1])
                elif row[0] == 'za':
                    self.za = self.store.json_to_ucomplex(row[1])
                elif row[0] == 'ya':
                    self.ya = self.store.json_to_ucomplex(row[1])
                elif row[0] == 'zinta':
                    self.zinta = self.store.json_to_ucomplex(row[1])
                elif row[0] == 'y3':
                    self.y3 = self.store.json_to_ucomplex(row[1])
                elif row[0] == 'y4Y2':
                    self.y4Y2 = self.store.json_to_ucomplex(row[1])
                elif row[0] == 'zb':
                    self.zb = self.store.json_to_ucomplex(row[1])
                elif row[0] == 'yb':
                    self.yb = self.store.json_to_ucomplex(row[1])
                elif row[0] == 'zintb':
                    self.zintb = self.store.json_to_ucomplex(row[1])
                elif row[0] == 'y1':
                    self.y1 = self.store.json_to_ucomplex(row[1])
                elif row[0] == 'y2Y1':
                    self.y2Y1 = self.store.json_to_ucomplex(row[1])
                else:
                    print('This row does not match. Wrong csv file? ', row)
        assert counter == 27, "csv file incorrect length, should be 27 rows:  %r" % counter
        data_in = self.data_folder / input_file_names[1]
        with open(data_in, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0] == 'gr10':
                    cgr10 = loads(row[1])  # a components.CAPACITOR object

        cstore = COMPONENTSTORE()
        admit_GR10 = cstore.dict_to_capacitor(cgr10).best_value  # admittance at 10000 rad/s
        self.GR10 = admit_GR10/(1j * self.w)
        # self.GR10 = 10e-12  # temporary value of GR10 ( to be picked up from csv)
        self.PC = (10.000144 + 10.000304 + 10.000218 + 10.000151 + 10.000200 + 10.000138 + 9.9998906 + 10.000130
                   + 10.000025 + 10.000043 + 10.000277) * 1e-12  # sum of 11 PC capacitors, p.33 of KJ Diary2

    def calc_raw_ratio(self):
        # implement formula 37 and 46 of E.005.03
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

    def correct_ratio(self, uncorrected_ratio):  # equation 45 of E.005.003
        top = 1+self.zb*(self.y2Y1 + (self.yb/2 + self.y1)*(1+self.zintb*self.y2Y1)) + self.zintb*self.y2Y1
        bottom =1+self.za*(self.y4Y2 + (self.ya/2 + self.y3)*(1+self.zinta*self.y4Y2)) + self.zinta*self.y4Y2
        corrected = uncorrected_ratio * top / bottom
        return corrected

    def file_ratio(self, correction):
        output_file = self.data_folder / self.output_name
        with open(output_file, 'w', newline='') as csvfile:
            outwriter = csv.writer(csvfile)
            outwriter.writerow(['Date', self.date_string])
            outwriter.writerow(['Reference', self.reference_string])
            outwriter.writerow([self.store.ucomplex_to_json(correction, new_label='main_ratio')])


if __name__ == '__main__':
    print('Testing cal_main_ratio.py')
    ratio_cal = PERMUTE('G:\\My Drive\\KJ\\PycharmProjects\\CapacitanceScale\\datastore',
                        ['perm.csv', 'leads_and_caps.csv'], 'out_perm.csv')
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


    store = GTCSTORE()
    ratio_for_file = store.ucomplex_to_json(final_ratio, new_label='main_ratio')
    main_ratio = store.json_to_ucomplex(ratio_for_file)
    print('main ratio', repr(main_ratio))
    print('budget')
    for l, u in budget(final_ratio.real, trim=0):
        print(l, u)

    ratio_cal.file_ratio(final_ratio)


    # temporary creation of most likely values for leads etc.
    # will make ucomplex for storage
    # p.90 of KJ Diary 2 has PC values
    # I:\MSL\Private\Electricity\Ongoing\Farad\CalcCap\Cap1997\BU29OC97.XLS has assumed lead values
    # these will do for now, but remeasuring them in future is obviously a good idea.
    angf = ratio_cal.w
    rel_u = 0.05  # nominal 5% error in component measurements
    # lead A
    aR = 6.5128e-2
    aL = 4.269e-7
    za = ucomplex((aR + 1j * angf * aL), (rel_u * aR, rel_u * angf * aL), label='za')
    # print(za)
    aG = 5e-11
    aC = 6.4915e-11
    ya = ucomplex((aG + 1j * angf * aC), (rel_u * aG, rel_u * angf * aC), label='ya')
    # print(ya)
    yR = 2.606e-2
    yL = 2.417e-7
    zinta = ucomplex((yR + 1j * angf * yL), (rel_u * yR, rel_u * angf * yL), label='zinta')
    # print(zinta)
    gppp = 2.09e-10
    cppp = 6.0527e-12
    y3 = ucomplex((gppp + 1j * angf * cppp), (rel_u * gppp, rel_u * angf * cppp), label='y3')
    # print(y3)
    gp = 6.4e-9
    cp = 3.1818e-10  # this is effectively y4 + Y2
    y4Y2 = ucomplex((gp + 1j * angf * cp), (rel_u * gp, rel_u * angf * cp), label='y4Y2')
    # print(y4Y2)

    # lead B
    bR = 6.5498e-2
    bL = 4.330e-7
    zb = ucomplex((bR + 1j * angf * bL), (rel_u * bR, rel_u * angf * bL), label='zb')
    # print(zb)
    bG = 5.0e-11
    bC = 6.438e-11
    yb = ucomplex((bG + 1j * angf * bC), (rel_u * bG, rel_u * angf * bC), label='yb')
    # print(yb)
    xR = 2.417-2
    xL = 2.515e-7
    zintb = ucomplex((xR + 1j * angf * xL), (rel_u * xR, rel_u * angf * xL), label='zintb')
    # print(zintb)
    gppp = 2.09e-10
    cppp = 6.0527e-12
    y1 = ucomplex((gppp + 1j * angf * cppp), (rel_u * gppp, rel_u * angf * cppp), label='y1')
    # print(y1)
    gpp = 7.41e-10
    cpp = 4.0168e-11  # this is effectively y2 + Y1
    y2Y1 = ucomplex((gpp + 1j * angf * cpp), (rel_u * gpp, rel_u * angf * cpp), label='y2Y1')
    # print(y2Y1)

    temp = GTCSTORE()
    for_json = [za, ya, zinta, y3, y4Y2, zb, yb, zintb, y1, y2Y1]  # list of ucomplex
    for_file = []
    for x in for_json:
        for_file.append([x.label, temp.ucomplex_to_json(x)])  # a dictionary of json strings
    # for y in for_file:
    #     print(y, for_file[y] )
    # temp.save_gtc(for_file, 'temp.csv')
