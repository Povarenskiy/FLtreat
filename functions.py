import glob


def set_path(task_name):
    path = task_name
    path_geom = path + '\\razrez_3d\\geom\\'
    path_limits = 'limits\\'
    path_cmp = path + '\\razrez_3d\\_cmp\\'
    path_sensor = path + '\\razrez_3d\\sensor\\'
    path_work = path + '\\work\\'
    return path_geom, path_limits, path_cmp, path_sensor, path_work

def read_limitsfiles(path):
    H2 = []
    O2 = []
    v = []
    p = []
    t = []
    regims = []
    Time = []

    files = glob.glob(path + "*.out*") + glob.glob(path + "regims.txt")
    for file in files:
        with open(file) as f:
            data = []
            next(f)
            for row in f:
                data.append([float(x) for x in row.split()])
            if file == path + 'C_H2.out':
                H2 = data
                Time = [row[0] for row in data]
            if file == path + 'C_O2.out':
                O2 = data
            if file == path + 'C_v.out':
                v = data
            if file == path + 'p.out':
                p = data
            if file == path + 't.out':
                t = data
            if file == path + 'regims.txt':
                regims = data
    return H2, Time, O2, v, p, t, regims


def read_geom(files_list):
    geom = {}
    for file in files_list:
        with open(file) as f:
            data_geom = []
            for row in f:
                data_geom.append([int(x) for x in row.split()])
            geom[file] = data_geom
    return geom


def read_rnd(path):
    rnd_file = glob.glob(path + "rnd*.txt")
    for file in rnd_file:
        rnd = []
        geom_files = []
        geom_minH = {}
        geom_maxH = {}
        with open(file) as f:
            for row in f:
                if row != '\n':
                    rnd.append(row)
                    if row.split()[0] == 'FILECOR':
                        geom_files.append(path + row.split()[1])
                        geom_minH[path + row.split()[1]] = row.split()[2]
                        geom_maxH[path + row.split()[1]] = row.split()[3]
    return rnd, geom_files, geom_minH, geom_maxH


def treat_files(regims):
    combust_i = []
    combust_j = []
    det_i = []
    det_j = []
    for i, row in enumerate(regims):
        for j, x in enumerate(row):
            if x == 1:
                combust_i.append(i)
                combust_j.append(j)
            if x == 3:
                det_i.append(i)
                det_j.append(j)
    return combust_i, combust_j, det_i, det_j


def find_max(H2, O2, combust_N_dt, combust_box, det_N_dt, det_box):
    H2_min = 0.00
    # O2_min = self.horizontalSlider.value() / 10 / 100
    O2_min = 0.05
    O2_max = 0
    H2_max = H2_min
    H2_recommend = H2_min
    O2_recommend = 0

    i_max, j_max, i_recommend, j_recommend = 0, 0, 0, 0

    off_box_list = []

    for i, j in zip(combust_N_dt, combust_box):
        if j not in off_box_list:
            if H2[i][j] == H2_max:
                if O2[i][j] >= O2_max:
                    H2_max = H2[i][j]
                    O2_max = O2[i][j]
                    i_max = i
                    j_max = j
            if H2[i][j] > H2_max:
                H2_max = H2[i][j]
                O2_max = O2[i][j]
                i_max = i
                j_max = j
            if H2[i][j] > H2_recommend and O2[i][j] > O2_min:
                H2_recommend = H2[i][j]
                O2_recommend = O2[i][j]
                i_recommend = i
                j_recommend = j
            if H2[i][j] == H2_recommend and O2[i][j] > O2_min:
                if O2[i][j] >= O2_recommend:
                    H2_recommend = H2[i][j]
                    O2_recommend = O2[i][j]
                    i_recommend = i
                    j_recommend = j

    for i, j in zip(det_N_dt, det_box):
        if j not in off_box_list:
            if H2[i][j] == H2_max:
                if O2[i][j] >= O2_max:
                    H2_max = H2[i][j]
                    O2_max = O2[i][j]
                    i_max = i
                    j_max = j
            if H2[i][j] > H2_max:
                H2_max = H2[i][j]
                O2_max = O2[i][j]
                i_max = i
                j_max = j
            if H2[i][j] > H2_recommend and O2[i][j] > O2_min:
                H2_recommend = H2[i][j]
                O2_recommend = O2[i][j]
                i_recommend = i
                j_recommend = j
            if H2[i][j] == H2_recommend and O2[i][j] > O2_min:
                if O2[i][j] >= O2_recommend:
                    H2_recommend = H2[i][j]
                    O2_recommend = O2[i][j]
                    i_recommend = i
                    j_recommend = j
    return i_max, j_max, i_recommend, j_recommend

def get_spisok(i, j, Time, H2, O2, v, p, t):
    line = [j]
    for x in Time, H2, O2, v, p, t:
        if isinstance(x[0], list) == True:
            line.append(x[i][j])
        else:
            line.append(x[i])
    return line
