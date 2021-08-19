"""

main.py  takes all input data from the calibration of the dials, the 10:1 ratio
and all the individual capacitance ratio measurements so that the results can be
presented together with the input data in a format suitable for checking.

A single buildup dataset is identified in the main.csv file that contains the names of all
the input/output directories/files that are used in the specific calculation.
"""
from cal_balance import DIALCAL  # calibration of the balance injection dials
from cal_main_ratio import PERMUTE  # calibration of the 10:1 voltage ratio
from meas_cap_ratio import CAPSCALE  # calibration of all the capacitors relative to a reference
import csv
from GTC import ureal
from GTC.reporting import budget  # just for checks
from summary_check import SUMMARY

file_info = 'main_2.csv'  # list of directories and files
file_dict = {}  # hold these directories/files in this dictionary
with open(file_info, newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        file_dict[row[0]] = row[1]
print('Dictionary of files', file_dict)
print()
print('Testing cal_balance.py')
cal_dials = DIALCAL(file_dict['Working directory'],
                    [file_dict['Dial input'], file_dict['Leads and caps']], file_dict['Dial output'])
factora, factorb = cal_dials.dialfactors(file_output=True, append=False)

# Note that previously the results from 'Dial output' were manually pasted into 'Ratio input'.
# This means that cal_main_ratio.py is now modified to read the factors from from above ('Dial output')
# rather than 'Ratio input'. This needs to be tidied up
print('Testing cal_main_ratio.py')
ratio_cal = PERMUTE(file_dict['Working directory'],
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
# Should be part of main.csv?
w = 1e4  # rad/s
cap = 99.999586e-12  # pF
ucap = 0.11e-6  # relative expanded uncertainty, k = 2
dfact = 1.9e-6  # dissipation factor S/F/Hz
udfact = 0.6e-6  # S/F/Hz, k=2
g = ureal(dfact * w * cap, udfact / 2 * w * cap, 50, label='ah11c1d')
c = ureal(cap, cap * ucap / 2, 50, label='ah11c1c')
cert = g + 1j * w * c  # admittance of reference at angular frequency w
print('reference value for buildup = ', repr(cert))
# uses this reference value in CAPSCALE
buildup = CAPSCALE(file_dict['Working directory'],
                   [file_dict['Scale input'], file_dict['Leads and caps']], file_dict['Scale output'], cert,
                   afactor=factora, bfactor=factorb, ratio=final_ratio)
all_capacitors = buildup.buildup()
buildup.store_buildup()

summary = SUMMARY(file_info)
summary.create_summary(True)  # False if no updated leads and caps csv is required
# example uncertainty budget
select = buildup.caps['gr1000a'].best_value
# capacitance is imaginary part
capacitance = select.imag / buildup.w
print(capacitance)
print('budget')
print(capacitance.u / capacitance * 1e6)
for label, u in budget(capacitance, trim=0):
    print("{:^20} {:.2e}   {:.3f}".format(label, u, u / capacitance.x * 1e6))
