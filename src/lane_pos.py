import requests
import json
from os.path import isfile
import time
from tqdm import tqdm
import sys
from collections import defaultdict
import numpy as np
import pandas as pd
from od_pull import get_match, pro_list, pub_list
from matplotlib import pyplot as plt
import seaborn as sns
from skimage.measure import block_reduce
import skimage as ski
from sklearn.decomposition import PCA


def get_lane_pos(match):
    players = match['players']
    position_counts = []
    for player in players:
        for x, ys in player['lane_pos'].items():
            for y, count in ys.items():
                position_counts.append((int(x), int(y), int(count)))
    return position_counts


def plot_positions(positions):
    mat = gen_pos_matrix(positions)
    plt.suptitle('Positions of all players during laning stage')
    plt.subplot(1, 2, 1)
    x, y, c = zip(*positions)
    plt.scatter(x, y, c=c)
    plt.subplot(1, 2, 2)

    cmap = plt.get_cmap('cividis')
    cmap.set_under('white')  # Color for values less than vmin
    cmap.set_over('red')

    heat = plt.imshow(mat, interpolation='none', vmin=.5, vmax=25, cmap=cmap)
    plt.colorbar(heat, extend='min')

    plt.show()


def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


def gen_pos_matrix(pts):
    result = np.zeros((140, 140))
    for pt in pts:
        x, y, c = pt
        x = clamp(x - 60, 0, result.shape[0]-1)
        y = clamp(y - 60, 0, result.shape[1]-1)
        result[y, -x] = c
    result = block_reduce(result, 2)
    return result

# returns list of tuples (player_slot, player_role)
# 11 rad safe, 33 rad off, 22 mid, 13 dire off, 31 dire safe
def identify_roles(match):
    players = match['players']
    results = []
    dire_off = []
    rad_off = []
    dire_safe = []
    rad_safe = []
    dire = []
    radiant = []
    for player in players:
        player_slot = player['player_slot']
        player_lane = player['lane']
        player_role = player['lane_role']
        lane_kills = player['lane_kills']



    #     if player_role == 1 and player_lane == 1:
    #         rad_safe.append((lane_kills, player_slot))
    #     if player_role == 3 and player_lane == 3:
    #         rad_off.append((lane_kills, player_slot))
    #     if player_role == 1 and player_lane == 3:
    #         dire_off.append((lane_kills, player_slot))
    #     if player_role == 3 and player_lane == 1:
    #         dire_safe.append((lane_kills, player_slot))
    #     if player_role == 2 and player_lane == 2:
    #         results.append((player_slot, 2))
    #
    # if dire_off[0][0] > dire_off[1][0]:
    #     results.append((dire_off[0][1], 3))
    #     results.append((dire_off[1][1], 4))
    # else:
    #     results.append((dire_off[0][1], 4))
    #     results.append((dire_off[1][1], 3))
    #
    # if dire_safe[0][0] > dire_safe[1][0]:
    #     results.append((dire_safe[0][1], 1))
    #     results.append((dire_safe[1][1], 5))
    # else:
    #     results.append((dire_safe[0][1], 5))
    #     results.append((dire_safe[1][1], 1))
    # # =============
    # if rad_off[0][0] > rad_off[1][0]:
    #     results.append((rad_off[0][1], 3))
    #     results.append((rad_off[1][1], 4))
    # else:
    #     results.append((rad_off[0][1], 4))
    #     results.append((rad_off[1][1], 3))
    #
    # if rad_safe[0][0] > rad_safe[1][0]:
    #     results.append((rad_safe[0][1], 1))
    #     results.append((rad_safe[1][1], 5))
    # else:
    #     results.append((rad_safe[0][1], 5))
    #     results.append((rad_safe[1][1], 1))

    return results



def get_role_positions(match, lane, role):
    players = match['players']
    results = []
    # roles = identify_roles(match)
    # role_ids = [elt[0] for elt in roles if elt[1] == role]

    for player in players:
        player_slot = player['player_slot']
        # if player_slot not in role_ids:
        #     continue
        player_lane = player['lane']
        player_role = player['lane_role']
        if player_lane != lane or player_role != role:
            continue

        positions = []
        for x, ys in player['lane_pos'].items():
            for y, count in ys.items():
                positions.append((int(x), int(y), int(count)))
        results.append(gen_pos_matrix(positions).flatten())
    return results


def main():

    match = get_match(7704459920)
    pos = get_lane_pos(match)
    plot_positions(pos)



    pro_pos = []
    pub_pos = []
    pros = pro_list(1000)
    pubs = pub_list(1000)
    for m_id in pros:
        match = get_match(m_id)
        pro_pos += get_role_positions(match, 3, 3)
    for m_id in pubs:
        match = get_match(m_id)
        pub_pos += get_role_positions(match, 3, 3)
    X_pros = np.asarray(pro_pos).T.astype(float)
    X_pubs = np.asarray(pub_pos).T.astype(float)

    m = 10
    pca_pros = PCA(n_components=m)
    pca_pubs = PCA(n_components=m)

    eigens_pros = pca_pros.fit_transform(X_pros)
    eigens_pubs = pca_pubs.fit_transform(X_pubs)


    # for i in range(m):
    #     pro_face = eigens_pros[:, i].reshape((70, 70))
    #     plt.imshow(pro_face, cmap=plt.cm.gray)
    #     plt.set_title('Pro Eigen ' + str(i))
    #     plt.show()

    for i in range(m):
        pro_face = eigens_pros[:, i].reshape((70, 70))
        pub_face = eigens_pubs[:, i].reshape((70, 70))
        fig, (ax1, ax2, ax3) = plt.subplots(1,3)
        ax1.imshow(pro_face, cmap=plt.cm.gray)
        ax2.imshow(pub_face, cmap=plt.cm.gray)
        ax3.imshow(pro_face - pub_face, cmap=plt.cm.gray)
        ax1.set_title('Pro Eigen ' + str(i))
        ax2.set_title('Amateur Eigen ' + str(i))
        ax3.set_title('Diff in Eigen ' + str(i))
        plt.show()


    # match = get_match(7704459920)
    # players = match['players']
    # for player in players:
    #     player_slot = player['player_slot']
    #     player_lane = player['lane']
    #     player_role = player['lane_role']
    #     lane_kills = player['lane_kills']
    #     print(player_slot, player_lane, player_role, lane_kills)
    #
    # roles = identify_roles(match)

    print('done')




if __name__ == '__main__':
    main()