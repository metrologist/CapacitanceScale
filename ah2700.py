from openpyxl import Workbook, load_workbook
from GTC import ureal
from predictor import PREDICT as pre
from matplotlib import pyplot as plt
# first tidying up attempt
class EXCEL(object):
    def __init__(self, source):
        self.source = source

    def getdata_block(self, datasheet, block_range):
        """
        'datasheet' is the name of the calc worksheet
        'block_range' is a 4 element list [start row, finish row, start column, finish column]
        """
        try:
            wb2 = load_workbook(self.source, data_only=True)  # reads numbers rather than formulae
        except PermissionError:
            print('Permission error: Could not open file in "get_data_block" method of Excel.py')
            exit(1)
        sheet = wb2[datasheet]
        selected_rows = []
        for i in range(block_range[0], block_range[1] + 1):
            this_row = []
            for j in range(block_range[2], block_range[3] + 1):
                this_row.append(sheet.cell(row=i, column=j).value)
            selected_rows.append(this_row)
        return selected_rows

    def get_sheets(self):
        try:
            wb2 = load_workbook(self.source, data_only=True)  # reads numbers rather than formulae
        except PermissionError:
            print('Permission error: Could not open file in "get_data_block" method of Excel.py')
            exit(1)
        names = wb2.sheetnames
        return names


