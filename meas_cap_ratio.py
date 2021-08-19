#  python3.9 environment
from archive import GTCSTORE, COMPONENTSTORE
from pathlib import Path
import csv
from components import CAPACITOR, LEAD, CONNECT, PARALLEL
from GTC import ucomplex, ureal
from GTC.reporting import budget  # just for checks
from json import dumps, loads


class CAPSCALE(object):
    def __init__(self, file_path, input_files, output_file_name, ref_value, **kwargs):
        """

        Takes in all the measurement information from the input files and has methods to calculate the values of all the
        capacitors in the buildup based on the assumed value of the reference capacitor.
        :param file_path: the sub-folder that holds all the csv files
        :param input_files: a list of file names for dial factors, 10:1 ratio, leads, capacitors and balance readings
        :param output_file_name: csv file for calculated values of all the capacitors
        :param ref_value is the up to date value of AH11C1 (derived from external calibration history)
        :param kwargs: allows values of 'afactor', 'bfactor' and 'ratio' to be entered directly rather than extracted
        from the input files. This is used when the whole buildup calculation is done in a single run in main.py
        """
        self.ref_cap = ref_value
        self.output_name = output_file_name  # optional store in a csv file
        self.store = GTCSTORE()
        self.storecomp = COMPONENTSTORE()
        self.data_folder = Path(file_path)
        data_in = self.data_folder / input_files[0]
        self.data_out = self.data_folder / output_file_name
        self.r = 1e-4  # ratio with 100:1 injection transformer
        with open(data_in, newline='') as csvfile:  # format must be correct
            reader = csv.reader(csvfile)
            counter = 0
            self.balance_dict = {}
            ratios = ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15']
            for row in reader:
                counter += 1
                if row[0] == 'Date':
                    self.date_string = row[1]
                elif row[0] == 'Reference':
                    self.reference_string = row[1]
                elif row[0] == 'w':  # radians per second
                    self.w = float(row[1])
                elif row[0] in ratios:  # each build up ratio has an (alpha, beta) tuple
                    self.balance_dict[row[0]] = (float(row[1]), float(row[2]))
                elif row[0] == 'factora':
                    self.factora = self.store.json_to_ucomplex(row[1])
                elif row[0] == 'factorb':
                    self.factorb = self.store.json_to_ucomplex(row[1])
                elif row[0] == 'main_ratio':
                    self.main_ratio = self.store.json_to_ucomplex(row[1])
                else:
                    print('This row does not match. Wrong csv file? ', row)
        # next load in all the lead and capacitor objects
        data_in = self.data_folder / input_files[1]
        cap_list = ['ah11a1', 'ah11b1', 'ah11c1', 'ah11d1', 'ah11a2', 'ah11b2', 'ah11c2', 'ah11d2', 'es14', 'es13',
                    'es16',
                    'gr10', 'gr100', 'gr1000a', 'gr1000b', 'es13_16']
        lead_list = ['hv1', 'hv2', 'lv1', 'lv2', 'xfrm', 'hv1_xfrm', 'hv2_xfrm', 'no_lead']
        self.caps = {}
        self.leads = {}
        with open(data_in, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0] in cap_list:
                    item = loads(row[1])
                    item = self.storecomp.dict_to_capacitor(item)
                    self.caps[row[0]] = item
                elif row[0] in lead_list:
                    item = loads(row[1])
                    item = self.storecomp.dict_to_lead(item)
                    self.leads[row[0]] = item
        # allows key values to override those supplied from the input csv
        for arg in kwargs.keys():
            if arg == 'afactor':
                self.factora = kwargs[arg]
            if arg == 'bfactor':
                self.factorb = kwargs[arg]
            if arg == 'ratio':
                self.main_ratio = kwargs[arg]

    def cap_ratio(self, balance, cap, inverse):
        """

        Equation 46,47 of E.005.003
        :param balance: the tuple of balance dial values
        :param cap: the 'known' capacitor in the ratio
        :param inverse: boolean when true to divide capacitor by the ratio
        :return: the 'known' capacitor value either multiplied or divided by the measured ratio
        """

        ratio = self.main_ratio * 1 / (1 + self.r * (balance[0] * self.factora + 1j * balance[1] * self.factorb))
        if inverse:
            return cap / ratio
        else:
            return cap * ratio

    def sum_ratio(self, bal1, bal2, sum_val):
        """

        Calculates the value of the two 5 pF capacitors (ES 13 and ES16) from knowing the value of the two in parallel
        and their difference in ratio when individually balanced against the 0.5 pF (ES14). Equations 19 to 21 of
        E.005.003. Preferred method is sum_ratio2 that includes the effect of connecting to the injection transformer.
        :param bal1: ratio ES14/ES13
        :param bal2: ratio ES14/ES16
        :param sum_val: the value of the two capacitors in parallel
        :return: value of ES13, ES16 and ES14
        """
        ratio1 = 1 / (self.main_ratio * 1 / (1 + self.r * (bal1[0] * self.factora + 1j * bal1[1] * self.factorb)))
        ratio2 = 1 / (self.main_ratio * 1 / (1 + self.r * (bal2[0] * self.factora + 1j * bal2[1] * self.factorb)))
        c13 = ratio2 / (ratio1 + ratio2) * sum_val
        c16 = ratio1 / (ratio1 + ratio2) * sum_val
        c14 = (ratio1 * ratio2) / (ratio1 + ratio2) * sum_val
        return c13, c16, c14

    def sum_ratio2(self, bal1, bal2, sum_val, cap1, cap2, com_lead):
        """

        Calculates the value of the two 5 pF capacitors (ES13 and ES16) from knowing the value of the two in parallel
        and their difference in ratio when individually balanced against the 0.5 pF (ES14). The 5 pF capacitors connect
        directly to the HV side when measured against a 100 pF capacitor, but are on the LV side with the injection
        transformer (xfrm LEAD) when being compared to the 0.5 pF capacitor. E005.003 does not have these formulae.
        :param bal1: ratio ES14/ES13
        :param bal2: ratio ES14/ES16
        :param sum_val: the value of the two capacitors in parallel
        :param cap1: one of the 5 pF CAPACITOR object ES13
        :param cap2: the other of the 5 pF CAPACITOR objects ES16
        :param com_lead: the additional common lead when the two 5 pF caps are paralleled on the low voltage side
        :return: value of ES13, ES16 and ES14
        """
        ratio1 = 1 / (self.main_ratio * 1 / (1 + self.r * (bal1[0] * self.factora + 1j * bal1[1] * self.factorb)))
        ratio2 = 1 / (self.main_ratio * 1 / (1 + self.r * (bal2[0] * self.factora + 1j * bal2[1] * self.factorb)))
        lead_13 = cap1.lead_correction(com_lead, self.leads['no_lead'])  # lead correction for ES13 on LV injection
        lead_16 = cap2.lead_correction(com_lead, self.leads['no_lead'])  # lead correction for ES16 on LV injection
        c13 = ratio2 / (ratio1 + ratio2) * (sum_val + ratio1 / ratio2 * lead_13 - lead_16)
        c16 = ratio1 / (ratio1 + ratio2) * (sum_val + ratio2 / ratio1 * lead_16 - lead_13)
        c14 = (ratio1 * ratio2) / (ratio1 + ratio2) * (sum_val + ratio1 / ratio2 * lead_13 - lead_16) - ratio1 * lead_13
        return c13, c16, c14

    def buildup(self):
        """

        This calculation strictly follows the buildup described in MSLT.E.005.03 where each of the ratio measurements
        r1...r13 is defined. Any change such as the choice of leads or choice of reference capacitor, will need a new
        method. It would be best to add methods named, e.g., buildup_2002() rather than to edit this method. Ultimately
        it should be possible to use **kwargs to manage alternative buildups.
        :return: a dictionary of CAPACITOR objects with new 'best values' set.
        """
        hv2 = self.leads['hv2']
        lv2 = self.leads['lv2']
        hv1 = self.leads['hv1']
        lv1 = self.leads['lv1']
        xfrm = self.leads['xfrm']
        hv2_xfrm = CONNECT(xfrm, hv2)  # hv2 lead connected to 100:1 transformer
        no_lead = self.leads['no_lead']
        # start with the best value for c1 (from certificate)
        self.caps['ah11c1'].set_best_value(self.ref_cap)
        c1 = self.caps['ah11c1'].best_value - self.caps['ah11c1'].lead_correction(hv2_xfrm,
                                                                                  lv2)  # measured C slightly larger
        r4 = self.balance_dict['r4']
        a1 = self.cap_ratio(r4, c1, True)
        self.caps['ah11a1'].set_best_value(a1 + self.caps['ah11a1'].lead_correction(hv1, lv1))  # value with no leads
        r5 = self.balance_dict['r5']
        b1 = self.cap_ratio(r5, c1, True)
        self.caps['ah11b1'].set_best_value(b1 + self.caps['ah11b1'].lead_correction(hv1, lv1))  # value with no leads
        r6 = self.balance_dict['r6']
        a2 = self.cap_ratio(r6, c1, True)
        self.caps['ah11a2'].set_best_value(a2 + self.caps['ah11a2'].lead_correction(hv1, lv1))  # value with no leads
        r7 = self.balance_dict['r7']
        b2 = self.cap_ratio(r7, c1, True)
        self.caps['ah11b2'].set_best_value(b2 + self.caps['ah11b2'].lead_correction(hv1, lv1))  # value with no leads
        r8 = self.balance_dict['r8']
        g10 = self.cap_ratio(r8, c1, True)
        self.caps['gr10'].set_best_value(
            g10 + self.caps['gr10'].lead_correction(no_lead, no_lead))  # value with no leads

        # shift to AH11A1 as the reference to put values on all the 100 pF capacitors
        ref2 = self.caps['ah11a1'].best_value - self.caps['ah11a1'].lead_correction(hv1, lv1)
        r9 = self.balance_dict['r9']
        c100 = self.cap_ratio(r9, ref2, False)  # cross check with c1 for build up consistency
        r10 = self.balance_dict['r10']
        d1 = self.cap_ratio(r10, ref2, False)
        self.caps['ah11d1'].set_best_value(
            d1 + self.caps['ah11d1'].lead_correction(hv2_xfrm, lv2))  # value with no leads
        r11 = self.balance_dict['r11']
        c2 = self.cap_ratio(r11, ref2, False)
        self.caps['ah11c2'].set_best_value(
            c2 + self.caps['ah11c2'].lead_correction(hv2_xfrm, lv2))  # value with no leads
        r12 = self.balance_dict['r12']
        d2 = self.cap_ratio(r12, ref2, False)
        self.caps['ah11d2'].set_best_value(
            d2 + self.caps['ah11d2'].lead_correction(hv2_xfrm, lv2))  # value with no leads
        r13 = self.balance_dict['r13']
        g100 = self.cap_ratio(r13, ref2, False)
        self.caps['gr100'].set_best_value(
            g100 + self.caps['gr100'].lead_correction(xfrm, no_lead))  # value with no leads

        # change the leads on AH11C1 as they no longer include the 100:1 transformer
        # same ah11c1 capacitor different lead corrections
        ref3 = self.caps['ah11c1'].best_value - self.caps['ah11c1'].lead_correction(hv2, lv2)
        r14 = self.balance_dict['r14']
        g1000a = self.cap_ratio(r14, ref3, False)
        self.caps['gr1000a'].set_best_value(
            g1000a + self.caps['gr1000a'].lead_correction(xfrm, no_lead))  # value with no leads
        r15 = self.balance_dict['r15']
        g1000b = self.cap_ratio(r15, ref3, False)
        self.caps['gr1000b'].set_best_value(
            g1000b + self.caps['gr1000b'].lead_correction(xfrm, no_lead))  # value with no leads

        # work down to 0.5 pF
        r3 = self.balance_dict['r3']
        e1316 = self.cap_ratio(r3, c1, True)
        self.caps['es13_16'].set_best_value(e1316)  # no transformer connection
        r1 = self.balance_dict['r1']
        r2 = self.balance_dict['r2']
        # c13, c16, c14 = self.sum_ratio(r1, r2, e1316)
        c13_2, c16_2, c14_2 = self.sum_ratio2(r1, r2, e1316, self.caps['es13'], self.caps['es16'], self.leads['xfrm'])
        # print('c13', c13)
        # print('c13_2', c13_2)
        # print('c14', c14)
        # print('c14_2', c14_2)
        # print('c16', c16)
        # print('c16_2', c16_2)
        self.caps['es13'].set_best_value(c13_2)
        self.caps['es16'].set_best_value(c16_2)
        self.caps['es14'].set_best_value(c14_2)
        return self.caps

    def store_buildup(self):
        """

        Stores the capacitor name, capacitor best value in pF and CAPACITOR object in the output csv file.
        :return: saves the output file.
        """
        with open(self.data_out, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for x in self.caps:
                y = self.storecomp.capacitor_to_dict(self.caps[x])
                simple = loads(y['best_value'])  # json string to dictionary
                simple = self.store.dict_to_ucomplex(simple)  # to ucomplex
                simple_i = simple / (1j * self.w)  # extracting capacitance from admittance
                z = simple_i.real * 1e12  # and putting it in units of pF
                writer.writerow([x, z, dumps(y)])


if __name__ == '__main__':
    print('Derive ah11a1 from ah11c1 using balance r4')
    w = 1e4  # rad/s
    cap = 99.999581e-12  # pF
    ucap = 0.11e-6  # relative expanded uncertainty, k = 2
    dfact = 1.9e-6  # dissipation factor S/F/Hz
    udfact = 0.6e-6  # S/F/Hz, k=2
    g = ureal(dfact * w * cap, udfact / 2 * w * cap, 50, label='ah11c1d')
    c = ureal(cap, cap * ucap / 2, 50, label='ah11c1c')
    cert = g + 1j * w * c  # admittance of reference at angular frequency w
    print('reference value for buildup =', cert)
    final_ratio = ucomplex(10.00001763921027 + 1j * -0.0001684930432066416, (1e-10, 1e-10), df=100, label="main_ratio")
    factora = ucomplex(1.0003093210681406 + 1j * 0.0007497042903003306, (1e-10, 1e-10), df=100, label='factora')
    factorb = ucomplex(1.0001942917392947 + 1j * -0.00023893092658472306, (1e-10, 1e-10), df=100, label='factorb')
    buildup = CAPSCALE(r'G:\My Drive\KJ\PycharmProjects\CapacitanceScale\datastore_improv',
                       [r'in3.csv', r'leads_and_caps.csv'], r'out3.csv', cert,
                       afactor=factora, bfactor=factorb, ratio=final_ratio)
    print('reference from CAPSCALE', buildup.ref_cap)
    ah11c1 = buildup.caps['ah11c1']
    ah11c1.set_best_value(cert)  # force the value to cert (but doesn't change in leads_and_caps.csv
    best = ah11c1.best_value.imag.x
    print('reference used', best)
    not_best = cert.imag.x
    print('cert value', not_best)
    hv2_xfrm = buildup.leads['hv2_xfrm']
    lv2 = buildup.leads['lv2']
    hv1 = buildup.leads['hv1']
    lv1 = buildup.leads['lv1']
    balances = buildup.balance_dict
    r4 = balances['r4']
    a1 = buildup.cap_ratio(r4, ah11c1.best_value - ah11c1.lead_correction(hv2_xfrm, lv2), True)
    buildup.caps['ah11a1'].set_best_value(a1 + buildup.caps['ah11a1'].lead_correction(hv1, lv1))  # value with no leads
    print('ah11a1', buildup.caps['ah11a1'].best_value.imag.x)
