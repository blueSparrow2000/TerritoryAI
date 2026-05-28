import pygame
import os, sys

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
    tiles = []
    # instantiate each text into tiles
    with open(full_path, "r") as f:
        lines = [line.strip() for line in f.readlines()] # each lines
        lines = [line for line in lines if line[0]!='#'] # comment 줄 제거
        tiles = [line.split(' ') for line in lines]# space(공백)으로 구분된 파일 (w r r w r ... 이런 식으로)

    return tiles

def printMat(tiles):
    xlen = len(tiles[0])
    for y in range(len(tiles)):
        info = ''
        for x in range(xlen):
            info += tiles[y][x].display_color + ' '

        print(info)











