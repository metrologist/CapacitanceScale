"""
test_meas_cap_ratio.py
"""
def test_cap_ratio():
    import os
    from GTC import ureal, ucomplex
    from meas_cap_ratio import CAPSCALE

    cwd = os.getcwd()
    w = 1e4  # rad/s
    cap = 99.999581e-12  # pF
    ucap = 0.11e-6  # relative expanded uncertainty, k = 2
    dfact = 1.9e-6  # dissipation factor S/F/Hz
    udfact = 0.6e-6  # S/F/Hz, k=2
    g = ureal(dfact * w * cap, udfact / 2 * w * cap, 50, label='ah11c1d')
    c = ureal(cap, cap * ucap / 2, 50, label='ah11c1c')
    cert = g + 1j * w * c  # admittance of reference at angular frequency w
    final_ratio = ucomplex(10.00001763921027 + 1j * -0.0001684930432066416, (1e-10, 1e-10), df=100, label="main_ratio")
    factora = ucomplex(1.0003093210681406 + 1j * 0.0007497042903003306, (1e-10, 1e-10), df=100, label='factora')
    factorb = ucomplex(1.0001942917392947 + 1j * -0.00023893092658472306, (1e-10, 1e-10), df=100, label='factorb')
    buildup = CAPSCALE(cwd + r'\files_for_test',
                       [r'in3.csv', r'leads_and_caps.csv'], r'out3.csv', cert,
                       afactor=factora, bfactor=factorb, ratio=final_ratio)
    ah11c1 = buildup.caps['ah11c1']
    ah11c1.set_best_value(cert)  # force the value to cert (but doesn't change in leads_and_caps.csv
    hv2_xfrm = buildup.leads['hv2_xfrm']
    lv2 = buildup.leads['lv2']
    hv1 = buildup.leads['hv1']
    lv1 = buildup.leads['lv1']
    balances = buildup.balance_dict
    r4 = balances['r4']
    a1 = buildup.cap_ratio(r4, ah11c1.best_value - ah11c1.lead_correction(hv2_xfrm, lv2), True)
    buildup.caps['ah11a1'].set_best_value(a1 + buildup.caps['ah11a1'].lead_correction(hv1, lv1))  # value with no leads
    result_test = buildup.caps['ah11a1'].best_value.imag.x
    assert result_test==9.999950862604164e-08
