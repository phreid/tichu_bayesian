import requests
import csv
import sys
import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def run_scraper(n_games,filename):
    """
    Scrape information on Tichu hands from the n_games most recent played games
    logged on http://log.tichumania.de/view/pages/Games.php, and write data
    to a csv file
    
    n_games: int
    filename: string
    """
    
    url = 'http://log.tichumania.de/view/pages/Games.php'
    header_names = ['player_name','gt_cards','final_cards','gt_call',
                    'tichu_call','out_first','player_elo']
                    
    csvfile = open(filename,'wb')
    writer = csv.writer(csvfile)
    writer.writerow(header_names)
    
    for game in get_game_urls(url,n_games):
        try:
            game_data = scrape_game(game)
            writer.writerows(game_data)
        except:
            pass
            
    csvfile.close()
    
def get_game_urls(url,n):
    """
    Return the n most recent game urls from the most recent games log page.
    Will open a Firefox window.
    
    url: string
    n: int
    
    returns: list of urls
    """
    driver = webdriver.Firefox()
    driver.get(url)
    
    game_urls = []
    i = 0
    while i < n:
        visible_games = driver.find_elements_by_class_name('gameLink')
        elem = driver.find_element_by_tag_name('a')
        elem.send_keys(Keys.PAGE_DOWN)
        i = len(visible_games)
    
    for elem in visible_games:
        game_urls.append(elem.get_attribute('href'))
        
    driver.quit()
    
    # while loop above is imprecise at hitting exactly n games      
    return game_urls[:n]
    
def scrape_game(game_url):
    """
    Given a game page url, scrape relevant information from each game round.
    
    game_url: string
    
    return: list
    """
    
    game = []
    for game_round in find_rounds(game_url):
        game.extend(find_round_results(game_round))
        
    elos = get_player_elos(game_url)
    for game_round in game:
        player_name = game_round[0]
        game_round.append(elos[player_name])
        
    return game

def find_rounds(game_url):
    """
    Given a game url, return a BeautifulSoup object containing the game rounds.
    
    game_url: string
    
    returns: BeautifulSoup object
    """
    
    game_page = requests.get(game_url).text
    soup = bs.BeautifulSoup(game_page)
    rounds = soup.findAll('div',{'class':'round'})
    
    return rounds    

def get_player_elos(game_url):
    """
    Find ELO rankings of players in the game.
    
    game_url: string
    
    returns: dict player_name:player_elo
    """
    
    game_page = requests.get(game_url).text
    soup = bs.BeautifulSoup(game_page)
    
    player_names = []
    player_elos = []
    for table in soup.findAll('div',{'class':'statisticTable'}):
        thead = table.find('thead')
        content = [item.text for item in thead.findAll('th')]
        player_names.append(content[1])
        player_names.append(content[2])
        
        tbody = table.find('tbody')
        for row in tbody.findAll('tr'):
            content = [item.text for item in row.findAll('td')]
            if content[0] == 'Elo score':
                player_elos.append(int(content[1]))
                player_elos.append(int(content[2]))
                
    return dict(zip(player_names,player_elos))

def find_round_results(single_round):
    """
    Given a BeautifulSoup object containing a single game round, find for 
    each player:
        - player name
        - grand tichu cards
        - final cards (after trades)
        - if the player called tichu
        - if the player called grand tichu
        - if the player went out first
        
    single_round: BS object
    
    returns: list of lists
    """
    
    player_names = get_player_names(single_round)
    gt_cards = get_gt_cards(single_round)
    final_cards = get_final_cards(single_round)
    tichu_calls = get_tichu_calls(single_round,player_names)
    gt_calls = get_gt_calls(single_round)
    out_first = get_out_first(single_round,player_names)
    
    return map(list,zip(player_names,gt_cards,final_cards,gt_calls,tichu_calls,out_first))
    
def get_player_names(single_round):
    """
    Find names of players in a single game round.

    single_round: BS object
    
    returns: list
    """    
    
    names = []
    for elem in single_round.findAll('div',{'class':'gtHands'}):
        for line in elem.findAll('div',{'class':'line'}):
            names.append(line.find('span',{'class':'tip'})['data-player'])
    return names
    
def get_gt_cards(single_round):
    """
    Find grand tichu cards of players in a single game round.

    single_round: BS object
    
    returns: list
    """ 
    
    gt_cards = []
    for elem in single_round.findAll('div',{'class':'gtHands'}):
        for line in elem.findAll('div',{'class':'line'}):
            for card_list in line.findAll('div',{'class':'cards'}):
                gt_cards.append([span['class'] for span in card_list])
    
    return gt_cards
    
def get_gt_calls(single_round):
    """
    Find grand tichu calls of players in a single game round.

    single_round: BS object
    
    returns: list
    """  
    
    gt_calls = []
    for elem in single_round.findAll('div',{'class':'gtHands'}):
        for line in elem.findAll('div',{'class':'line'}):
            if line.findAll('span',{'class':'actionItem gt'}) != []:
                gt_calls.append(1)  
            else:
                gt_calls.append(0)
    return gt_calls
    
def get_final_cards(single_round):
    """
    Find grand tichu cards of players in a single game round.

    single_round: BS object
    
    returns: list
    """ 
    
    final_cards = []
    for elem in single_round.findAll('div',{'class':'completeHands'}):
        for line in elem.findAll('div',{'class':'line big'}):
            for card_list in line.findAll('div',{'class':'cards'}):
                final_cards.append([card['class'] for card in card_list.findAll('span') \
                                    if 'tradeIcon' not in card['class']])
                                    
    return final_cards
    
def get_tichu_calls(single_round,player_names):
    """
    Find tichu calls of players in a single game round.

    single_round: BS object
    player_names: list
    
    returns: list
    """ 
     
    tichu_calls = []
    for elem in single_round.findAll('div',{'class':'subline'}):
        span = elem.find('span')
        if span:
            if 'Tichu' in span.text:
                player_name = span.text.split()[0]
                tichu_calls.append(player_name)
    
    return [int(name in tichu_calls) for name in player_names]

def get_out_first(single_round,player_names):
    """
    Find if players went out first in a single game round.

    single_round: BS object
    player_names: list
    
    returns: list
    """ 
    
    for elem in single_round.findAll('div',{'class':'gameMove'}):
        if (elem.findAll('div',{'class':'trading'}) != [] and 
            len(elem.findAll('div',{'class':'trading'})) == 
            len([line.findAll('span') for line in elem.find('div',{'class':'cards'})])):
                first_out = elem.find('span',{'class':'tip'})['data-player']
                break
    
    return [int(name == first_out) for name in player_names]
    
if __name__ == '__main__':
   n_games,output_file = int(sys.argv[1]),sys.argv[2]
   run_scraper(n_games,output_file)