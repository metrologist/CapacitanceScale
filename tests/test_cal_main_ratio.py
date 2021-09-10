"""
test_cal_main_ratio.py
"""
def test_calc_raw_ratio():
    import os
    cwd = os.getcwd()
    from cal_main_ratio import PERMUTE
    ratio_cal = PERMUTE(cwd + '\\files_for_test',
                        ['ratiocal_in_2021-09-03.csv', 'comp_leads_caps_2021-09-02.csv', 'dial_factor_out.csv',
                         'comp_permute_2021-09-02.csv'], 'ratiocal_out_2021-09-03.csv')
    raw_ratio = ratio_cal.calc_raw_ratio()
    assert raw_ratio.x==10.000018239084838-0.00018105879574237794j
    main_ratio = ratio_cal.correct_ratio(raw_ratio)
    assert main_ratio.x==10.000018421928607-0.0001820228269418922j
