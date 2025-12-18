import requests
import json
from os.path import isfile
import time
from tqdm import tqdm
import sys
from collections import defaultdict
import numpy as np
import pandas as pd
import pickle
from od_pull import get_match, pro_list, pub_list






def parse_match(match, type=0):
    result = {}
    result['class'] = type
    result['teamfights'] = len(match.get('teamfights', []))
    # result['lobby_type'] = match['lobby_type']

    values = defaultdict(list)

    rad_gold_adv = match['radiant_gold_adv']

    players = match['players']
    for player in players:
        values['obs_placed'].append(player['obs_placed'])
        values['sen_placed'].append(player['sen_placed'])
        values['item_uses'].append(sum(player['item_uses'].values()))
        values['ability_uses'].append(sum(player['ability_uses'].values()))
        values['healing'].append(player['hero_healing'])
        values['damage'].append(player['hero_damage'])
        values['kills'].append(player['kills'])
        values['deaths'].append(player['deaths'])
        values['assists'].append(player['assists'])
        values['last_hits'].append(player['last_hits'])
        values['denies'].append(player['denies'])
        values['gold_per_min'].append(player['gold_per_min'])
        values['xp_per_min'].append(player['xp_per_min'])
        values['lane_efficiency'].append(player.get('lane_efficiency', 0))
        values['actions_per_min'].append(player['actions_per_min'])
        values['stuns'].append(player['stuns'])
        values['camps_stacked'].append(player['camps_stacked'])

    for key in values:
        vals = np.asarray(values[key])
        result[key + '_mean'] = vals.mean()
        result[key + '_std'] = vals.std()
    return result




def main():
    match_fields = []
    for m_id in pro_list(1000):
        match = get_match(m_id)
        # filter out games shorter than 20min or haven't been parsed by API yet
        if match['duration'] < 1200 or not match['od_data']['has_parsed']:
            continue
        match_fields.append(parse_match(match, 1))

    for m_id in pub_list(1200):
        match = get_match(m_id)
        if match['duration'] < 1200 or not match['od_data']['has_parsed']:
            continue
        match_fields.append(parse_match(match, 0))


    matches_df = pd.DataFrame(match_fields)
    matches_df.to_pickle('data\\match_data.pkl')
    print('done')




if __name__ == '__main__':
    main()
