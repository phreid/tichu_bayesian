import sys
from load_data import load_clean_vectorize
from model import *

if __name__ == '__main__':
    unique_ranks = ['Dr','Ph','A','K','Q','J','T',
                    '9','8','7','6','5','4','3','2','Mahj','Dog']
                    
    print 'Loading data...'
    data = load_clean_vectorize('data/tichu_data.csv','data/tichucards.csv',
                                unique_ranks,'final_cards')
                                
    hand_crit = eval(sys.argv[1])
    mcmc = model(data,hand_crit,unique_ranks)
    print 'Fitting model...'
    mcmc.sample(20000,5000,5)
    plot_traces(mcmc,hand_crit)
    print '\nFinished.'