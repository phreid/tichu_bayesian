import pandas as pd
import numpy as np
from csv import DictReader

def load_card_dict(filename):
    """
    Create a dictionary mapping css card names to a more readable format.
    
    filename: string. location of css-card name csv file.
    
    returns: dict
    """
    card_dict = {}
    with open(filename) as csvfile:
        reader = DictReader(csvfile)
        for row in reader:
            card_dict[row['html']] = row['card']
    return card_dict

def get_ranks_only(hand):
    """
    Hand suits aren't useful in this analysis. Given a list of tichu cards,
    return only the rank of each card.
    
    hand: list of strings
    
    returns: list of strings
    """
    ranks = []
    for card in hand:
        if card in ['Dr','Ph','Mahj','Dog']:
            ranks.append(card)
        else:
            ranks.append(card[0])
    return ranks

def vectorize_single_hand(hand,feature_list,boolean=False):
    """
    Given a list of card ranks, convert it to a vector of features.
    
    hand: list of strings
    feature_list: list of strings
    boolean=False: if False, count the number of occurences of each feature
                   if True, return a Boolean if the hand contains each feature
    
    returns: list of ints
    """
    vec = np.zeros(len(feature_list))
    for i,feature in enumerate(feature_list):
        if boolean:
            vec[i] = int(feature in hand)
        else:
            vec[i] = hand.count(feature)
    return vec

def vectorize_hands(df,function,feature_list,hand_type,boolean=False):
    """
    Apply a vectorizer function across feature_list columns of a pandas
    DataFrame.
    
    df: pandas DataFrame containing at least one column of card lists
    function: vectorizer to apply
    feature_list: list
    hand_type: string. column of df to apply vectorizer. In this case, one of 
                       'gt_cards', 'final_cards'
    boolean=False: if False, count the number of occurences of each feature
                   if True, return a Boolean if the hand contains each feature
    
    returns: DataFrame
    """

    vectorize = lambda x: function(x,feature_list,boolean)
    vec_matrix = [x for x in df[hand_type].apply(vectorize).values]
    new_df = pd.DataFrame(vec_matrix,columns=feature_list)
    return new_df

def load_clean_vectorize(data_filename,card_dict_filename,feature_set,hand_type):
    """
    Load a csv file containing Tichu data from scraper.py, clean and vectorize
    it.
    
    data_filename: string
    card_dict_filename: string
    feature_set: list
    hand_type: string
    
    returns: DataFrame
    """
    df = pd.read_csv(data_filename)
    card_dict = load_card_dict(card_dict_filename)
    
    df.gt_cards = df.gt_cards.apply(eval)
    df.final_cards = df.final_cards.apply(eval)
    df.gt_cards = df.gt_cards.apply(lambda x: [card_dict[c] for c in x])
    df.final_cards = df.final_cards.apply(lambda x: [card_dict[c] for c in x])
    
    df.gt_cards = df.gt_cards.apply(get_ranks_only)
    df.final_cards = df.final_cards.apply(get_ranks_only)
    
    vec_df = vectorize_hands(df,vectorize_single_hand,feature_set,hand_type)
    
    vec_df = pd.concat([vec_df,df.drop(['gt_cards','final_cards'],axis=1)],axis=1)
    
    return vec_df