# def printMat(data):
#     xlen = len(data[0])
#     for y in range(len(data)):
#         info = ''
#         for x in range(xlen):
#             info += str(data[y][x]) + ' '
#
#         print(info)

region = [ [(1,2)], [(0,3)]]

region[-1] += [(1,2), (2,4)]

print(region)