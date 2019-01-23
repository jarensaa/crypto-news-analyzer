import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_correlation(price, social, x, lags, ccor):

    fig, axs = plt.subplots(nrows=2)
    fig.subplots_adjust(hspace=0.4)
    ax = axs[0]
    ax.plot(x, price, 'b', label='price')
    ax.plot(x, social, 'r', label='social media score')
    ax.legend(loc='upper right', fontsize='small', ncol=2)

    ax = axs[1]
    ax.plot(lags, ccor)
    ax.set_ylim(-1.1, 1.1)
    ax.set_ylabel('cross-correlation')
    ax.set_xlabel('lag of price in hours relative to social media activity')

    maxlag = lags[np.argmax(ccor)]
    print("max correlation is at lag %d" % maxlag)
    plt.show()

def plot_autocorrelation(autocorr_xdm, lags):

    fig, ax = plt.subplots()
    ax.plot(lags, autocorr_xdm, 'r')
    ax.set_xlabel('lag')
    ax.set_ylabel('correlation coefficient')
    ax.grid(True)
    plt.show()


corr = pd.read_pickle('corr.pkl')
corrs = corr['maxlag'].drop_duplicates()

x = list(range(len(corrs)))
fig, ax = plt.subplots()
ax.plot(x, corrs, 'r', label='time lag')
#ax.plot(x, corr['corrR'], 'b', label='correlation random timeperiod')
#ax.ticks
ax.set_xlabel('different changepoints over time')
ax.set_ylabel('time lag in hours at highest correlation')
ax.grid(True)
ax.legend(loc='upper right', fontsize='small', ncol=2)
plt.show()