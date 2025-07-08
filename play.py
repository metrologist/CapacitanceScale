import GTC
from msl.nlf import Model
from math import pi


x = [1.6, 3.2, 5.5, 7.8, 9.4]
y = [7.8, 19.1, 17.6, 33.9, 45.4]
model = Model("a1+a2*x")
result = model.fit(x, y, params=[1, 1])
print(result.params)
print(result.to_ureal())

# l = 1.0
r = 600
c = 3.442e-11
c = c * 1.43  # some capacitance in the coil?
c = 0.43 * c
w = 1e4
# z1 = r + 1j * w * l
# z2 = 1 / (1j * w * c)
# ztot = z1 * z2 / (z1 + z2)
# print(ztot)
# ltot = ztot.imag / w
# print('effective inductance =',ltot, 'H')
# print('an increase of ',(ltot / l - 1) * 100, '%')

def ztot(l, r):
    z1 = r + 1j * w * l
    z2 = 1 / (1j * w * c)
    ztot = z1 * z2 / (z1 + z2)
    # print(ztot)
    ltot = ztot.imag / w
    # print('effective inductance =', ltot, 'H')
    # print('an increase of ', (ltot / l - 1) * 100, '%')
    print('ztot =', ztot)
    return ltot

def alt_ltot(l, r):
    alt_l = (l - r**2 * c - w**2 * l**2 * c) / ((1 - w**2 * l * c)**2 + (w * r * c)**2)
    print(l, alt_l)
    return alt_l

def simpl(l):
    simp_l = l / (1 - w**2 * l * c)
    return simp_l

induct = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8 ,0.9 ,1.0]
resist = [168.0187428, 243.8520811, 301.4602532, 350.4856378, 396.4452306, 440.2763314, 481.8281965, 520.3136875, 558.7898957, 600]

delta = []
delta2 = []
delta3 = []
for i in range(len(induct)):
    d = ztot(induct[i], resist[i]) - induct[i]
    d2 = alt_ltot(induct[i], resist[i]) - induct[i]
    d3 = simpl(induct[i]) - induct[i]
    print(d-d2)
    delta.append(d)
    delta2.append(d2)
    delta3.append(d3)
    print(d, d2, d3)

print(delta)
for x in delta:
    print(x)

for x in delta2:
    print(x)

for x in delta3:
    print(x)
print('for 1 H only')
# for 1 H only
induct9 = induct[9]
resist9 = resist[9]
print('induct, resist =', induct9, resist9)
w = 1e4
L1 = ztot(induct9, resist9)
print(w, L1)
w = w * 1.05
L2 = ztot(induct9, resist9)
print(w, L2)
print('frequency =', w/(2 * pi))
print((L2 / L1 -1) * 1e6)
print('cap =', c)