#  python3.9 environment
from GTC import ucomplex
from GTC.reporting import budget  # just for checks

"""
Develop classes and methods for dealing efficiently with lead corrections in impedance bridges.
"""


class LEAD(object):
    def __init__(self, name, series_z, parallel_y, ang_freq, rel_u):
        """

        Pi transform of a cable
        :param name: label to identify cable
        :param series_z: series impedance as tuple of resistance (ohm) and inductance (H)
        :param parallel_y: admittance of cable as tuple of conductance (S) and capacitance (F)
        :param ang_freq: angular frequency in radians per second
        :param rel_u a default relative uncertainty in the L, R, C values (could be nuanced)
        """
        self.relu = rel_u
        self.w = ang_freq
        self.label = name
        self.z = ucomplex((series_z[0] + 1j * series_z[1] * self.w), (series_z[0] * self.relu, series_z[1] * self.w
                                                                      * self.relu), label=name + ' z')
        self.y = ucomplex((parallel_y[0] + 1j * parallel_y[1] * self.w), (parallel_y[0] * self.relu, parallel_y[1]
                                                                          * self.w * self.relu), label=name + ' y')


class CONNECT(object):
    def __init__(self, lead1, lead2):
        """

        Connects two LEAD objects in series with the assumption that they are two similar coaxial leads differing only
        in length. This allows the transformer lead to simply be added to the hv lead on the low voltage side of
        the 10:1 ratio.
        :param lead1: LEAD object
        :param lead2: LEAD object
        """
        assert lead1.w == lead2.w, 'leads should both be defined at the same frequency'
        self.w = lead1.w
        assert lead1.relu == lead2.relu, 'leads need same relative uncertainty'
        self.relu = lead1.relu
        self.label = lead1.label + lead2.label  # not really used as it is an intermediate calculation step
        self.z = lead1.z + lead2.z
        self.y = lead1.y + lead2.y


class CAPACITOR(object):
    def __init__(self, name, nom_cap, yhv, ylv, ang_freq, rel_u, **kwargs):
        """

        Two terminal-pair capacitor. Components entered as C and G but stored as admittances for the given angular
         frequency. The lead corrections is calculated using the nominal value of the capacitor.
        :param name: label to identify capacitor
        :param nom_cap: the main capacitor as a tuple of conductance and capacitance, nominal value
        :param yhv: additional admittance to screen at the HV terminal as a tuple of G and C
        :param ylv: additional admittance to screen at the LV terminal as a tuple of G and C
        :param ang_freq: angular frequency, w, in radians per second
        :param rel_u a default 1% relative uncertainty in measured C, G values for yhv and ylv (should nuance?).
        :param kwargs: best_value = the best calculated value as a ucomplex in the build up
        """
        self.relu = rel_u  #
        for arg in kwargs.keys():
            if arg == 'best_value':
                self.best_value = kwargs[arg]
        self.w = ang_freq
        self.label = name
        self.y13 = ucomplex((nom_cap[0] + 1j * nom_cap[1] * self.w), (0, 0),
                            label=self.label + ' nom_y13')  # treat y13 as exact for correction purposes
        self.y12 = ucomplex((yhv[0] + 1j * yhv[1] * self.w), (yhv[0] * self.relu, yhv[1] * self.w * self.relu),
                            label=self.label + ' y12')
        self.y34 = ucomplex((ylv[0] + 1j * ylv[1] * self.w), (ylv[0] * self.relu + ylv[1] * self.w * self.relu),
                            label=self.label + ' y34')

    def lead_correction(self, hvlead, lvlead):
        """
        connects the hv and lv leads to capacitor and calculates the modified value of the capacitor
        :param hvlead: a LEAD object connected at the high potential terminal 1-2
        :param lvlead: a LEAD object connected at the low potential terminal 3-4
        :return: ucomplex correction so that true Y = measured Y + correction
        """
        # from A3, Figure 7, equation 40 of E.005.003
        z1 = hvlead.z
        y1 = hvlead.y / 2 + self.y12  # half lead capacitance plus screen capacitance.
        z2 = lvlead.z
        y2 = self.y34 + lvlead.y / 2  # screen capacitance plus half lead capacitance
        a = 1 + z1 * y1 + z2 * y2 + z1 * y1 * z2 * y2
        b = z1 + z2 + z1 * z2 * (y1 + y2)
        y_meas = self.y13 / (a + b * self.y13)
        correction = self.y13 - y_meas  # i.e. y13 = y_meas + correction
        return correction

    def set_best_value(self, value):
        """
        Replaces the instantiated self.best_value with a ucomplex value. This might be a convenience if an updated
        version of a specific instance of CAPACITOR needs to be stored.
        :param value:
        :return:
        """
        self.best_value = value
        return


