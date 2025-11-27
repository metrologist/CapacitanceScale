# all_buildup.py will reprocess all selected data sets to produce a consistent history
# this is built on the previous main.py, essentially running that repeatedly
# likely that automated file naming (i.e. incorporating date) will help
# likely that the BATCH class will be put in a separate script

from cal_balance import DIALCAL  # calibration of the balance injection dials
from cal_main_ratio import PERMUTE  # calibration of the 10:1 voltage ratio
from meas_cap_ratio import CAPSCALE  # calibration of all the capacitors relative to a reference
import csv
from GTC import ureal
from GTC.reporting import budget  # just for checks
from summary_check import SUMMARY
import os
from analysis import ANALYSE


class BATCH():
    def __init__(self, main_list, folder):
        """

        :param main_list: a list of all the main_yyyy-dd_x.csv lists of input data
        :param folder: the folder that holds this set of files
        """
        self.main_list = main_list
        self.folder = folder
        self.cwd = os.getcwd()  # get the current working directory

    def execute(self):
        """

        :return:
        """

        summary_file_list = []  # for use by analysis
        cwd = self.cwd  # get the current working directory
        for file_info in self.main_list:
            print('this file_info = ', file_info)
            # file_info = 'main_2025-07-08.csv'  # list of directories and files, also used to name the summary file
            file_dict = {}  # hold these directories/files in this dictionary
            cwd_file_info = os.path.join(cwd, self.folder, file_info)
            with open(cwd_file_info, newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    file_dict[row[0]] = row[1]

            cal_dials = DIALCAL(os.path.join(cwd, file_dict['Working directory']),
                                [file_dict['Dial input'], file_dict['Leads and caps']], file_dict['Dial output'])
            factora, factorb = cal_dials.dialfactors(file_output=True, append=False)

            # Note that previously the results from 'Dial output' were manually pasted into 'Ratio input'.
            # This means that cal_main_ratio.py is now modified to read the factors from from above ('Dial output')
            # rather than 'Ratio input'. This needs to be tidied up
            print('Testing cal_main_ratio.py')
            ratio_cal = PERMUTE(os.path.join(cwd, file_dict['Working directory']),
                                [file_dict['Ratio input'], file_dict['Leads and caps'], file_dict['Dial output'],
                                 file_dict['Permutable']], file_dict['Ratio output'], afactor=factora, bfactor=factorb)
            print(ratio_cal.balance_dict)
            raw_ratio = ratio_cal.calc_raw_ratio()
            print(repr(raw_ratio))
            print((raw_ratio / 10 - 1) * 1e6)
            main_ratio = ratio_cal.correct_ratio(raw_ratio)
            print(main_ratio)
            final_ratio = ratio_cal.correct_ratio(main_ratio)
            print('final ratio ', repr(final_ratio))
            ratio_cal.file_ratio(final_ratio)
            print()
            print('Testing the scale buildup')
            # For now the starting point is an NMIA value of AH11C1
            # Read in the reference value of AH11C
            ref_file = os.path.join(cwd, file_dict['Working directory'], file_dict['Reference'])
            ref_dict = {}
            with open(ref_file, newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    ref_dict[row[0]] = row[1]
            w = float(ref_dict['w'])  # rad/s
            cap = float(ref_dict['cap'])  # pF
            ucap = float(ref_dict['ucap'])  # relative expanded uncertainty, k = 2
            dfact = float(ref_dict['dfact'])  # dissipation factor S/F/Hz
            udfact = float(ref_dict['udfact'])  # S/F/Hz
            g = ureal(dfact * w * cap, udfact / 2 * w * cap, 50, label='ah11c1d')
            c = ureal(cap, cap * ucap / 2, 50, label='ah11c1c')
            cert = g + 1j * w * c  # admittance of reference at angular frequency w
            print('reference value for buildup = ', repr(cert))
            # uses this reference value in CAPSCALE
            list_of_monitored = ['AH1', 'AH2', 'GRin', 'GRout', 'AB1', 'Sball', 'Perm', 'Barom' ] # temperature/pressure
            buildup = CAPSCALE(os.path.join(cwd, file_dict['Working directory']),
                               [file_dict['Scale input'], file_dict['Leads and caps']], file_dict['Scale output'], cert,
                               afactor=factora, bfactor=factorb, ratio=final_ratio, expected=list_of_monitored)
            all_capacitors = buildup.buildup()
            buildup.store_buildup()

            summary = SUMMARY(file_info, self.folder)
            # create the file and return its full path
            summary_path = summary.create_summary(True)  # False if no updated leads and caps csv is required
            summary_file_list.append(summary_path)
            # example uncertainty budget
            select = buildup.caps['gr1000a'].best_value
            # capacitance is imaginary part
            capacitance = select.imag / buildup.w
            print(capacitance)
            print('budget')
            print(capacitance.u / capacitance * 1e6)
            for label, u, id_thing in budget(capacitance, trim=0):
                print("{:^20} {:.2e}   {:.3f}".format(label, u, u / capacitance.x * 1e6))

        return summary_file_list


if __name__ == '__main__':
    files = [r'main_2021-08-23_a.csv',
        r'main_2021-08-27_a.csv',
        r'main_2021-09-06_a.csv',
        r'main_2021-09-09.csv',
        r'main_2021-09-10.csv',
        r'main_2021-09-22.csv',
        r'main_2021-10-11_b.csv',
        r'main_2022-04-07.csv',
        r'main_2025-07-03.csv',
        r'main_2025-07-04.csv',
        r'main_2025-07-07.csv',
        r'new_main_2025-07-08.csv',
        r'main_2025-10-23.csv',
        r'main_2025-10-28.csv',
        r'main_2025-11-06.csv',
        r'main_2025-11-21.csv']  # new is the trial with more recent dial and ratio calibration
    # files = [r'main_2021-08-27_a.csv', r'main_2025-07-08.csv'] # select subset
    batch = BATCH(files, 'temp_run')
    summary_files = batch.execute()  # both executes the buildups and gives the list of summary files
    anal = ANALYSE(summary_files)
    anal.all_sumry()  # loads the data
    anal.corrected_dict()  # applies constraint of the mean of AH11 set #1
    anal.corrected_to_std_con()
    anal.plot(['AH11A1', 'AH11B1', 'AH11C1', 'AH11D1', 'AH11A2', 'AH11B2', 'AH11C2', 'AH11D2'], 'AH11 set')
    anal.plot(['ES14', 'ES13', 'ES16', 'GR10', 'GR100', 'GR1000A', 'GR1000B', 'ES13ES16'], 'GR and S ball set')
    out_block = anal.out_block()  # prepares csv-friendly lists
    anal.file_block('test_analysis.csv', out_block)  # writes to csv file
    anal.store_dicts()
