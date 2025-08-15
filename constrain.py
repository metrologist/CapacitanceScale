# constrain.py predicts future values of AH11A#1 for use in the scale build up
# for now the average of the predicted ppm valuew of all four capacitors seems reasonable
from primcal import PRIMCAL
from matplotlib import pyplot as plt
from GTC import ureal
from dict_test import FUNCDICTL

class CONSTRAINT():
    def __init__(self, capa, capb, capc, capd):
        """

        A set of externally calibrated (or independently realised) AH11s is a single instance of CONSTRAINT.
        :param capa: PRIMCAL 10pF a
        :param capb: PRIMCAL 10pF b
        :param capc: PRIMCAL 100 pF c
        :param capd: PRIMCAL 100 pF d
        """
        self.AH11 = [capa, capb, capc, capd]
        self.colours = ['b', 'g', 'r', 'c']  # a convenience for plotting

    def predict(self, date, min_u):
        """

        Predicts the mean of the relative values of the four capacitors on the given date.
        :param date: string formatted as 'Dec 25 1025'
        :param min_u: the base uncertainty in ppm  ... averaging does not reduce the calibration uncertainty
        :return: prediction: ureal of the mean value of the relative errors in ppm
        """

        base_uncertainty = ureal(0, min_u)
        dec_date = self.AH11[0].decimal_date(date)  # clumsily use one of the PRIMCAL instances to access the method
        predicted_vals = []
        sum = 0
        count = 0
        for x in self.AH11:
            gtcft = x.gtcfit  # need to automatically get the number of coefficients
            val = x.equation['fn'](x.gtcfit, dec_date)
            val_ppm = (val / x.nompF - 1) * 1e6
            predicted_vals.append(val_ppm)
            sum = sum + val_ppm
            count += 1
        mean_val  = sum / count
        prediction = mean_val + base_uncertainty  # fit uncertainty always adds to the base uncertainty
        return prediction

    def plot_ppm(self):
        """
        convert all capacitor and fit values to ppm
        :return:
        """
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        colour = 0
        for item in self.AH11:  # each capacitance value and uncertainty is put in ppm
            hue = self.colours[colour]
            nompF = item.nompF
            yy2 = []
            for x in item.pltfn:
                yy2.append((x / nompF - 1) * 1e6)
            yy3 = []
            for x in item.pltfn_plus_u:
                yy3.append((x / nompF - 1) * 1e6)
            yy4 = []
            for x in item.pltfn_minus_u:
                yy4.append((x / nompF - 1) * 1e6)
            plt_x = item.plt_x
            time_axis = item.time_axis
            cap = []
            for x in item.cap:
                cap.append((x / nompF - 1) * 1e6)
            yerr = []
            for x in item.cap_u:
                yerr.append(x / nompF * 1e6)

            ax.plot(plt_x, yy2, label=item.label, color=hue)
            ax.plot(plt_x, yy3, linestyle='dashed', color=hue)
            ax.plot(plt_x, yy4, linestyle='dashed', color=hue)
            ax.errorbar(time_axis, cap, yerr= yerr, linestyle="None", fmt='o', capsize=10, color=hue)
            colour += 1

        plt.title('Primary Calibrations of AH11 #1')
        # plt.title(self.label)
        plt.legend()
        plt.show()


if __name__ == '__main__':
    # Input data
    # Start with AH11A1 with data from Electricity\Ongoing\Farad\LabShift\AH2700A checks KJ_GH.xlsx
    # Note the dummy Jul 20 values to give one degree of freedom
    fn_set = FUNCDICTL()
    std_temperature = 29

    cap1 = [('Mar 19 2009', (9.999950922, 0.000000400, 50, 31.4)),
            ('Jul 20 2019', (9.9999500, 0.000000550, 50, 27.0)),
            ('Jul 21 2019', (9.9999501, 0.000000550, 50, 27.0))
            ]

    coefficient1 = 0.003086584

    # equation1 = 'a1 + a2 * x'
    equation1 = fn_set.f_dict['func1']  # FUNCDICT version

    cap2 = [('Mar 19 2009', (9.999953022, 0.000000400, 50, 31.4)),
            ('Jul 20 2019', (9.9999526, 0.000000550, 50, 27.0)),
            ('Jul 21 2019', (9.9999527, 0.000000550, 50, 27.0))
            ]

    coefficient2 = 0.004026581
    # equation2 = 'a1 + a2 * x'
    equation2 = fn_set.f_dict['func1']  # FUNCDICT version

    cap3 = [('Mar 19 2009', (99.999557221, 0.000004000, 50, 31.4)),
            ('Jul 20 2019', (99.999580, 0.000005500, 50, 27.0)),
            ('Jul 21 2019', (99.999581, 0.000005500, 50, 27.0))
            ]

    coefficient3 = -0.001883384
    # equation3 = 'a1 + a2 * x'
    equation3 = fn_set.f_dict['func1']  # FUNCDICT version

    cap4 = [('Mar 19 2009', (99.999548221, 0.000004000, 50, 31.4)),
            ('Jul 20 2019', (99.999567, 0.000005500, 50, 27.0)),
            ('Jul 21 2019', (99.999568, 0.000005500, 50, 27.0))
            ]

    coefficient4 = -0.003210803
    # equation4 = 'a1 + a2 * x'
    equation4 = fn_set.f_dict['func1']  # FUNCDICT version

    # Create instances of PRIMCAL
    ah11a1 = PRIMCAL(cap1, coefficient1, std_temperature, equation1, '#1 AH11A 10 pF', 10)
    ah11b1 = PRIMCAL(cap2, coefficient2, std_temperature, equation2, '#1 AH11B 10 pF', 10)
    ah11c1 = PRIMCAL(cap3, coefficient3, std_temperature, equation3, '#1 AH11C 100 pF', 100)
    ah11d1 = PRIMCAL(cap4, coefficient4, std_temperature, equation4, '#1 AH11D 100 pF', 100)

    # further process in CONSTRAINT
    constraint = CONSTRAINT(ah11a1, ah11b1, ah11c1, ah11d1)
    predicted_value = constraint.predict('Aug 5 2025', 0.11)
    print('predicted value =', predicted_value, 'ppm')
    predicted_value = constraint.predict('Mar 19 2009', 0.11)
    print('predicted value =', predicted_value, 'ppm')
    constraint.plot_ppm()  # plots all four capacitors on a ppm scale
