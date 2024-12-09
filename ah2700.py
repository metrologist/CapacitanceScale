from openpyxl import Workbook, load_workbook
from GTC import ureal
from predictor import PREDICT as pre
from matplotlib import pyplot as plt

class EXCEL(object):
    def __init__(self, source):
        self.source = source

    def getdata_block(self, datasheet, block_range):
        """
        'datasheet' is the name of the calc worksheet
        'block_range' is a 4 element list [start row, finish row, start column, finish column]
        """
        # simplefilter('ignore')  # hide 'Cannot parse header or footer so it will be ignored'
        try:
            wb2 = load_workbook(self.source, data_only=True)  # reads numbers rather than formulae
        except PermissionError:
            print('Permission error: Could not open file in "get_data_block" method of Excel.py')
            exit(1)
        # simplefilter('default')  # and allow warnings again
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
    plot_date = []

    input = EXCEL(r"AH2700A checks KJ.xlsx")
    # extract conditions
    data = input.getdata_block('Conditions', [3, 27, 4, 7])
    pressure = []
    grtemp = []
    sballtemp = []
    for x in data:
        pressure.append(x[1])
        grtemp.append(x[2])
        sballtemp.append(x[3])
    print(pressure)
    print(grtemp)
    print(sballtemp)

    n_sample = 10  # could be extracted from spreadsheet
    sheets = input.get_sheets()
    print('sheets', sheets)
    count = 0  # just use counter to index relevant conditions ..... this is risky!
    for s in sheets:
        if s != 'Checks' and s != 'Summary' and s != 'KJ notes' and s != 'Conditions':
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
                # else:
                #     print('Help! Not a recognised name.')
            # for x in all_caps:
            #     print(all_caps[x])

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
            # print(cora, corb, corc, cord)
            # might use the average correction for all capacitors in the first instance
            correction = (cora + corb + corc + cord) / 4  # note the lack of correlation gives a lower uncertainty in the mean
            # print('correction=', correction, 'ppm')

            # apply this correction to all measurements?
            for x in all_caps:
                if x != 'zero':
                    # print('x=', x)
                    all_caps[x]['cor_val'] = all_caps[x]['err'] + correction  # pressure & temp could be here
                    if 'tco' in all_caps[x] and 'pco' in all_caps[x]:
                        # print(all_caps[x]['name'], all_caps[x]['tco'],grtemp[count])
                        tcor = (24 - grtemp[count]) * all_caps[x]['tco']
                        pcor = (1000 - pressure[count]) * all_caps[x]['pco']
                        all_caps[x]['cor_val'] = all_caps[x]['cor_val'] + tcor + pcor
                    # print(all_caps[x])
            # print(a_est, b_est, c_est, d_est)

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
            es13 .append(all_caps['es13']['cor_val'])
            ub1000.append(all_caps['ub1000']['cor_val'])
            plot_date.append(all_caps['ah11a1']['PlotDate'])  # this will need to be matplotlib compatible
            count += 1
    # print(ah11a1)
    # print(ub1000)

    # Plotting, so first create plottable arrays
    GR10 = []
    uGR10 = []
    for x in gr10:
        GR10.append(x.x)
        uGR10.append(x.u)
    GR100 = []
    uGR100 = []
    for x in gr100:
        GR100.append(x.x)
        uGR100.append(x.u)
    GR1000B = []
    uGR1000B = []
    for x in gr1000b:
        GR1000B.append(x.x)
        uGR1000B.append(x.u)
    GR1000A = []
    uGR1000A = []
    for x in gr1000a:
        GR1000A.append(x.x)
        uGR1000A.append(x.u)

    AH11A2 = []
    uAH11A2 = []
    for x in ah11a2:
        AH11A2.append(x.x)
        uAH11A2.append(x.u)
    AH11B2 = []
    uAH11B2 = []
    for x in ah11b2:
        AH11B2.append(x.x)
        uAH11B2.append(x.u)
    AH11C2 = []
    uAH11C2 = []
    for x in ah11c2:
        AH11C2.append(x.x)
        uAH11C2.append(x.u)
    AH11D2 = []
    uAH11D2 = []
    for x in ah11d2:
        AH11D2.append(x.x)
        uAH11D2.append(x.u)

    AH11A1 = []
    uAH11A1 = []
    for x in ah11a1:
        AH11A1.append(x.x)
        uAH11A1.append(x.u)
    AH11B1 = []
    uAH11B1 = []
    for x in ah11b1:
        AH11B1.append(x.x)
        uAH11B1.append(x.u)
    AH11C1 = []
    uAH11C1 = []
    for x in ah11c1:
        AH11C1.append(x.x)
        uAH11C1.append(x.u)
    AH11D1 = []
    uAH11D1 = []
    for x in ah11d1:
        AH11D1.append(x.x)
        uAH11D1.append(x.u)

    print('GR10 =', GR10)
    print('GR100 =', GR100)
    print('GR1000A =', GR1000A)
    print('GR1000B =', GR1000B)

    barsize = 4  # points for errorbar cap
    dotsize = 4

    fig, axs = plt.subplots(3, 1, layout='constrained', sharex=True)
    axs[0].errorbar(plot_date, GR10, yerr=uGR10, capsize=barsize, label='GR10', marker='o', markersize=dotsize)
    axs[0].errorbar(plot_date, GR100, yerr=uGR100, capsize=barsize, label = 'GR100', marker='o', markersize=dotsize)
    axs[0].errorbar(plot_date, GR1000A, yerr=uGR1000A, capsize=barsize, label = 'GR1000A', marker='o', markersize=dotsize)
    axs[0].errorbar(plot_date, GR1000B, yerr=uGR1000A, capsize=barsize, label = 'GR1000B', marker='o', markersize=dotsize)
    axs[1].errorbar(plot_date, AH11A2, yerr=uAH11A2, capsize=barsize, label = 'AH11A2', marker='o', markersize=dotsize)
    axs[1].errorbar(plot_date, AH11B2, yerr=uAH11B2, capsize=barsize, label = 'AH11B2', marker='o', markersize=dotsize)
    axs[1].errorbar(plot_date, AH11C2, yerr=uAH11C2, capsize=barsize, label = 'AH11C2', marker='o', markersize=dotsize)
    axs[1].errorbar(plot_date, AH11D2, yerr=uAH11D2, capsize=barsize, label = 'AH11D2', marker='o', markersize=dotsize)
    axs[2].errorbar(plot_date, AH11A1, yerr=uAH11A1, capsize=barsize, label = 'AH11A1', marker='o', markersize=dotsize)
    axs[2].errorbar(plot_date, AH11B1, yerr=uAH11B1, capsize=barsize, label = 'AH11B1', marker='o', markersize=dotsize)
    axs[2].errorbar(plot_date, AH11C1, yerr=uAH11C1, capsize=barsize, label = 'AH11C1', marker='o', markersize=dotsize)
    axs[2].errorbar(plot_date, AH11D1, yerr=uAH11D1, capsize=barsize, label = 'AH11D1', marker='o', markersize=dotsize)
    axs[0].legend()
    axs[1].legend()
    axs[2].legend()
    plt.show()

    # for x in plot_date:
    #     print(x)

