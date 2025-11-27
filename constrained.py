from constrain import CONSTRAINT
from primcal import PRIMCAL
from dict_test import FUNCDICTL

class REFERENCE():
    def __init__(self):  # built in external calibrations
        fn_set = FUNCDICTL()
        std_temperature = 29

        cap1 = [('Mar 19 2009', (9.999950922, 0.000000400, 50, 31.4)),
                ('Jul 20 2019', (9.9999500, 0.000000550, 50, 27.0)),
                ('Jul 31 2025', (9.9999513, 0.00000070/4, 50, 27.75))
                ]

        coefficient1 = 0.003086584

        # equation1 = 'a1 + a2 * x'
        equation1 = fn_set.f_dict['func1']  # FUNCDICT version

        cap2 = [('Mar 19 2009', (9.999953022, 0.000000400, 50, 31.4)),
                ('Jul 20 2019', (9.9999526, 0.000000550, 50, 27.0)),
                ('Jul 31 2025', (9.9999540, 0.00000070/4, 50, 27.75))
                ]

        coefficient2 = 0.004026581
        # equation2 = 'a1 + a2 * x'
        equation2 = fn_set.f_dict['func1']  # FUNCDICT version

        cap3 = [('Mar 19 2009', (99.999557221, 0.000004000, 50, 31.4)),
                ('Jul 20 2019', (99.999580, 0.000005500, 50, 27.0)),
                ('Jul 31 2025', (99.999564, 0.0000070/4, 50, 27.75))
                ]

        coefficient3 = -0.001883384
        # equation3 = 'a1 + a2 * x'
        equation3 = fn_set.f_dict['func1']  # FUNCDICT version

        cap4 = [('Mar 19 2009', (99.999548221, 0.000004000, 50, 31.4)),
                ('Jul 20 2019', (99.999567, 0.000005500, 50, 27.0)),
                ('Jul 31 2025', (99.999584, 0.0000070/4, 50, 27.75))
                ]

        coefficient4 = -0.003210803
        # equation4 = 'a1 + a2 * x'
        equation4 = fn_set.f_dict['func1']  # FUNCDICT version

        # Create instances of PRIMCAL
        self.ah11a1 = PRIMCAL(cap1, coefficient1, std_temperature, equation1, '#1 AH11A 10 pF', 10, weight=True)
        self.ah11b1 = PRIMCAL(cap2, coefficient2, std_temperature, equation2, '#1 AH11B 10 pF', 10, weight=True)
        self.ah11c1 = PRIMCAL(cap3, coefficient3, std_temperature, equation3, '#1 AH11C 100 pF', 100, weight=True)
        self.ah11d1 = PRIMCAL(cap4, coefficient4, std_temperature, equation4, '#1 AH11D 100 pF', 100, weight=True)
        self.con = CONSTRAINT(self.ah11a1, self.ah11b1, self.ah11c1, self.ah11d1)
