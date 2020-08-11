#  python3.8 som environment
from meas_cap_ratio import CAPSCALE
from GTC import ureal
from GTC.reporting import budget  # just for checks

# For now the starting point is an NMIA value of AH11C1
w = 1e4  # rad/s
cap = 99.999581e-12  # pF
ucap = 0.11e-6  # relative expanded uncertainty, k = 2
dfact = 1.9e-6  # dissipation factor S/F/Hz
udfact = 0.6e-6 # S/F/Hz, k=2
g = ureal(dfact * w * cap, udfact/2 * w * cap, 50, label='ah11c1d')
c = ureal(cap, cap * ucap / 2 , 50, label='ah11c1c')
cert = g + 1j * w * c  # admittance of reference at angular frequency w
print('reference value for buildup = ', repr(cert))
# uses this reference value in CAPSCALE
buildup = CAPSCALE('G:\\My Drive\\KJ\\PycharmProjects\\CapacitanceScale\\datastore',
                   ['in.csv', 'leads_and_caps.csv'], 'out.csv', cert)
buildup.buildup()
buildup.store_buildup()

# example uncertainty budget
select = buildup.caps['gr1000a'].best_value
# capacitance is imaginary part
capacitance = select.imag/buildup.w
print(capacitance)
print('budget')
print(capacitance.u / capacitance * 1e6)
for label, u in budget(capacitance, trim=0):
    print("{:^20} {:.2e}   {:.3f}".format(label, u, u/capacitance.x * 1e6))