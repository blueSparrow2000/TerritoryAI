import math

def circleTileMapGenerator(radius, verbose = False):
    tileMap = []
    # dist represents distance to the center
    # for horizontal movement
    for i in range((2 * radius) + 1):
        each_row = []
        # for vertical movement
        for j in range((2 * radius) + 1):

            dist = math.sqrt((i - radius) * (i - radius) +
                             (j - radius) * (j - radius))

            # dist should be in the
            # range (radius - 0.5)
            # and (radius + 0.5) to print stars(*)
            # if (dist > radius - 0.5 and dist < radius + 0.5):
            if (dist > radius - 0.5):
                each_row.append("+")
            else:
                each_row.append("w")
        tileMap.append(each_row)

    return tileMap



def circleMapGenerator(radius, verbose = False):
    pattern = ""
    # dist represents distance to the center
    # for horizontal movement
    for i in range((2 * radius) + 1):
        # for vertical movement
        for j in range((2 * radius) + 1):

            dist = math.sqrt((i - radius) * (i - radius) +
                             (j - radius) * (j - radius))

            # dist should be in the
            # range (radius - 0.5)
            # and (radius + 0.5) to print stars(*)
            # if (dist > radius - 0.5 and dist < radius + 0.5):
            if (dist > radius - 0.5):
                pattern += "+ "
                if verbose: print("+", end=" ")
            else:
                pattern += "w "
                if verbose: print("w", end=" ")
        pattern += "\n"
        if verbose: print()

    # write_tile_pattern('circle', 2 * radius + 1, 2 * radius + 1, pattern)
    return pattern


# circleMapGenerator(20)
# circleMapGenerator(10)





