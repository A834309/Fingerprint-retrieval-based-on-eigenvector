import numpy as np
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed
from operator import itemgetter
from multiprocessing import Process
import xlwt
import math


# 定义细节点类
class detail_point:
    def __init__(self, x=0, y=0, theta=0, d=0):
        self.x = x
        self.y = y
        self.theta = theta
        self.d = d


# 定义指纹类
class Fingerprint:
    def __init__(self, fgprint_name, point_list=[]):
        self.fgprint_name = fgprint_name
        self.point_list = sorted(point_list, key=lambda x: [x.x, x.y])




# 数据读取函数
def data_former(path):
    f = open(path, 'r')  # 读取文件
    lines = f.read().splitlines()  # 读取各行
    line_count = len(lines)  # 行数
    dataset = [Fingerprint('', []) for p in range(line_count)]  # 初始化对象数组
    i = 0
    for line in lines:
        elements = line.split(',')
        dataset[i].fgprint_name = elements[0]
        del (elements[-1])
        del (elements[0])
        count = len(elements)
        points = [detail_point() for p in range(int(count / 3))]  # 初始化对象数组
        for j in range(0, int(count / 3)):
            points[j].x = int(elements[3 * j])
            points[j].y = int(elements[3 * j + 1])
            points[j].theta = int(elements[3 * j + 2])
        dataset[i].point_list = points.copy()
        i = i + 1

    return dataset


def distance(point1, point2):  # 距离
    return math.sqrt((point1.x - point2.x) * (point1.x - point2.x) + (point1.y - point2.y) * (point1.y - point2.y))


def direction_difference(point1, point2):  # 角度差值
    return point1.theta - point2.theta


def get_neighbor_point(fingerprint, center_point, R):
    neighbor_list = [detail_point() for length in range(0, len(fingerprint.point_list))]
    i = 0
    for neighbor_point in fingerprint.point_list:
        d = int(distance(neighbor_point, center_point))
        if d >= R:
            neighbor_point.d = d
            neighbor_list[i] = neighbor_point
            i = i + 1
    sorted(neighbor_list, key=lambda x: x.d, reverse=True)
    return neighbor_list[0: 5]


def get_eigen_vector(fingerprint, R):  # 获取特征向量组
    eigen_list = [[[0 for col in range(0, 3)] for row in range(0, 5)] for num in
                  range(0, 10)]
    j = 0
    # print(eigen_list)
    for center_point in fingerprint.point_list[0:10]:
        i = 0
        neighbor_points = get_neighbor_point(fingerprint, center_point, R)
        for neighbor_point in neighbor_points:
            d = int(distance(center_point, neighbor_point))  # 距离
            alpha = math.atan2(neighbor_point.x - center_point.x, neighbor_point.y - center_point.y)
            if neighbor_point.y > center_point.y:
                alpha = int(-1 * alpha * 180 / math.pi)
            else:
                alpha = int(alpha * 180 / math.pi)  # 连线夹角

            delta_theta = direction_difference(center_point, neighbor_point)  # 细节点角度差
            eigen_list[j][i][:] = d, alpha, delta_theta
            i = i + 1
        j = j + 1
    # print(eigen_list)
    return eigen_list


def get_similarity_count(eigen_vectors_1, eigen_vectors_2):
    count = 0
    # 找出相似程度高的特征向量并计数
    for eigen_vector_1 in eigen_vectors_1:
        for eigen_vector_2 in eigen_vectors_2:
            delta = np.array(eigen_vector_1) - np.array(eigen_vector_2)  # 两特征向量差
            # print(np.maximum(delta,-1*delta))
            base = np.maximum(np.array(eigen_vector_1), -1 * np.array(eigen_vector_1))  # 原特征向量绝对值
            # print(base)
            # tar = np.allclose(eigen_vector_1, eigen_vector_2, rtol=0.2)
            # if tar == 1:
            if (np.maximum(delta, -1 * delta) < 0.5 * base).all():
                count = count + 1
                break
    # print(count)
    return count


def evaluate(fingerprint1, fingerprint2, R):
    # similarity = [[0 for f in range(0, len(fingerprint2.point_list))] for g in range(0, len(fingerprint1.point_list))]
    similarity = 0
    eigen_list1 = get_eigen_vector(fingerprint1, R)
    eigen_list2 = get_eigen_vector(fingerprint2, R)

    for eigen_vetcors_1 in eigen_list1:
        for eigen_vectors_2 in eigen_list2:
            count = get_similarity_count(eigen_vetcors_1, eigen_vectors_2)
            if count > 2:
                similarity = similarity + 1
                break
    # print(similarity)
    return similarity


def screening(dataset1, dataset2, R, process=0):
    rows = int(len(dataset1))
    cols = int(len(dataset2))
    likelyhood_mat = np.zeros((rows, cols))
    m = 0
    for fp1 in dataset1:
        n = 0
        for fp2 in dataset2:
            likelyhood_mat[m][n] = evaluate(fp1, fp2, R)
            n = n + 1
        m = m + 1
    print(likelyhood_mat)
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("sheet")
    for j in range(1, rows + 1):
        sheet.write(j, 0, dataset1[j-1].fgprint_name)
    for i in range(1, cols + 1):
        sheet.write(0, i, dataset2[i-1].fgprint_name)
    for k in range(1, rows+1):
        for l in range(1, cols+1):
            sheet.write(k, l, likelyhood_mat[k-1][l-1])
    workbook.save('result'+'.xlsx')


if __name__ == '__main__':
    path1 = 'TZ_同指200_乱序后_Data.txt'
    path2 = 'TZ_异指.txt'
    dataset1 = data_former(path1)
    dataset2 = data_former(path2)
    # total = dataset1
    # length = len(total)
    # n = 20  # 切分成多少份
    # step = int(length / n)  # 每份的长度
    # dataset = [[Fingerprint('', []) for p in range(0, step)]for q in range(0, n+1)]
    #
    # for i in range(0, length, step-1):
    #     j = 0
    #     dataset[j] = total[i: i + step]
    #     j = j + 1
    #
    # process_list = []
    # for i in range(0, n+1):  # 开启20个子进程
    #     p = Process(target=screening, args=(dataset[i], dataset2, 100, i))  # 实例化进程对象
    #     p.start()
    #     process_list.append(p)
    screening(dataset1, dataset2, 100)
