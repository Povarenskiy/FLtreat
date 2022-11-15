import sys, glob, os, shutil
import pandas as pd

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from modules import functions as func
from modules import statusvariable as stv
from modules.paint import Paint


Form,_ = uic.loadUiType("Interface.ui")

class MyProcessClass(QThread):
        stepChanged = pyqtSignal(int)

        def run(self):
            while True:
                self.msleep(100) 
                self.stepChanged.emit(stv.sensor_points)
                

class Ui(QtWidgets.QMainWindow, Form):

    def setup_data(self):
        self.paths = func.set_paths('firecon')
        self.rnd, self.mesh, self.min_height, self.max_height = func.read_rnd_new(self.paths['geometry'])
        self.geom_files = list(self.mesh.keys())
        self.data_fields = func.read_data(self.paths) 
        self.combust = func.find_combust(self.data_fields)
        self.treat_combust = func.treat_combust(self.combust)
       
       
    def setup_buttons(self):
        self.deleteButton.clicked.connect(self.button_deleteClicked)
        self.writeButton.clicked.connect(self.button_writeClicked)
        self.PrnScrButton.clicked.connect(self.button_PrnScrButton)
        self.writeCPButton.clicked.connect(self.button_write_points)
        self.writeAllCPButton.clicked.connect(self.button_write_allpoints)
        self.horizontalSlider.valueChanged.connect(self.change_minO2_slider)
        self.openDirButton.clicked.connect(self.getDirectory)
        self.PrnScrButtonSostav.clicked.connect(self.button_PrnScrButtonSostav)


    def setup_tabs(self):

        width = round(self.width() * 0.5)
        height = round(self.height() * 0.75)

        self.tab_paint = {}
        for file in self.geom_files:            
            tab = QtWidgets.QWidget()
            tab.setFixedWidth(width)
            tab.setFixedHeight(height)
            tab.setObjectName(file)
            self.tabWidget.addTab(tab, file.split('/')[3].split('.')[0])
            self.tab_paint[file] = Paint(tab, self.mesh[file], self.min_height[file], self.max_height[file], tab.width(), tab.height(), file)


    def setup_table(self):
        self.table.setRowCount(0)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["X", "Y", "Z"])


    def setup_work_dir(self):
        self.work_dir = os.getcwd().split('\\')[-1]
        self.comboBox.addItem(self.work_dir)        
        self.task_name = 'firecon'


    def setup_slider_label(self):
        self.label_O2.setText('%1.2f' % (self.horizontalSlider.value()/10) + '%')


    def __init__(self):
        super(Ui, self).__init__()
        
        thread = MyProcessClass()
        thread.stepChanged.connect(self.thread_app)
        thread.start()

        self.setupUi(self)
        self.setup_work_dir()
        self.setup_slider_label()
        self.setup_buttons()
        self.setup_table()
        self.setup_data()
        self.setup_tabs()


    def thread_app(self):
        stv.place_fire_radio_button_checked = self.radioButton.isChecked()
        stv.init_combust_box = self.treat_combust['Box']['filtered']
        self.update_table()
        

    def update_tab(self):
        self.tab_paint[self.geom_files[self.tabWidget.currentIndex()]].update()


    def update_table(self):

        self.table.setRowCount(len(stv.sensor_points))

        if len(stv.sensor_points) > 0:

            element_number = len(stv.sensor_points) - 1

            x, y, z = self.set_coord_to_metre(stv.sensor_points[-1])

            self.table.setItem(element_number, 0, QtWidgets.QTableWidgetItem(x))
            self.table.setItem(element_number, 1, QtWidgets.QTableWidgetItem(y))
            self.table.setItem(element_number, 2, QtWidgets.QTableWidgetItem(z))


    def set_coord_to_metre(self, point):
        
        dx = self.tab_paint[self.geom_files[self.tabWidget.currentIndex()]].dx
        dy = self.tab_paint[self.geom_files[self.tabWidget.currentIndex()]].dy

        x = (point[0] / dx * 0.495) - 22.5
        y = (point[1] / dy * 0.495) - 22.5
        z = point[2]

        x = str(round(x, 2))
        y = str(round(y, 2))
        z = str(round(z, 2))
        
        return x, y, z

    def change_minO2_slider(self):

        O2_min_concentration = self.horizontalSlider.value() / 10
        
        self.label_O2.setText('%1.2f' % (O2_min_concentration) + '%')
        self.treat_combust = func.treat_combust(self.combust, O2_min_concentration / 100)

        
    def add_text(self, text):
        self.textBrowser.append(str(text))


    def button_write_allpoints(self):
        self.add_text(self.combust)


    def button_write_points(self):
        self.add_text(self.treat_combust)


    def button_deleteClicked(self):
        if len(stv.sensor_points):
            stv.sensor_points.pop()
        self.update_tab()
            

    def button_writeClicked(self):

        current_name = self.comboBox.currentText()
        self.task_name = current_name if current_name != 'firecon' else '00000'  
        
        if os.path.exists(self.task_name + '\\') != True:
            shutil.copytree("firecon\\", self.task_name + '\\')

        self.paths = func.set_paths(self.task_name)

        self.write_rnd()
        self.write_sostav()
        self.write_cmp()
        self.write_sensor()
        self.write_combust_param()
        self.textBrowser.clear()

        self.add_text('File creation is complete')


    def button_PrnScrButton(self):      
        path_name = "Photo_sensors"

        if os.path.exists(path_name):
            shutil.rmtree(path_name)

        os.mkdir(path_name)

        self.tabs_for_screen = set([point[4] for point in stv.sensor_points])

        for tab in self.tabs_for_screen:
            file_name = path_name + '/' + tab.split('/')[3].split('.')[0] + '.png'
            self.tab_paint[tab].grab().save(file_name , 'png')
            self.add_text(f'{file_name} create!')


    def write_rnd(self):
        rnd_file = glob.glob(self.paths['geometry'] + "rnd*")
        
        for file in rnd_file:
            with open(file, 'w') as f:
                for row in self.rnd:
                    if row.split()[0] != 'FILEPRN' and row.split()[0] != 'PNTFIRE' and row.split()[0] != 'ENDTEXT':
                        f.write(row)

                x, y, z = self.set_coord_to_metre(stv.init_combust_point_coord)

                pressure = self.treat_combust['p']['filtered']
                pressure = int(pressure)

                f.write('\nFILEPRN SOSTAV_' + self.task_name + '.txt\n')
                f.write(f'PNTFIRE Y={y} X={x} Z={z} P0(Pa)={pressure} T0(K)= 1072 ENDINFO')
                f.write('\nENDTEXT')

            rnd_file_new = self.paths['geometry'] + "rnd_" + self.task_name + '.txt'
            os.rename(file, rnd_file_new)


    def write_sostav(self):

        sostav = {}
        time = self.treat_combust['Time']['filtered']
        
        for field in self.data_fields.keys():
            if field != 'regims':
                sostav[field] = self.data_fields[field].loc[time, 1:].tolist()

        sostav['N'] = [box for box in self.data_fields['H2'].columns if box != 'Time']

        sostav_file = glob.glob(self.paths["geometry"] + 'SOSTAV_*')[0]

        pd.DataFrame(sostav).set_index('N').round(4).to_csv(sostav_file, sep=' ')

        new_sostav_file = f'{self.paths["geometry"]}SOSTAV_{self.task_name}.txt'
        os.rename(sostav_file, new_sostav_file)


    def write_cmp(self):
        cmp_file = glob.glob(self.paths['cmp'] + self.task_name + '.cmp')
        if not cmp_file:
            cmp_file.append(self.paths['cmp'] + self.task_name + '.cmp')
        for file in cmp_file:
            with open(file, 'w') as f:
                f.write('Identification \nuser 2369\npRoBleM ' + self.task_name + '\nvariant 0\ntype (egak_3D)\n0113\nComputer\nprocessor_cart(dim0=1 dim1=1 dim2='+ str(self.spinBoxNt.value()*self.spinBoxNn.value()) + ')\nProcess\nGas(gas_type=pressure)\nTransport(approximation=donor)\nBurning(fire_velocity = -1)\nMonotonization()\n\nCommand\n\npre_init(ni=92 nj=92 nk=176 math_comp=3 phys_comp=3)\n\nfirecon_rnd(rnd_' + self.task_name + '.txt)\n//read(filetype=rec n=Lastrecord)\ninstall(tau= 0.000001)     //!!!\ninstall(tau_max= 0.00005)   //!!! \ngraph(vol_concentration beta ro ro_aver e p_aver e_aver p H2_fire O2_fire N_fire H2O_fire H2_initial O2_initial N_initial H2O_initial temp_fire temp_initial speed_fire uz_aver) \ntrap\ntime++ 0 0.1 1.001 record(compress=yes n=Lastrecord)\nstep++ 1 1 500000 sensor(sensor ' + self.task_name + '_dat.txt ' + self.task_name + '_out)\ntime++ 0 0.1 1.001 graph(vol_concentration beta ro ro_aver e p_aver e_aver p H2_fire O2_fire N_fire H2O_fire H2_initial O2_initial N_initial H2O_initial temp_fire temp_initial speed_fire uz_aver)\ntime= 1.001 endproblem\nendtrap\ncalc')


    def write_sensor(self):
        file_sensor = self.paths['sensors'] + self.task_name + "_dat.txt"
        with open(file_sensor, 'w') as f:
            for N, point in enumerate(stv.sensor_points):
                print_line = str(N) + ' ' + '%1.2f' % (point[0]) + ' ' + '%1.2f' % (point[1]) + ' ' +'%1.2f' % (point[2]) + ' x y z p t endinfo\n'
                f.write(print_line)


    def write_combust_param(self):

        pressure = self.treat_combust['p']['filtered']
        pressure = int(pressure)

        x, y, z = self.set_coord_to_metre(stv.init_combust_point_coord)

        with open("combust_param.txt", 'w') as f:
            f.write(str(self.treat_combust.loc['filtered']))
            f.write('\n')
            f.write(f'PNTFIRE Y={y} X={x} Z={z} P0(Pa)={pressure} T0(K)= 1072 ENDINFO')


    def getDirectory(self):
        p_matrix = {}
        dirlist = QFileDialog.getExistingDirectory(self, "Выбрать папку", ".")
        if len(dirlist) != 0:
            N = len(glob.glob(dirlist + '\\' + "*dat*"))
            files = []
            for n in range(N):
                files += glob.glob(dirlist +'\\'+ "*_dat" + str(n) + '.txt')

            for file in files:
                with open(file) as f:
                    name = next(f)
                    data = []
                    data_time = []
                    check = 0
                    for row in f:
                        for x,param in zip(row.split(),name.split()):
                            if param == 'p':
                                data.append(x)
                            if param == 'time' and check == 0:
                                data_time.append(x)
                    if check == 0:
                        p_matrix['time'] = data_time
                        check = 1
                    if data!=[]:
                        p_matrix[file.split('dat')[1].split('.')[0]] = data

            allsensors_file = dirlist + '\\allsensors.txt'

            with open(allsensors_file, 'w') as f:
                for i in p_matrix.keys():
                    f.write('s_'+ i + ' ')
                for i in range(len(p_matrix['time'])):
                    f.write('\n')
                    for j in p_matrix.keys():
                        f.write(p_matrix[str(j)][i] + ' ')


    def button_PrnScrButtonSostav(self):
        self.add_text('Not include yet')
    #     self.plane_paint = {}
    #     k = 0

    #     path_name = "Photo_fields"

    #     if os.path.exists(path_name) != True:
    #         os.mkdir(path_name)
    #     else:
    #         shutil.rmtree(path_name)
    #         os.mkdir(path_name)

    #     plane_list = ['X', 'Y', 'Z']
    #     for N_coord, plane in enumerate(plane_list):
    #         for param in 'H2', 'O2', 'v':
    #             tab = QtWidgets.QWidget()
    #             name = plane + '.' + param

    #             if plane != 'Z':
    #                 size_horizont = self.width() / 2.9
    #                 size_wertical = self.height() * 0.75
    #             else:
    #                 size_horizont = self.width() / 2
    #                 size_wertical = self.height() * 0.65
    #             tab.setFixedWidth(round(size_horizont))
    #             tab.setFixedHeight(round(size_wertical))
    #             self.tabWidget.insertTab(k, tab, name)

    #             self.plane_paint[plane] = paint_plane(tab, tab.width(), tab.height(), self.mesh, self.geom_files,
    #                                                   self.min_height, self.max_height, self.printFire, N_coord, plane,
    #                                                   param, self.sostav[param])

    #             self.plane_paint[plane].grab().save(path_name + '\\' + name + '.png', 'png')
    #             self.add_text(path_name + '/' + name + '.png')

    #             self.tabWidget.removeTab(0)

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())