# # Making sure that application of the constraint and temperature corrections will be handled correctly.
#
#
# def val_t(val, alpha, t, t_ref):
#     """
#
#     :param val: reference value of capacitor at reference temperature, t_ref
#     :param alpha: temperature coefficient of capacitor in ppm/degree
#     :param t: temperature at which the value is calculated
#     :param t_ref: default reference temperature
#     :return: value at temperature t
#     """
#     val_at_temp = val * (1 + alpha * 1e-6 * (t - t_ref))
#     return val_at_temp
#
# # set of capacitors with known values at 20 degrees
# a20 = 10 * (1 + 120e-6)
# a_alpha =150  # ppm
# a25 = val_t(a20, a_alpha, 25, 20)
# print('a25 =', a25)
#
# b20 = 10 * (1 + 250e-6)
# b_alpha = -a_alpha
# b25 = val_t(b20, b_alpha, 25, 20)
# print('b25 =',b25)
#
# c = 100  # a temperature indpependent capacitor for now
#
# # measure ratios at 25 degrees
# r1 = a25 / c
# r2 = b25 / c
# print('check b25 =', a25 * r2 / r1)
# print('check b20 =', a20 * r2 / r1 )
# print('b20 =', b20)


# # testing storage options for environmental conditions
# from archive import GTCSTORE
# from GTC import ureal
# from json import dumps, loads
#
# st = GTCSTORE()
# temp = ureal(20.0, 0.2)
# temp_dict = st.ureal_to_dict(temp)
# print(temp_dict)
# new_temp = st.dict_to_ureal(temp_dict)
# print(new_temp)
# temp_json = st.ureal_to_json(temp)
# print(temp_json)  # so json seems to do the dictionary thing to ureals
#
# conditions = {}
# conditions1 = {'AH1': ureal(29, 0.1), 'AH2': ureal(31, 0.1)}
# for x in conditions1:
#     print(x)
#     conditions[x] = st.ureal_to_dict(conditions1[x])
# # conditions = {'AH1': st.ureal_to_dict(ureal(29, 0.1)), 'AH2': st.ureal_to_dict(ureal(31, 0.1))}  # dictionary
# print('conditions =', conditions)
# cond_json = dumps(conditions)
# print('cond_json =', cond_json)
# new_cond = loads(cond_json)
# print('new_cond =', new_cond)
# print(new_cond['AH1'])
# print(st.dict_to_ureal(new_cond['AH1']))

# for the nanoparticle capacitance paper
from GTC import ureal
def capfit(cap):
    a = ureal(0.9, 0.1)
    b = ureal(1.0, 0.02)
    c_meas = a * cap**b
    error = (c_meas / cap - 1) * 100
    return (c_meas, error)

capac = [1, 10, 100, 1000]
for x in capac:
    c_m = capfit(x)
    print(x, 'pF', c_m[0], 'pF', c_m[1], '%')