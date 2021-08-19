#  python 3.9 environment
import csv
from GTC import ucomplex
from archive import COMPONENTSTORE
from components import LEAD, CAPACITOR
from json import dumps


class CREATOR(object):
    def __init__(self, working_directory, input_files, output_files):
        """

        Component models are managed with the classes in components.py with the measured values held in various csv
        files. While it can be convenient to enter new values by directly editing json string representations of
        ucomplex etc., it is safer to create these files by entering values directly from measurements recorded in lab
        books. The aim is to ensure that there is always clarity about the source of values for leads and various
        parasitic immitances. The risk is that hasty editing of files might later lead to difficulties with
        interpreting historic calculations where old values were simply overwritten with no lasting records kept.

        Values need to be entered into this code, but the ultimate intent is to use a GUI for manual data entry and
        display. All data entered into the GUI would be stored in csv files for processing. In this way the GUI remains
        a convenience without altering the essential flow of data in from csv files followed by calculation with
        results placed in csv files.

        Some information could be in an input file, but in general only the output file is required.
        :param working_directory: assume a common working directory
        :param input_files: not yet used as values are in the code and easy to edit
        :param output_files: name chosen to match the purpose
        """
        self.working_directory = working_directory
        self.output_file = output_files

    def create_permutable(self, permutable_header):
        """

        Latest values are entered by editing the values in the code for this method.
        :param permutable_header: string that identifies the source of the information
        :return: creates a csv file of the model of the permutable capacitor
        """
        # enter the value of each of the 11 capacitors in pF
        pc_dict = {}
        pc_dict['pc1'] = 10.000144
        pc_dict['pc2'] = 10.000304
        pc_dict['pc3'] = 10.000218
        pc_dict['pc4'] = 10.000151
        pc_dict['pc5'] = 10.000200
        pc_dict['pc6'] = 10.000138
        pc_dict['pc7'] = 9.9998906
        pc_dict['pc8'] = 10.000130
        pc_dict['pc9'] = 10.000025
        pc_dict['pc10'] = 10.000043
        pc_dict['pc11'] = 10.000277

        # enter the value of components in Fig. 9 of E005.003
        # p.90 of KJ Diary 2 has PC values
        # I:\MSL\Private\Electricity\Ongoing\Farad\CalcCap\Cap1997\BU29OC97.XLS has assumed lead values
        # these will do for now, but remeasuring them in future is obviously a good idea.
        # values entered in ohm, henry, farad and siemen
        angf = 1e4  # assume measurements made at about 1.6 kHz
        rel_u = 0.05  # nominal 5% error in component measurements
        # lead A
        aR = 6.5128e-2
        aL = 4.269e-7
        za = ucomplex((aR + 1j * angf * aL), (rel_u * aR, rel_u * angf * aL), label='za')

        aG = 5e-11
        aC = 6.4915e-11
        ya = ucomplex((aG + 1j * angf * aC), (rel_u * aG, rel_u * angf * aC), label='ya')

        yR = 2.606e-2
        yL = 2.417e-7
        zinta = ucomplex((yR + 1j * angf * yL), (rel_u * yR, rel_u * angf * yL), label='zinta')

        gppp = 2.09e-10
        cppp = 6.0527e-12
        y3 = ucomplex((gppp + 1j * angf * cppp), (rel_u * gppp, rel_u * angf * cppp), label='y3')

        gp = 6.4e-9
        cp = 3.1818e-10  # this is effectively y4 + Y2
        y4Y2 = ucomplex((gp + 1j * angf * cp), (rel_u * gp, rel_u * angf * cp), label='y4Y2')

        # lead B
        bR = 6.5498e-2
        bL = 4.330e-7
        zb = ucomplex((bR + 1j * angf * bL), (rel_u * bR, rel_u * angf * bL), label='zb')

        bG = 5.0e-11
        bC = 6.438e-11
        yb = ucomplex((bG + 1j * angf * bC), (rel_u * bG, rel_u * angf * bC), label='yb')

        # zintb
        xR = 2.417 - 2
        xL = 2.515e-7
        zintb = ucomplex((xR + 1j * angf * xL), (rel_u * xR, rel_u * angf * xL), label='zintb')

        # y1
        gppp = 2.09e-10
        cppp = 6.0527e-12
        y1 = ucomplex((gppp + 1j * angf * cppp), (rel_u * gppp, rel_u * angf * cppp), label='y1')

        # y2Y1
        gpp = 7.41e-10
        cpp = 4.0168e-11  # this is effectively y2 + Y1
        y2Y1 = ucomplex((gpp + 1j * angf * cpp), (rel_u * gpp, rel_u * angf * cpp), label='y2Y1')

        # assemble ucomplex json strings
        comps_dict = {}
        comps_dict['za'] = store.gs.ucomplex_to_json(za)
        comps_dict['ya'] = store.gs.ucomplex_to_json(ya)
        comps_dict['zinta'] = store.gs.ucomplex_to_json(zinta)
        comps_dict['y3'] = store.gs.ucomplex_to_json(y3)
        comps_dict['y4Y2'] = store.gs.ucomplex_to_json(y4Y2)
        comps_dict['zb'] = store.gs.ucomplex_to_json(zb)
        comps_dict['yb'] = store.gs.ucomplex_to_json(yb)
        comps_dict['zintb'] = store.gs.ucomplex_to_json(zintb)
        comps_dict['y1'] = store.gs.ucomplex_to_json(y1)
        comps_dict['y2Y1'] = store.gs.ucomplex_to_json(y2Y1)

        self.create_output(permutable_header, [comps_dict, pc_dict], True)

    def create_leads(self, header):
        """

        All the measured values are in the lists in this method.
        :param header: single line meta_data
        :return: creates a csv file of the lead models
        """
        lead_variables = ['hv1', 'hv2', 'lv1', 'lv2', 'xfrm', 'no_lead']  # removing renamed combinations of leads.
        matching_labels = ['ah11hv1', 'ah11hv2', 'ah11lv1', 'ah11lv2', '100 to 1', 'no_lead']
        relative_u = [0.05, 0.05, 0.05, 0.05, 0.05, 0.05]  # relative uncertainty, assumed
        ang_freq_list = [1e4, 1e4, 1e4, 1e4, 1e4, 1e4]  # frequency at which the lead is used
        resistance_list = [0.286, 0.16, 0.302, 0.273, 0.037, 0.0]  # ohms
        inductance_list = [0.782e-6, 0.83e-6, 0.616e-6, 1.101e-6, 0.81e-6, 0.0]  # henry
        capacitance_list = [255.2e-12, 260.6e-12, 93.6e-12, 169.8e-12, 52.4e-12, 0.0]  # farad
        conductance_list = [2.8e-10, 3.0e-10, 2.0e-10, 3.6e-10, 3.4e-10, 0.0]  # siemen
        leads = []
        for i in range(len(lead_variables)):  # create LEAD objects based on values in the lists
            leads.append(LEAD(matching_labels[i], (resistance_list[i], inductance_list[i]),
                              (conductance_list[i], capacitance_list[i]), ang_freq_list[i], relative_u[i]))
        output_dict = {}
        for i in range(len(lead_variables)):
            output_dict[lead_variables[i]] = store.lead_to_dict(leads[i])  # a dictionary of lead dictionaries
        self.create_output(header, [output_dict], True)  # new file

    def create_capacitors(self, header):
        """

        All the measured values are in the lists created in this method
        :param header: the string to title the block of capacitors in the output csv
        :return: appends to the file created by create_leads
        """
        print('create_capacitor', self.output_file)
        capacitor_names = ['ah11a1', 'ah11b1', 'ah11c1', 'ah11d1', 'ah11a2', 'ah11b2', 'ah11c2', 'ah11d2', 'es14',
                           'es13', 'es16', 'gr10', 'gr100', 'gr1000a', 'gr1000b', 'es13_16']
        relative_u = [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01]
        labels = ['AH11A1', 'AH11B1', 'AH11C1', 'AH11D1', 'AH11A2', 'AH11B2', 'AH11C2', 'AH11D2', 'ES14',
                  'ES13', 'ES16', 'GR10', 'GR100', 'GR1000A', 'GR1000B', 'ES13ES16']
        nominal_cap = [(0.0, 10e-12), (0.0, 10e-12), (0.0, 100e-12), (0.0, 100e-12), (0.0, 10e-12), (0.0, 10e-12),
                       (0.0, 100e-12), (0.0, 100e-12), (0.0, 0.5e-12), (0.0, 5.0e-12), (0.0, 5.0e-12), (0.0, 10e-12),
                       (0.0, 100e-12), (0.0, 1000e-12), (0.0, 1000e-12), (0.0, 10e-12)]  # (siemen, farad)
        yhv = [(1.62e-09, 8.42e-11), (2.48e-09, 8.36e-11), (2.06e-09, 1.041e-10), (1.91e-09, 1.024e-10),
               (1.62e-09, 8.42e-11), (1.62e-09, 7.78e-11), (1.96e-09, 1.012e-10), (1.91e-09, 1.024e-10), (0.0, 0.0),
               (8e-10, 2.05e-10), (6e-10, 1.85e-10), (0.0, 0.0), (0.7e-09, 4.8372e-10), (0.0, 1.386e-09),
               (0.0, 1.386e-09), (2.08e-09, 4.948e-10)]  # (siemen, farad) note lack of yhv for GR10 (only on HV side)
        ylv = [(7.2e-10, 1.208e-10), (7e-10, 1.175e-10), (5.7e-10, 8.77e-11), (3.1e-10, 1.019e-10),
               (4.3e-10, 1.191e-10), (4e-10, 1.129e-10), (5.6e-10, 1.048e-10), (3.1e-10, 1.019e-10), (0.0, 0.0),
               (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0)]  # (siemen, farad)
        ang_freq = [1e4, 1e4, 1e4, 1e4, 1e4, 1e4, 1e4, 1e4, 1e4, 1e4, 1e4, 1e4, 1e4, 1e4, 1e4, 1e4]
        capacitors = []
        for i in range(len(capacitor_names)):  # create CAPACITOR objects (without best values?)
            capacitors.append(CAPACITOR(labels[i], nominal_cap[i], yhv[i], ylv[i], ang_freq[i], relative_u[i]))
        for i in range(len(capacitors)):  # set best_value to nominal at the start ...
            nominal = ucomplex(nominal_cap[i][0] + 1j * ang_freq[i] * nominal_cap[i][1], (1e-20, 1e-20),
                               label=capacitor_names[i])
            capacitors[i].set_best_value(nominal)
        output_dict = {}
        for i in range(len(capacitor_names)):
            output_dict[capacitor_names[i]] = store.capacitor_to_dict(capacitors[i])  # a dictionary of cap dictionaries
        self.create_output(header, [output_dict], False)  # assumes it is appending to the leads

    def create_output(self, header, input_dict_list, new):
        """

        Generic csv writer
        :param header: string to include key meta-data
        :param input_dict_list: each dictionary value is written as a row of the key and the value of the key
        :param new: boolean set True for to write a new file or overwrite the file, when False it appends data
        :return: the output csv file for the CREATOR object
        """
        if new:
            csv_flag = 'w'  # creates new csv file
        else:
            csv_flag = 'a'  # appends to existing csv file
        output = []
        output.append([header])
        for i in range(len(input_dict_list)):
            for x in input_dict_list[i]:
                output.append([x, dumps(input_dict_list[i][x])])
        csv_out = self.working_directory + '/' + self.output_file + '.csv'
        with open(csv_out, csv_flag, newline='') as csvfile:
            writer = csv.writer(csvfile)
            for x in output:
                writer.writerow(x)


if __name__ == '__main__':
    store = COMPONENTSTORE()  # to access conversion methods

    # # permutable capacitor
    # make = CREATOR(r'G:\My Drive\KJ\PycharmProjects\CapacitanceScale\data_store_test', 'none', 'comp_permute')
    # permutable_header = 'Components of permutable capacitor circuit, assembled 9 August 2021'
    # make.create_permutable(permutable_header)
    # # end of permutable capacitor file

    make = CREATOR(r'G:\My Drive\KJ\PycharmProjects\CapacitanceScale\data_store_test', 'none', 'comp_leads_and_caps')
    make.create_leads('Leads')
    make.create_capacitors('Capacitors')
