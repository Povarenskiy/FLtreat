import glob
import re

import pandas as pd
import glob

import threading

def set_paths(task_name):

    paths = {
        'H2': f'limits/C_H2.out',
        'O2': f'limits/C_O2.out',
        'v': f'limits/C_v.out',
        'p': f'limits/p.out',
        't': f'limits/t.out',

        'limits': 'limits\\',
        'regims': f'limits/regims.txt',
        'geometry' : f'{task_name}/razrez_3d/geom/',
        'sensors': f'{task_name}/razrez_3d/sensor/',
        'work': f'{task_name}/work/',
        'cmp': f'{task_name}/razrez_3d/_cmp/',
    }

    return paths


def read_data(paths):

    data_fields = {
        'H2': None,
        'O2': None,
        'v': None,
        'p': None,
        't': None,
        'regims': None,
        }

    thH2 = threading.Thread(target = read_field, args = ('H2', paths['H2'], data_fields))
    thO2 = threading.Thread(target = read_field, args = ('O2', paths['O2'], data_fields))
    thv = threading.Thread(target = read_field, args = ('v', paths['v'], data_fields))
    thp = threading.Thread(target = read_field, args = ('t', paths['t'], data_fields))
    tht = threading.Thread(target = read_field, args = ('p', paths['p'], data_fields))
    thregims = threading.Thread(target = read_field, args = ('regims', paths['regims'], data_fields))

    thH2.start()
    thO2.start()
    thv.start() 
    thp.start()  
    tht.start() 
    thregims.start()

    thH2.join()
    thO2.join()
    thv.join()  
    thp.join()  
    tht.join() 
    thregims.join()
    
    return data_fields


def read_field(field, path, data_fields):
    
        data_fields[field] = pd.read_csv(path, sep='\\s+')
        data_fields[field].set_index('Time', inplace=True)
        data_fields[field].columns = [int(re.split('_{1,}', box)[-1]) for box in data_fields[field].columns]
        print(f'{field} set')
        

def read_rnd_new(path):
    mesh = {}
    min_height = {}
    max_height = {}
    rnd_file = glob.glob(path + "rnd*.txt")
    with open(*rnd_file) as f:
        rnd = []
        for row_f in f:
            if row_f != '\n':
                rnd.append(row_f)
                if row_f.split()[0] == 'FILECOR':
                    name = row_f.split()[1]
                    with open(path + name) as g:
                        data_geom = []
                        for row_g in g:
                            data_geom.append([int(x) for x in row_g.split()])
                    file_name = path + name
                    mesh[file_name] = data_geom
                    min_height[file_name] = row_f.split()[2]
                    max_height[file_name] = row_f.split()[3]
                     
    return rnd, mesh, min_height, max_height


def find_combust(data_fields):

    buffer_list = []
    names_list = data_fields.keys()
    for field in names_list:
        buffer_list.append(data_fields[field][data_fields['regims'] == 1].stack())
    combust = pd.concat(buffer_list, axis=1)
    combust.columns = names_list
    combust.index.names = ['Time', 'Box']
    combust.reset_index(inplace=True)

    return combust

def treat_combust(data, O2_min_concentration=0.049):

    dict = {
        'COMB max H2': {
            'name': 'max',
            'regim': 1,
            'min O2': 0
        },
        'COMB filtered O2': {
            'name': 'filtered',
            'regim': 1,
            'min O2': O2_min_concentration
        },
        'DET max H2': {
            'name': 'max',
            'regim': 3,
            'min O2': 0
        },
        'DET filtered O2': {
            'name': 'filtered',
            'regim': 3,
            'min O2': O2_min_concentration
        }
    }

    list_ = []
    for key, value in dict.items():
        data_set = data[(data['O2'] >= value['min O2']) & (data['regims'] == value['regim'])]
        if not data_set.empty:
            id_max = data_set['H2'].idxmax()
            list_.append(pd.Series(data.iloc[id_max], name=value['name']))
    df = pd.DataFrame(list_)

    return df




























