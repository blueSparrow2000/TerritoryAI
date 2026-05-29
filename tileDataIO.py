import pygame
import os, sys
from pattern_generator import *

def read_all_file_names(folderName):
    folderName += '/'
    all_file_names = list(os.listdir(folderName))
    # remove '.txt' part
    all_file_names = [file_name[:-4] for file_name in all_file_names]
    # print(all_file_names)
    return all_file_names

'''
Read tilemap text data and make it into 2D array
'''
def read_tile_map(fileName):
    APP_FOLDER = os.path.dirname(os.path.realpath(sys.argv[0])) + '/tileMaps/'
    full_path = os.path.join(APP_FOLDER, '{}.txt'.format(fileName))

    # check generic map names ; such as 'blank' will make general col x row space
    # 1. generic map class of 'name col row'.txt
    if fileName.startswith('blank'):
        mapName, col, row = fileName.split(' ')
        col,row = int(col),int(row)
        if col < 4 or row < 4:
            print("[Error generating tilemap] Col, Row must be at least 4")
            sys.exit(0)

        tiles = [['w' for _ in range(col)] for _ in range(row)]
        return tiles

    # 2. generic map class of 'circle radius'.txt
    if fileName.startswith('circle'):
        # if file exists, read it
        # generate circle pattern and read
        mapName, radius = fileName.split(' ')
        radius = int(radius)
        if radius < 8:
            print("[Error generating tilemap] Radius must be at least 8")
            sys.exit(0)

        tiles = circleTileMapGenerator(radius) #[['w' for _ in range(radius*2+1)] for _ in range(radius*2+1)]
        return tiles

    return generate_tile_map(full_path)

def generate_tile_map(full_path):
    tiles = []
    # instantiate each text into tiles
    with open(full_path, "r") as f:
        lines = [line.strip() for line in f.readlines()] # each lines
        lines = [line for line in lines if line[0]!='#'] # comment 줄 제거
        tiles = [line.split(' ') for line in lines]# space(공백)으로 구분된 파일 (w r r w r ... 이런 식으로)

    return tiles

def init_trajectory_data(fileName, mapName):
    APP_FOLDER = os.path.dirname(os.path.realpath(sys.argv[0])) + '/trajectoryData/'
    full_path = os.path.join(APP_FOLDER, '{}.txt'.format(fileName))
    with open(full_path, "w") as f:
        f.write(mapName)
        f.write('\n')

def write_trajectory_data(fileName, bot_initial_pos, bot_color, data_list):
    APP_FOLDER = os.path.dirname(os.path.realpath(sys.argv[0])) + '/trajectoryData/'
    full_path = os.path.join(APP_FOLDER, '{}.txt'.format(fileName))
    # print(data_list)
    bot_info = "{} {} {}".format(bot_initial_pos[0], bot_initial_pos[1], bot_color)
    trajectory = " ".join(map(str, data_list))

    with open(full_path, "a") as f:
        f.write(bot_info)
        f.write('\n')
        f.write(trajectory)
        f.write('\n')

def read_trajectory_data(fileName):
    APP_FOLDER = os.path.dirname(os.path.realpath(sys.argv[0])) + '/trajectoryData/'
    full_path = os.path.join(APP_FOLDER, '{}.txt'.format(fileName))
    data = []
    # instantiate each text into tiles
    with open(full_path, "r") as f:
        lines = [line.strip() for line in f.readlines()] # each lines
        data.append(lines[0]) # mapname
        lines = lines[1:]
        bot_num = len(lines)//2
        for bot_i in range(bot_num):
            bot_info = lines[2 * bot_i].split(' ') # x, y, color
            botx,boty,bot_color = int(bot_info[0]),int(bot_info[1]),bot_info[2]
            bot_trajectory = list(map(int,  lines[2 * bot_i + 1].split(' ') ))
            data.append([botx,boty,bot_color,bot_trajectory])
        # line = f.readline().strip().split(' ') # 공백 구분자
        # data = list(map(int, line))
    return data


def printMat(tiles):
    xlen = len(tiles[0])
    for y in range(len(tiles)):
        info = ''
        for x in range(xlen):
            info += tiles[y][x].display_color + ' '

        print(info)


def write_tile_pattern(patternName, col, row, pattern):
    APP_FOLDER = os.path.dirname(os.path.realpath(sys.argv[0])) + '/tileMaps/'
    fileName = '{} {} {}.txt'.format(patternName, col, row)
    full_path = os.path.join(APP_FOLDER, fileName)
    with open(full_path, "w") as f:
        f.write(pattern)


# def printMat(data):
#     xlen = len(data[0])
#     for y in range(len(data)):
#         info = ''
#         for x in range(xlen):
#             info += str(data[y][x]) + ' '
#
#         print(info)








