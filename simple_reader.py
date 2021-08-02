"""
simple_reader.py takes the csv output files from cal_main_ratio.py and cap_scale.py and summarises them in
hr.csv, a 'human readable' version of the capacitance values and the transformer ratio.
"""
from archive import COMPONENTSTORE
from json import loads
import csv

# input_file = r'datastore_12_2020/leads_and_caps.csv'  # location of build up results
# input_perm_file = r'datastore/out_perm.csv'  # location of transformer ratio
input_file = r'datastore_12_2020/out3.csv'  # location of build up results
input_perm_file = r'datastore_12_2020/out_perm2.csv'  # location of transformer ratio
hr_file = r'hr.csv'

store = COMPONENTSTORE()
values = store.gs.read_gtc(input_file)
header1 = ['Buildup file', input_file]
header2 = ['Name','capacitance/pF', 'u/pF', 'conductance/nS', 'u/nS']
simple_output = [header1, header2]
for x in values:
    check = 'False'
    output = []
    name = x[0]
    jdata = loads(x[2])
    try:
        bb = store.dict_to_capacitor(jdata)  # components.CAPACITOR object
        cap = (bb.best_value.imag/bb.w*1e12).x  # in pF
        unc = [bb.best_value.u[0]*1.0e9, bb.best_value.u[1]/bb.w*1e12]  # in nS and pF
        output.append(bb.label)
        output.append(cap)
        output.append(unc[1])
        cond = (bb.best_value.real.x * 1.0e9)  # conductance in nS
        output.append(cond)
        output.append(unc[0])
        check = 'True'
    except:  # components.LEAD object so not processed (lazy approach)
        # bb = store.dict_to_lead(jdata)
        bb = 0

    if check == 'True':
        simple_output.append(output)

simple_output.append([])  # space in the csv file
simple_output.append(['Transformer ratio file', input_perm_file])
values = store.gs.read_gtc(input_perm_file)
simple_output.append(values[0])
simple_output.append(values[1])
simple_output.append(['ratio.real', 'u', 'ratio.imag', 'u'])
dictratio = loads(values[2][0])  # dictionary loaded from the json string
ratio = store.gs.dict_to_ucomplex(dictratio)
simple_output.append([ratio.real.x, ratio.real.u, ratio.imag.x, ratio.imag.u])

for item in simple_output:
    print(item)

with open(hr_file, 'w', newline='') as output_file_name:
    writer = csv.writer(output_file_name)
    writer.writerows(simple_output)
    output_file_name.close()
