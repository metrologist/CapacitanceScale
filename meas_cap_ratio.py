#  python3.8 som environment
from archive import GTCSTORE, COMPONENTSTORE
from pathlib import Path
import csv
from components import CAPACITOR, LEAD, CONNECT, PARALLEL
from GTC import ucomplex
from GTC.reporting import budget  # just for checks
from json import dumps, loads

class CAPSCALE(object):
    def __init__(self, file_path, input_files, output_file_name, ref_value):
        """

        :param file_path: the subfolder that holds all the csv files
        :param input_files: a list of file names for dial factors, 10:1 ratio, leads, capacitors and balance readings
        :param output_file_name: csv file for calculated values of all the capacitors
        :param ref_value is the up to date value of AH11C1 (derived from external calibration history)
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
        assert counter == 21, "csv file incorrect length, should be 21 rows:  %r" % counter
        # next load in all the lead and capacitor objects
        data_in = self.data_folder / input_files[1]
        cap_list = ['ah11a1', 'ah11b1', 'ah11c1', 'ah11d1', 'ah11a2', 'ah11b2', 'ah11c2', 'ah11d2', 'es14', 'es13',
                    'es16',
                    'gr10', 'gr100', 'gr1000a', 'gr1000b', 'es13_16']
        lead_list = ['hv1', 'hv2', 'lv2', 'xfrm', 'hv1_xfrm', 'hv2_xfrm', 'no_lead']
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

    def cap_ratio(self, balance, cap, inverse):
        # equation 47 of E.005.003
        ratio = self.main_ratio * 1 / (1 + self.r * (balance[0] * self.factora + 1j * balance[1] * self.factorb))
        if inverse:
            return cap / ratio
        else:
            return cap * ratio

    def sum_ratio(self, bal1, bal2, sum):
        """

        :param bal1:
        :param bal2:
        :param sum:
        :return:
        """
        ratio1 = 1/((self.main_ratio) * 1 / (1 + self.r * (bal1[0] * self.factora + 1j * bal1[1] * self.factorb)))
        ratio2 = 1/((self.main_ratio) * 1 / (1 + self.r * (bal2[0] * self.factora + 1j * bal2[1] * self.factorb)))
        c13 = ratio2 / (ratio1 + ratio2) * sum
        c16 = ratio1 / (ratio1 + ratio2) * sum
        c14 = (ratio1 * ratio2) / (ratio1 + ratio2) * sum
        return c13, c16, c14

    def buildup(self):
        # start with the best value for c1 (from certificate)
        self.caps['ah11c1'].set_best_value(self.ref_cap)
        c1 = self.caps['ah11c1'].best_value - self.caps['ah11c1'].lead_correction()  # measured C slightly larger
        r4 = self.balance_dict['r4']
        a1 = self.cap_ratio(r4, c1, True)
        self.caps['ah11a1'].set_best_value(a1 + self.caps['ah11a1'].lead_correction())  # value with no leads
        r5 = self.balance_dict['r5']
        b1 = self.cap_ratio(r5, c1, True)
        self.caps['ah11b1'].set_best_value(b1 + self.caps['ah11b1'].lead_correction())  # value with no leads
        r6 = self.balance_dict['r6']
        a2 = self.cap_ratio(r6, c1, True)
        self.caps['ah11a2'].set_best_value(a2 + self.caps['ah11a2'].lead_correction())  # value with no leads
        r7 = self.balance_dict['r7']
        b2 = self.cap_ratio(r7, c1, True)
        self.caps['ah11b2'].set_best_value(b2 + self.caps['ah11b2'].lead_correction())  # value with no leads
        r8 = self.balance_dict['r8']
        g10 = self.cap_ratio(r8, c1, True)
        self.caps['gr10'].set_best_value(g10 + self.caps['gr10'].lead_correction())  # value with no leads

        # shift to AH11A1 as the reference to put values on all the 100 pF capacitors
        ref2 = self.caps['ah11a1'].best_value - self.caps['ah11a1'].lead_correction()
        r9 = self.balance_dict['r9']
        c100 = self.cap_ratio(r9, ref2, False)  # cross check with c1 for build up consistency
        r10 = self.balance_dict['r10']
        d1 = self.cap_ratio(r10, ref2, False)
        self.caps['ah11d1'].set_best_value(d1 + self.caps['ah11d1'].lead_correction())  # value with no leads
        r11 = self.balance_dict['r11']
        c2 = self.cap_ratio(r11, ref2, False)
        self.caps['ah11c2'].set_best_value(c2 + self.caps['ah11c2'].lead_correction())  # value with no leads
        r12 = self.balance_dict['r12']
        d2 = self.cap_ratio(r12, ref2, False)
        self.caps['ah11d2'].set_best_value(d2 + self.caps['ah11d2'].lead_correction())  # value with no leads
        r13 = self.balance_dict['r13']
        g100 = self.cap_ratio(r13, ref2, False)
        self.caps['gr100'].set_best_value(g100 + self.caps['gr100'].lead_correction())  # value with no leads

        # shift to AH11C1_no_xfrm as the reference to put values on all the 1000 pF capacitors
        ah11c1_nox = self.caps['ah11c1']
        ah11c1_nox.set_new_leads(self.leads['hv2'], self.leads['hv1'])  # leads without transformer
        ref3 = ah11c1_nox.best_value - ah11c1_nox.lead_correction()  # same ah11c1 capacitor different lead corrections
        r14 = self.balance_dict['r14']
        g1000a = self.cap_ratio(r14, ref3, False)
        self.caps['gr1000a'].set_best_value(g1000a + self.caps['gr1000a'].lead_correction())  # value with no leads
        r15 = self.balance_dict['r15']
        g1000b = self.cap_ratio(r15, ref3, False)
        self.caps['gr1000b'].set_best_value(g1000b + self.caps['gr1000b'].lead_correction())  # value with no leads

        # work down to 0.5 pF
        r3 = self.balance_dict['r3']
        e1316 = self.cap_ratio(r3, c1, True)
        # print('es1316 ', e1316.imag * 1e8)
        self.caps['es13_16'].set_best_value(e1316)  # no transformer connection
        r1 = self.balance_dict['r1']
        r2 = self.balance_dict['r2']
        c13, c16, c14 = self.sum_ratio(r1, r2, e1316)
        # print('answer', (c13.imag * 1e8 / 5 - 1) * 1e6, (c16.imag * 1e8 / 5 - 1) * 1e6,
        #       (c14.imag * 1e8 / 0.5 - 1) * 1e6)
        self.caps['es13'].set_best_value(c13)
        self.caps['es16'].set_best_value(c16)
        self.caps['es14'].set_best_value(c14)

        return

    def store_buildup(self):

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
    scale = CAPSCALE('G:\\My Drive\\KJ\\PycharmProjects\\CapacitanceScale\\datastore',
                     ['in.csv', 'leads_and_caps.csv'], 'out.csv')
    # for b in scale.balance_dict:
    #     x = scale.cap_ratio(scale.balance_dict[b], 0.5 * (1 + 94e-6), 3)
    #     print(x)
    scale.buildup()

    # let's do a pseudo build up starting with ES14 = +94.445 ppm
    ES14 = 0.5 * (1 + 94.445e-6)
    ES13 = scale.cap_ratio(scale.balance_dict['r1'], ES14, 3)
    print('ES13 ', (ES13.real/5-1)*1e6)
    ES16 = scale.cap_ratio(scale.balance_dict['r2'], ES14, 3)
    print('ES16 ', (ES16.real/5-1)*1e6)
    print('ES13+ES16',((ES13.real+ES16.real)/10-1)*1e6)
    AH11C1 = scale.cap_ratio(scale.balance_dict['r3'], ES13 + ES16, 3)
    print('AH11C1 ', (AH11C1.real / 100 - 1) * 1e6)
    for l, u in budget(AH11C1.real, trim=0):
        print(l, u)

    # this confirms the basic formulas make sense
    # next look at how to handle the capacitor and lead classes
    # create the components to be used in the build up
    # ideally from a csv file once everything is tested
    print('\n', 'Full build up')
    w = 1e4
    relu = 0.01
    hv1 = LEAD('ah11hv1', (286e-3, 0.782e-6), (0.28e-9, 255.2e-12), w, 0.05)
    lv1 = LEAD('ah11lv1', (302e-3, 0.616e-6), (0.20e-9, 93.6e-12), w, 0.05)
    hv2 = LEAD('ah11hv2', (160e-3, 0.830e-6), (0.30e-9, 260.6e-12), w, 0.05)
    lv2 = LEAD('ah11lv2', (273e-3, 1.101e-6), (0.36e-9, 169.8e-12), w, 0.05)
    no_lead = LEAD('no lead', (0, 0), (0, 0), w, 0.05)  # use as default when no leads are required
    xfrm = LEAD('100 to 1', (3.7e-2, 8.1e-7), (3.4e-10, 5.24e-11), w, 0.05)
    hv2_xfrm = CONNECT(xfrm, hv2)  # for when hv2 connects to the injection transformer
    hv1_xfrm = CONNECT(xfrm, hv1)  # for when hv1 connects to the injection transformer

    ah11a1 = CAPACITOR('AH11A1', (0.0, 10e-12), (1.62e-9, 84.2e-12), (0.72e-9, 120.8e-12), w, hv1, lv1, relu)
    ah11b1 = CAPACITOR('AH11B1', (0.0, 10e-12), (2.48e-9, 83.6e-12), (0.70e-9, 117.5e-12), w, hv1, lv1, relu)
    ah11c1 = CAPACITOR('AH11C1', (0.0, 100e-12), (2.06e-9, 104.1e-12), (0.57e-9, 87.7e-12), w, hv2_xfrm, lv2, relu)
    ah11d1 = CAPACITOR('AH11D1', (0.0, 100e-12), (2.15e-9, 100.2e-12), (1.04e-9, 93.9e-12), w, hv2_xfrm, lv2, relu)
    ah11a2 = CAPACITOR('AH11A2', (0.0, 10e-12), (1.62e-9, 84.2e-12), (0.43e-9, 119.1e-12), w, hv1, lv1, relu)
    ah11b2 = CAPACITOR('AH11B2', (0.0, 10e-12), (1.62e-9, 77.8e-12), (0.40e-9, 112.9e-12), w, hv1, lv1, relu)
    ah11c2 = CAPACITOR('AH11C2', (0.0, 100e-12), (1.96e-9, 101.2e-12), (0.56e-9, 104.8e-12), w, hv2_xfrm, lv2, relu)
    ah11d2 = CAPACITOR('AH11D2', (0.0, 100e-12), (1.91e-9, 102.4e-12), (0.31e-9, 101.9e-12), w, hv2_xfrm, lv2, relu)

    es14 = CAPACITOR('ES14', (0.0, 0.5e-12), (0, 0), (0, 0), w, no_lead, no_lead, relu)
    es13 = CAPACITOR('ES13', (0.0, 5.0e-12), (8e-10, 2.05e-10), (0, 0), w, xfrm, no_lead, relu)
    es16 = CAPACITOR('ES16', (0.0, 5.0e-12), (6e-10, 1.85e-10), (0, 0), w, xfrm, no_lead, relu)
    gr10 = CAPACITOR('GR10', (0.0, 10.0e-12), (0, 0), (0, 0), w, no_lead, no_lead, relu)
    gr100 = CAPACITOR('GR100', (0.0, 100.0e-12), (0, 0), (0, 0), w, no_lead, no_lead, relu)
    gr1000a = CAPACITOR('GR1000A', (0.0, 1000.0e-12), (0, 0), (0, 0), w, xfrm, no_lead, relu)
    gr1000b = CAPACITOR('GR1000B', (0.0, 1000.0e-12), (0, 0), (0, 0), w, xfrm, no_lead, relu)
    es13_16 = PARALLEL(es13, es16, hv1, no_lead)

    # For now the starting point is an NMIA value of AH11C1
    cert = ucomplex((1.9e-6 * 100e-12 * 1.5915e3 + 1j * w * 99.999586e-12),(0.6e-6 * 100e-12 * 1.5915e3,
                                                                            0.11e-6 / 2 * w * 100e-12), 50)
    ah11c1.set_best_value(cert)  # nominal value remains as 100 pF
    c1 = ah11c1.best_value - ah11c1.lead_correction() # measured C slightly larger than certificate value
    r4 = scale.balance_dict['r4']
    a1 = scale.cap_ratio(r4, c1, True)
    ah11a1.set_best_value(a1 + ah11a1.lead_correction())  # this is the value with no leads
    r5 = scale.balance_dict['r5']
    b1 = scale.cap_ratio(r5, c1, True)
    ah11b1.set_best_value(b1 + ah11b1.lead_correction())  # this is the value with no leads
    r6 = scale.balance_dict['r6']
    a2 = scale.cap_ratio(r6, c1, True)
    ah11a2.set_best_value(a2 + ah11a2.lead_correction())  # this is the value with no leads
    r7 = scale.balance_dict['r7']
    b2 = scale.cap_ratio(r7, c1, True)
    ah11b2.set_best_value(b2 + ah11b2.lead_correction())  # this is the value with no leads
    r8 = scale.balance_dict['r8']
    g10 = scale.cap_ratio(r8, c1, True)
    gr10.set_best_value(g10 + gr10.lead_correction())  # this is the value with no leads

    # shift to AH11A1 as the reference to put values on all the 100 pF capacitors
    ref2 = ah11a1.best_value -ah11a1.lead_correction()
    r9 = scale.balance_dict['r9']
    c100 = scale.cap_ratio(r9, ref2, False)  # cross check with c1 for build up consistency
    r10 = scale.balance_dict['r10']
    d1 = scale.cap_ratio(r10, ref2, False)
    ah11d1.set_best_value(d1 + ah11d1.lead_correction())  # this is the value with no leads
    r11 = scale.balance_dict['r11']
    c2 = scale.cap_ratio(r11, ref2, False)
    ah11c2.set_best_value(c2 + ah11c2.lead_correction())  # this is the value with no leads
    r12 = scale.balance_dict['r12']
    d2 = scale.cap_ratio(r12, ref2, False)
    ah11d2.set_best_value(d2 + ah11d2.lead_correction())  # this is the value with no leads
    r13 = scale.balance_dict['r13']
    g100 = scale.cap_ratio(r13, ref2, False)
    gr100.set_best_value(g100 + gr100.lead_correction())  # this is the value with no leads

    # shift to AH11C1_no_xfrm as the reference to put values on all the 1000 pF capacitors
    ah11c1_nox = CAPACITOR('AH11C1_nox', (0.0, 100e-12), (2.06e-9, 104.1e-12), (0.57e-9, 87.7e-12), w, hv2, lv2, relu)
    ref3 = ah11c1.best_value - ah11c1_nox.lead_correction()  # same capacitor different leads
    r14 = scale.balance_dict['r14']
    g1000a = scale.cap_ratio(r14, ref3, False)
    gr1000a.set_best_value(g1000a + gr1000a.lead_correction())  # this is the value with no leads
    r15 = scale.balance_dict['r15']
    g1000b = scale.cap_ratio(r15, ref3, False)
    gr1000b.set_best_value(g1000b + gr1000b.lead_correction())  # this is the value with no leads

    # work down to 0.5 pF
    r3 = scale.balance_dict['r3']
    e1316 = scale.cap_ratio(r3, c1, True)
    print('es1316 ', e1316.imag*1e8)
    es13_16.set_best_value(e1316)  # no transformer connection
    r1 = scale.balance_dict['r1']
    r2 = scale.balance_dict['r2']
    c13, c16, c14 = scale.sum_ratio(r1, r2, e1316)
    print('answer', (c13.imag*1e8/5 - 1)*1e6, (c16.imag*1e8/5 -1)*1e6, (c14.imag*1e8/0.5-1)*1e6)
    es13.set_best_value(c13)
    es16.set_best_value(c16)
    es14.set_best_value(c14)


    print('cert ', cert.imag)
    print('ah11c1 ', ah11c1.best_value.imag)
    print('lead correction ah11c1 ', ah11c1.lead_correction())
    print('c1 ', c1.imag*1e8)
    print('a1', a1.imag*1e8)
    print('ah11a1 ', ah11a1.best_value.imag*1e8)
    print('ah11b1 ', ah11b1.best_value.imag*1e8)
    print('ah11a2 ', ah11a2.best_value.imag*1e8)
    print('ah11b2 ', ah11b2.best_value.imag*1e8)
    print('gr10 ', gr10.best_value.imag*1e8)
    print('c100 ', c100.imag*1e8)
    print('ah11d1 ', ah11d1.best_value.imag * 1e8)
    print('ah11c2 ', ah11c2.best_value.imag * 1e8)
    print('ah11d2 ', ah11d2.best_value.imag * 1e8)
    print('gr100 ', gr100.best_value.imag * 1e8)
    print('gr1000a ', gr1000a.best_value.imag * 1e8)
    print('gr1000b ', gr1000b.best_value.imag * 1e8)

    # The above largely does the scale, but a lot of detail and some Y12 and Y34 values need to be sorted
    # Also impedance of common lead for the two 5 pF capacitors.

    # then correct for leads
    # then correct for transformer
    # ratio up and down doing lead and transformer corrections as we go
    # look at lead summation and capacitor summation
    value_at_end_of_leads = ah11c1.best_value - ah11c1.lead_correction()
    print('end leads ', value_at_end_of_leads)
    print(value_at_end_of_leads.imag/w *1e12, ' pF')
    ah11c1_xfrm = CAPACITOR('ah11c1_xfrm',(0.0, 100e-12), (2.06e-9, 104.1e-12), (0.57e-9, 87.7e-12), w, xfrm, no_lead, relu)
    value_with_xfrm = value_at_end_of_leads - ah11c1_xfrm.lead_correction()
    print(value_with_xfrm.imag/w *1e12, ' pF')

    print('es13_16 ', es13_16.y13.imag*1e8)

    # for convenience I will create a csv file here that is essentially appropriate for loading into the BUILDUP class
    # they should be starting with a best_value that has just been calculated
    lead_dict = {'hv1': hv1, 'hv2': hv2, 'lv2': lv2, 'xfrm':xfrm, 'hv1_xfrm': hv1_xfrm, 'hv2_xfrm':xfrm,
                 'no_lead': no_lead}
    cap_dict = {'ah11a1': ah11a1, 'ah11b1': ah11b1, 'ah11c1': ah11c1, 'ah11d1': ah11d2, 'ah11a2':ah11a2,
                'ah11b2': ah11b2, 'ah11c2': ah11c2, 'ah11d2': ah11d2, 'es14': es14, 'es13': es13, 'es16': es16,
                'gr10': gr10, 'gr100': gr100, 'gr1000a': gr1000a, 'gr1000b': gr1000b, 'es13_16': es13_16}

    my_store = COMPONENTSTORE()
    my_data_folder = Path('G:\\My Drive\\KJ\\PycharmProjects\\CapacitanceScale\\datastore')
    my_output_file_name = 'leads_and_caps.csv'
    my_data_out = my_data_folder / my_output_file_name
    print(repr(my_data_out))

    with open(my_data_out, 'w', newline='') as output_file:
        writer = csv.writer(output_file)
        for x in lead_dict:
            y = my_store.lead_to_dict(lead_dict[x])  # dictionary
            writer.writerow([x, dumps(y)])  # json string
        for x in cap_dict:
            y = my_store.capacitor_to_dict(cap_dict[x])
            writer.writerow([x, dumps(y)])

    print('finished saving to csv file')
    # lead_list = []
    # for x in lead_dict:
    #     lead_list.append(x)
    # print(lead_list)
    #
    # cap_list = []
    # for x in cap_dict:
    #     cap_list.append(x)
    # print(cap_list)

    cap_list = ['ah11a1', 'ah11b1', 'ah11c1', 'ah11d1', 'ah11a2', 'ah11b2', 'ah11c2', 'ah11d2', 'es14', 'es13', 'e16',
                'gr10', 'gr100', 'gr1000a', 'gr1000b', 'es13_16']
    lead_list = ['hv1', 'hv2', 'lv2', 'xfrm', 'hv1_xfrm', 'hv2_xfrm', 'no_lead']

    recovered = {}

    with open(my_data_out, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] in cap_list:
                item = loads(row[1])
                item = my_store.dict_to_capacitor(item)
                recovered[row[0]] = item

    print(type(recovered), recovered)  # recovered is a dictionary of capacitor objects
    print(recovered['ah11b1'].best_value.imag*1e8, ' pF')

    # Best value of AH11C1
    print(dumps(my_store.capacitor_to_dict(ah11c1)))  # will have even more quotes in csv form