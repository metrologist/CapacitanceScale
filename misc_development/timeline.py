import matplotlib.pyplot as plt
from datetime import date
import numpy as np

dates = [date(1864, 10, 26), date(1875, 5, 20), date(1926, 8, 31), date(1945, 10, 24), date(1991, 6, 1), date(1992, 6, 15), date(1999, 10, 14), date(2026, 5, 20)]
min_date = date(np.min(dates).year - 2, np.min(dates).month, np.min(dates).day)
max_date = date(np.max(dates).year + 2, np.max(dates).month, np.max(dates).day)

labels = ['Ordinance for Standard\nWeights and Measures', 'Metre Convention', 'DSIR\nEstablished',
          'DSIR ammendment\nPrincipal standard measures', 'NZ signs\nMetre\nConvention', 'Measurement\nStandards Act\nMSL', 'CIPM MRA', 'WMD\n2026']
# labels with associated dates
labels = ['{0:%d %b %Y}:\n{1}'.format(d, l) for l, d in zip(labels, dates)]

fig, ax = plt.subplots(figsize=(15, 4), constrained_layout=True)
_ = ax.set_ylim(-2, 1.75)
_ = ax.set_xlim(min_date, max_date)
_ = ax.axhline(0, xmin=0.05, xmax=0.95, c='deeppink', zorder=1)

_ = ax.scatter(dates, np.zeros(len(dates)), s=120, c='palevioletred', zorder=2)
_ = ax.scatter(dates, np.zeros(len(dates)), s=30, c='darkmagenta', zorder=3)
label_offsets = np.zeros(len(dates))
label_offsets[::2] = 0.35
label_offsets[1::2] = -0.7 * 1.2
for i, (l, d) in enumerate(zip(labels, dates)):
    _ = ax.text(d, label_offsets[i], l, ha='center', fontfamily='sans-serif', fontweight='normal', color='royalblue',fontsize=10)
stems = np.zeros(len(dates))
stems[::2] = 0.3
stems[1::2] = -0.3
markerline, stemline, baseline = ax.stem(dates, stems)
_ = plt.setp(markerline, marker=',', color='darkmagenta')
_ = plt.setp(stemline, color='darkmagenta')
# hide lines around chart
for spine in ["left", "top", "right", "bottom"]:
    _ = ax.spines[spine].set_visible(False)

# hide tick labels
_ = ax.set_xticks([])
_ = ax.set_yticks([])

# _ = ax.set_title('Metrology Milestones', fontweight="bold", fontfamily='sans-serif', fontsize=16,
#                  color='royalblue')
plt.savefig('timeline.png', transparent=True)
plt.show()
