import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pymc as pm
from load_data import vectorize_single_hand

plt.rcParams['figure.figsize'] = (10,6)
plt.style.use('bmh')

def model(df,hand_crit,unique_ranks):
    """
    Set up model as described in README.
    
    df: DataFrame containing vectorized Tichu hands
    hand_crit: list or list of lists. Hand(s) to estimate are input as lists of
                strings with format:
               [[Card1,...] (,[Card1,...])]
    unique_ranks: list of unique tichu card ranks for use in vectorizer
    
    returns: PyMC MCMC object
    """
    
    if type(hand_crit[0]) != (list or np.ndarray):
        hand_crit= [[x] for x in hand_crit]
    
    p = np.empty(len(hand_crit),dtype=object)
    obs = np.empty(len(hand_crit),dtype=object)
    
    for i,hand in enumerate(hand_crit):
        name = '-'.join(hand)
        
        p[i] = pm.Uniform('p_' + name,0,1)
    
        c = vectorize_single_hand(hand,unique_ranks)
        occurences = df[(df['Dr'] >= c[0]) &
                        (df['Ph'] >= c[1]) &
                        (df['A'] >= c[2]) &
                        (df['K'] >= c[3]) &
                        (df['Q'] >= c[4]) &
                        (df['J'] >= c[5]) &
                        (df['T'] >= c[6]) &
                        (df['9'] >= c[7]) &
                        (df['8'] >= c[8]) &
                        (df['7'] >= c[9]) &
                        (df['6'] >= c[10]) &
                        (df['5'] >= c[11]) &
                        (df['4'] >= c[12]) &
                        (df['3'] >= c[13]) &
                        (df['2'] >= c[14]) &
                        (df['Mahj'] >= c[15]) &
                        (df['Dog'] >= c[16])].out_first.values
        
        obs[i] = pm.Bernoulli('obs_' + name,p[i],value=occurences,observed=True)
        
    out_first = pm.Bernoulli('out_first',p)
    model = pm.Model([pm.Container(p),out_first,pm.Container(obs)])
    mcmc = pm.MCMC(model)
    return mcmc
    
def plot_traces(mcmc,hand_crit):
    """
    Plot posterior distributions and means for each hand in hand_crit, and save
    as .png in \plots folder

    mcmc: PyMC MCMC object from model()
    hand_crit: list or list of lists as described in model()
    """    
    
    if type(hand_crit[0]) != (list or np.ndarray):
        hand_crit= [[x] for x in hand_crit]
        
    names = map('-'.join,hand_crit)
    
    for i,name in enumerate(names):
        plt.hist(mcmc.trace('p_' + name)[:],histtype='stepfilled',label=name,alpha=0.75)
        plt.axvline(mcmc.trace('p_' + name)[:].mean(),
                    color=plt.rcParams['axes.color_cycle'][i],linestyle='--')
        plt.legend(bbox_to_anchor=(1.2, 1))
        
    plt.grid(False)
    plt.title('Posterior Distribution(s) and Mean(s) of $P_{cards}$')
    
    plt.savefig('plots\%s.png' % ','.join(names), bbox_inches='tight')
