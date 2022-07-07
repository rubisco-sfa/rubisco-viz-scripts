from condastats.cli import overall
import pandas as pd
import os
import matplotlib
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
font = {'size'   : 18}
matplotlib.rc('font', **font)

if not os.path.isfile("ilamb.pkl"):
    out = overall("ilamb", monthly=True)
    out.to_pickle("ilamb.pkl")
else:
    out = pd.read_pickle("ilamb.pkl")
out = out.reset_index()


tag = pd.DataFrame({'time':['2018-06','2019-01','2019-09','2021-05'],
                    'release':['v2.3','v2.4','v2.5','v2.6'],
                    'counts':[0,89,132,1595]},columns=['time','release','counts'])
out['time'] = pd.to_datetime(out['time'])
tag['time'] = pd.to_datetime(tag['time'])

fig,ax = plt.subplots(figsize=(16,6),tight_layout=True)
ax.plot(out['time'],out['counts'],'-')
for i, r in tag.iterrows():
    ax.plot(r["time"], r["counts"],'ok')
    ax.text(r["time"], r["counts"]+20, r["release"],va='bottom',ha='center')
ax.set_ylabel("monthly conda installs")
ax.set_xlim(pd.to_datetime('2018-05-01'),pd.to_datetime('2022-01-01'))
ax.set_xticks([])
ax.set_ylim(-50,1700)

ax.fill_between([pd.to_datetime('2018-05-01'),pd.to_datetime('2019-01-01')],
                [-100,-100],[1710,1710],color='k',alpha=0.1,lw=0)
ax.fill_between([pd.to_datetime('2020-01-01'),pd.to_datetime('2021-01-01')],
                [-100,-100],[1710,1710],color='k',alpha=0.1,lw=0)
ax.text(pd.to_datetime('2019-01-01'),1650," 2019",size=24,weight='bold',color='k',alpha=0.1,va='top')
ax.text(pd.to_datetime('2021-01-01'),1650," 2021",size=24,weight='bold',color='k',alpha=0.1,va='top')
ax.text(pd.to_datetime('2020-01-01'),1650," 2020",size=24,weight='bold',color='w',va='top')
fig.savefig("timeline.png")
plt.show()