class PARALLEL(object):
    def __init__(self, cap1, cap2):
        """

        Specifically for putting the two 5 pF capacitors in parallel with the original hv leads in parallel. It is
        assumed that there is no additional common lead, i.e. they plug directly into the LV transformer and common
        detector junction.
        :param cap1:
        :param cap2:
        """
        assert cap1.w == cap2.w, 'Both CAPACITOR objects must be defined at same frequency'
        self.w = cap1.w
        self.label = cap1.label + cap2.label
        assert cap1.relu == cap2.relu, 'capacitors need same relative uncertainty'
        self.relu = cap1.relu
        self.y13 = cap1.y13 + cap2.y13
        self.y12 = cap1.y12 + cap2.y12 + hv1.y + hv2.y  # add paralleled lead admittance to
        self.y34 = cap1.y34 + cap2.y34 + lv1.y + lv2.y  # screen admittance of capacitor

    def lead_correction(self, hvlead, lvlead):
        """
        Connects the hv and lv leads to capacitor and calculates the modified value of the capacitor
        :param hvlead: LEAD object for the common hv lead
        :param lvlead:  LEAD object for the common lv lead
        :return: ucomplex correction so that true Y = measured Y + correction
        """
        # from A3, Figure 7, equation 40 of E.005.003
        z1 = hvlead.z
        y1 = hvlead.y / 2 + self.y12  # half lead capacitance plus screen capacitance.
        z2 = lvlead.z
        y2 = self.y34 + lvlead.y / 2  # screen capacitance plus half lead capacitance
        a = 1 + z1 * y1 + z2 * y2 + z1 * y1 * z2 * y2
        b = z1 + z2 + z1 * z2 * (y1 + y2)
        y_meas = self.y13 / (a + b * self.y13)
        correction = self.y13 - y_meas  # i.e. y13 = y_meas + correction
        return correction

    def set_best_value(self, value):
        """
        Replaces the instantiated self.best_value with a ucomplex value. This might be a convenience if an updated
        version of a specific instance of CAPACITOR needs to be stored.
        :param value:
        :return:
        """
        self.best_value = value
        return


if __name__ == '__main__':
    relu = 0.05
    print('Testing components.py')
    w = 1e4
    hv1 = LEAD('ah11hv1', (286e-3, 0.782e-6), (0.28e-9, 255.2e-12), w, relu)
    lv1 = LEAD('ah11lv1', (302e-3, 0.616e-6), (0.20e-9, 93.6e-12), w, relu)
    hv2 = LEAD('ah11hv2', (160e-3, 0.830e-6), (0.30e-9, 260.6), w, relu)
    lv2 = LEAD('ah11lv2', (273e-3, 1.101e-6), (0.36e-9, 169.8e-12), w, relu)
    no_lead = LEAD('no lead', (0, 0), (0, 0), w, relu)  # use as default when no leads are required
    xfrm = LEAD('100 to 1', (3.7e-2, 8.1e-7), (3.4e-10, 5.24e-11), w, relu)
    hv2_xfrm = CONNECT(xfrm, hv2)
    hv1_xfrm = CONNECT(xfrm, hv1)
    print(hv1.z)
    print(no_lead.y)
    print(hv1_xfrm.z)

    ah11a1 = CAPACITOR('AH11A1', (0.0, 10e-12), (1.62e-9, 84.2e-12), (0.72e-9, 120.8e-12), w, 0.01,
                       best_value=(0.0, 10.00001e-12))
    print(ah11a1.y34.label)
    this_correction = ah11a1.lead_correction(hv1, lv1)
    print('correction', this_correction.imag.x / ah11a1.y13.imag.x)
    print('hv1', hv1.z, hv1.y, hv1.w)
    print('lv1', lv1.z, lv1.y, lv1.w)

    print(ah11a1.lead_correction(hv1, lv1).imag)
    for l, u in budget(ah11a1.lead_correction(hv1, lv1).imag, trim=0):
        print(l, u)

    print('best value ', ah11a1.best_value)
    ah11a1.set_best_value(ah11a1.y13)
    best = ah11a1.best_value + ah11a1.lead_correction(hv1, lv1)
    print('best value ', best)
    print(best.imag / w * 1e12, ' pF')
    correction1 = ah11a1.lead_correction(hv1, lv1)
    ah11a1 = CAPACITOR('AH11A1', (0.0, 10e-12), (1.62e-9, 84.2e-12), (0.72e-9, 120.8e-12), w, 0.01)
    correction2 = ah11a1.lead_correction(hv1_xfrm, lv1)
    print(correction1, correction2)
