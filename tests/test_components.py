"""
test_components.py
"""

def test_lead_correction():
    # from A3, Figure 7, equation 40 of E.005.003
    from components import LEAD, CAPACITOR
    lead1 = LEAD('lead1', (0.286, 0.782e-6), (255.2e-12, 2.8e-10), 1e4, 0.05)  # hv1
    lead2 = LEAD('lead1', (0.302, 0.616e-6), (93.6e-12, 2.0e-10), 1e4, 0.05)  # lv1
    cap = CAPACITOR('cap', (0, 100e-12), (2.06e-9, 1.041e-10), (5.7e-10, 8.77e-11), 1e4, 0.01)  # AH11C1
    correction = cap.lead_correction(lead1, lead2)
    assert correction.real.x == -1.8530010329390938e-12
    assert correction.real.u == 7.037918856330261e-14
    assert correction.imag.x == -4.381634944060136e-14
    assert correction.imag.u == 3.1661268566206577e-15

