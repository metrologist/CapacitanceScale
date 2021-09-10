"""
test_cal_balance.py
"""
def test_dialfactors():
    from cal_balance import DIALCAL
    import os
    cwd = (os.getcwd())
    # equation 38 of E.005.003
    cal_dials = DIALCAL(cwd + '\\files_for_test',
                        ['dialcal_in_2021-09-03.csv', 'comp_leads_caps_2021-09-02.csv'], 'dial_factor_out.csv')
    factora, factorb = cal_dials.dialfactors(file_output=True, append=False)
    assert factora.x==1.0003524339813534 + 1j * 0.0005839748330213842
    assert factorb.x==1.0002333356352149-1j * 0.00041983101116730635