if __name__ == '__main__':

    # List of all capacitors
    # Use the capacitor names for lists as these are reused as labels in the dictionary
    ah11a1 = []
    ah11b1 = []
    ah11c1 = []
    ah11d1 = []
    ah11a2 = []
    ah11b2 = []
    ah11c2 = []
    ah11d2 = []
    gr10 = []
    gr100 = []
    gr1000a = []
    gr1000b = []
    ub1000 = []
    es13 = []
    es16 = []
    es14 = []
    plot_date = []

    input = EXCEL(r"AH2700A checks KJ.xlsx")
    all_sheets = input.get_sheets()
    excluded_meta_sheets = ['Checks', 'Summary', 'KJ notes', 'Conditions']
    nmbr_temp_points = len(all_sheets) - len(excluded_meta_sheets) # need conditions for each data set
    # extract conditions
    data = input.getdata_block('Conditions', [3, 3 + nmbr_temp_points - 1, 4, 9])
    pressure = []
    grtemp = []
    sballtemp = []
    pctemp = []
    ubtemp = []
    for x in data:
        pressure.append(x[1])
        grtemp.append(x[2])
        sballtemp.append(x[3])
        pctemp.append(x[4])
        ubtemp.append(x[5])
    print('pressure =',pressure)
    print('grtemp =', grtemp)
    print('sballtemp =', sballtemp)
    print('pctemp =', pctemp)
    print('ubtemp =', ubtemp)

    n_sample = 10  # could be extracted from spreadsheet
    sheets = input.get_sheets()
    print('sheets', sheets)
    count = 0  # just use counter to index relevant conditions ..... this is risky!
    for s in sheets:
        if s not in excluded_meta_sheets:
        # if s != 'Checks' and s != 'Summary' and s != 'KJ notes' and s != 'Conditions':
            print(s)
            # note that sensitivity coefficients are entered here if available
            all_caps = {'zero': {'name': 'zero'},
                        'ah11a1': {'name': 'ah11a1', 'nom_val': 10},
                        'ah11b1': {'name': 'ah11b1', 'nom_val': 10},
                        'ah11c1': {'name': 'ah11c1', 'nom_val': 100},
                        'ah11d1': {'name': 'ah11d1', 'nom_val': 100},
                        'ah11a2': {'name': 'ah11a2', 'nom_val': 10},
                        'ah11b2': {'name': 'ah11b2', 'nom_val': 10},
                        'ah11c2': {'name': 'ah11c2', 'nom_val': 100},
                        'ah11d2': {'name': 'ah11d2', 'nom_val': 100},
                        'gr10': {'name': 'gr10', 'nom_val': 10, 'tco': 4.96, 'pco':4.8e-4},
                        'gr100': {'name': 'gr100', 'nom_val': 100, 'tco': 2.30, 'pco':-1.9e-4},
                        'gr1000a': {'name': 'gr1000a', 'nom_val': 1000, 'tco': 1.37, 'pco':-3.65e-4},
                        'gr1000b': {'name': 'gr1000b', 'nom_val': 1000, 'tco': 1.01, 'pco':-5.75e-4},
                        'es13': {'name': 'es13', 'nom_val': 5},
                        'es16': {'name': 'es16', 'nom_val': 5},
                        'es14': {'name': 'es14', 'nom_val': 0.5},
                        'ub1000': {'name': 'ub1000', 'nom_val': 1000}}

            print('current sheet', s)
            data = input.getdata_block(s, [3, 19, 1, 9])
            for x in data:
                myname = x[1]
                mydate = x[0].strftime('%d-%b-%Y')  # convert to simple text suitable for the PREDICT class
                if myname in all_caps and myname != 'zero':  # decide later whether to use zero in the calculation
                    all_caps[myname]['Date'] = mydate
                    all_caps[myname]['PlotDate'] = x[0]
                    er = ((x[2] / all_caps[myname]['nom_val'] - 1) * 1e6)
                    uer = (x[3] / all_caps[myname]['nom_val']  * 1e6)
                    rel_err = ureal(er, uer, n_sample - 1, label = myname)
                    all_caps[myname]['err'] = rel_err

            # consider correction required for the AH2700A to give the predicted reading
            ref = pre()  # the set chosen as the reference
            a_est = ref.a.predicted(all_caps['ah11a1']['Date'])
            b_est = ref.b.predicted(all_caps['ah11b1']['Date'])
            c_est = ref.c.predicted(all_caps['ah11c1']['Date'])
            d_est = ref.d.predicted(all_caps['ah11d1']['Date'])

            cora = a_est - all_caps['ah11a1']['err']
            corb = b_est - all_caps['ah11b1']['err']
            corc = c_est - all_caps['ah11c1']['err']
            cord = d_est - all_caps['ah11d1']['err']
            # might use the average correction for all capacitors in the first instance
            correction = (cora + corb + corc + cord) / 4  # note the lack of correlation gives a lower uncertainty in the mean

            # apply this correction to all measurements?
            for x in all_caps:
                if x != 'zero':
                    all_caps[x]['cor_val'] = all_caps[x]['err'] + correction  # pressure & temp could be here
                    if 'tco' in all_caps[x] and 'pco' in all_caps[x]:
                        try:
                            tcor = (24 - grtemp[count]) * all_caps[x]['tco']
                            pcor = (1000 - pressure[count]) * all_caps[x]['pco']
                            all_caps[x]['cor_val'] = all_caps[x]['cor_val'] + tcor + pcor
                        except IndexError:
                            print('!!!!! missing information !!!!')
                            print('Check that every data set has matching temperature and pressure in "Conditions" worksheet.')
                            exit(1)

            ah11a1.append(all_caps['ah11a1']['cor_val'])
            ah11b1.append(all_caps['ah11b1']['cor_val'])
            ah11c1.append(all_caps['ah11c1']['cor_val'])
            ah11d1.append(all_caps['ah11d1']['cor_val'])
            ah11a2.append(all_caps['ah11a2']['cor_val'])
            ah11b2.append(all_caps['ah11b2']['cor_val'])
            ah11c2.append(all_caps['ah11c2']['cor_val'])
            ah11d2.append(all_caps['ah11d1']['cor_val'])
            gr10.append(all_caps['gr10']['cor_val'])
            gr100.append(all_caps['gr100']['cor_val'])
            gr1000a.append(all_caps['gr1000a']['cor_val'])
            gr1000b.append(all_caps['gr1000b']['cor_val'])
            es13.append(all_caps['es13']['cor_val'])
            es16.append(all_caps['es16']['cor_val'])
            es14.append(all_caps['es14']['cor_val'])
            ub1000.append(all_caps['ub1000']['cor_val'])
            plot_date.append(all_caps['ah11a1']['PlotDate'])  # this will need to be matplotlib compatible
            count += 1

    # put all the corrected values in a new dictionary

    all_plots = {   'ah11a1': {'name': 'ah11a1', 'nom_val': 10, 'val': ah11a1},
                    'ah11b1': {'name': 'ah11b1', 'nom_val': 10, 'val': ah11b1},
                    'ah11c1': {'name': 'ah11c1', 'nom_val': 100, 'val': ah11c1},
                    'ah11d1': {'name': 'ah11d1', 'nom_val': 100, 'val': ah11d1},
                    'ah11a2': {'name': 'ah11a2', 'nom_val': 10, 'val': ah11a2},
                    'ah11b2': {'name': 'ah11b2', 'nom_val': 10, 'val': ah11b2},
                    'ah11c2': {'name': 'ah11c2', 'nom_val': 100, 'val': ah11c2},
                    'ah11d2': {'name': 'ah11d2', 'nom_val': 100, 'val': ah11d2},
                    'gr10': {'name': 'gr10', 'nom_val': 10, 'val': gr10},
                    'gr100': {'name': 'gr100', 'nom_val': 100, 'val': gr100},
                    'gr1000a': {'name': 'gr1000a', 'nom_val': 1000, 'val': gr1000a},
                    'gr1000b': {'name': 'gr1000b', 'nom_val': 1000, 'val': gr1000b},
                    'es13': {'name': 'es13', 'nom_val': 5, 'val': es13},
                    'es16': {'name': 'es16', 'nom_val': 5, 'val': es16},
                    'es14': {'name': 'es14', 'nom_val': 0.5, 'val': es14},
                    'ub1000': {'name': 'ub1000', 'nom_val': 1000, 'val': ub1000}}
    # split the corrected values into points and uncertainties
    for y in all_plots:
        all_plots[y]['pval'] = [z.x for z in all_plots[y]['val']]
        all_plots[y]['uval'] = [z.u for z in all_plots[y]['val']]

    # create list of plots for each axis
    list0 = ['ah11a1', 'ah11b1', 'ah11c1', 'ah11d1']
    list1 = ['ah11a2', 'ah11b2', 'ah11c2', 'ah11d2']
    list2 = ['gr10', 'gr100', 'gr1000a', 'gr1000b']
    list3 = ['ub1000', 'es13', 'es16', 'es14']

    barsize = 4  # points for errorbar cap
    dotsize = 4

    fig, axs = plt.subplots(2, 2, layout='constrained', sharex=True)
    for i in range(len(list0)):
        axs[0, 0].errorbar(plot_date, all_plots[list0[i]]['pval'], yerr=all_plots[list0[i]]['uval'], capsize=barsize, label=list0[i], marker='o', markersize=dotsize)
    for i in range(len(list1)):
        axs[0, 1].errorbar(plot_date, all_plots[list1[i]]['pval'], yerr=all_plots[list1[i]]['uval'], capsize=barsize, label=list1[i], marker='o', markersize=dotsize)
    for i in range(len(list2)):
        axs[1, 0].errorbar(plot_date, all_plots[list2[i]]['pval'], yerr=all_plots[list2[i]]['uval'], capsize=barsize, label=list2[i], marker='o', markersize=dotsize)
    for i in range(len(list3)):
        axs[1, 1].errorbar(plot_date, all_plots[list3[i]]['pval'], yerr=all_plots[list3[i]]['uval'], capsize=barsize, label=list3[i], marker='o', markersize=dotsize)
    axs[0, 0].legend()
    axs[0, 1].legend()
    axs[1, 0].legend()
    axs[1, 1].legend()
    plt.show()

