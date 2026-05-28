# def printMat(data):
#     xlen = len(data[0])
#     for y in range(len(data)):
#         info = ''
#         for x in range(xlen):
#             info += str(data[y][x]) + ' '
#
#         print(info)
s = [1,2,3]

g = " ".join(map(str, s))

print(g)