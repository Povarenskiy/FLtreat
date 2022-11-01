import functions
import statusvariable as stv
import sys, glob, os, shutil

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from paint import Paint


Form,_ = uic.loadUiType("Interface.ui")

class MyProcessClass(QThread):
        stepChanged = pyqtSignal(int)
        
        def __init__(self):
            super().__init__()
            self.data = 0

        def run(self):
            while True:
                self.data += 1
                self.stepChanged.emit(self.data)
                self.msleep(100) 


class Ui(QtWidgets.QMainWindow, Form):

    def setup_data(self):
        self.path_geom, self.path_limits, self.path_cmp, self.path_sensor, self.path_work = functions.set_path(
            self.task_name)
        self.rnd, self.geom_files, self.geom_minH, self.geom_maxH = functions.read_rnd(self.path_geom)
        self.geom = functions.read_geom(self.geom_files)

        self.H2, self.Time, self.O2, self.v, self.p, self.t, self.regims = functions.read_limitsfiles(self.path_limits)
        self.combust_i, self.combust_box, self.det_i, self.det_box = functions.treat_files(self.regims)
        self.fire_i_max, self.fire_box_max, self.fire_i_recommend, self.fire_box_recommend = functions.find_max(self.H2,
                                                                                                                self.O2,
                                                                                                                self.combust_i,
                                                                                                                self.combust_box,
                                                                                                                self.det_i,
                                                                                                                self.det_box)
        self.sostav = self.set_sostav(self.fire_i_recommend)


    def setup_buttons(self):
        self.deleteButton.clicked.connect(self.button_deleteClicked)
        self.writeButton.clicked.connect(self.button_writeClicked)   
        self.PrnScrButton.clicked.connect(self.button_PrnScrButton)
        self.PrnScrButtonSostav.clicked.connect(self.button_PrnScrButtonSostav)
        self.writeCPButton.clicked.connect(self.button_write_points)
        self.writeAllCPButton.clicked.connect(self.button_write_allpoints)
        self.horizontalSlider.valueChanged.connect(self.change_minO2_slider)
        self.openDirButton.clicked.connect(self.getDirectory)


    def setup_tabs(self):

        self.sensor_points = []
        self.tab_paint = {}

        width = round(self.width() * 0.5)
        height = round(self.height() * 0.75)

        for file in self.geom_files:
            tab = QtWidgets.QWidget()
            tab.setFixedWidth(width)
            tab.setFixedHeight(height)
            tab.setObjectName(file)
            self.tabWidget.addTab(tab, file.split('\\')[3].split('.')[0])
            self.tab_paint[file] = Paint(tab, self.geom[file], self.geom_minH[file], self.geom_maxH[file], tab.width(), tab.height(), file)
            self.tab_paint[file].sensor_points = self.sensor_points


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
        stv.init_combust_box = self.fire_box_max
        self.update_table()
        self.update_tab()


    def update_tab(self):
        self.tab_paint[self.geom_files[self.tabWidget.currentIndex()]].update()


    def update_table(self):
        self.table.setRowCount(len(stv.sensor_points))
        if len(stv.sensor_points) > 0:
            for i in 0,1,2:
                self.table.setItem(len(stv.sensor_points) - 1, i, QtWidgets.QTableWidgetItem('%1.2f' % stv.sensor_points[-1][i]))


    def change_minO2_slider(self):
        self.label_O2.setText('%1.2f' % (self.horizontalSlider.value()/10) + '%')
        self.fire_i_max, self.fire_box_max, self.fire_i_recommend, self.fire_box_recommend = functions.find_max(self.H2,self.O2,self.combust_i,self.combust_box,self.det_i,self.det_box)
        

    # def setPrintFireCoord(self, X, Y, Z):
    #     self.printFireX = X
    #     self.printFireY = Y
    #     self.printFireZ = Z
    #     self.radioButton_2.setChecked(True)
    #     line = '\nPNTFIRE   Y= ' + '%1.2f' % Y + ' X= ' + '%1.2f' % X + ' Z= ' + '%1.2f' % Z + ' P0(Pa)= ' + '%1.0f' % \
    #            self.p[self.fire_i_recommend][self.fire_box_recommend] + ' T0(K)= 1072 ENDINFO'
    #     self.add_text(line)


    # def setup_task_name(self):
    #     current_name = self.comboBox.currentText()
    #     self.task_name = current_name if current_name != 'firecon' else '00000'       

        
    def set_sostav(self, i):
        sostav =  {}
        for param,name in zip( (self.H2[i], self.O2[i], self.v[i], self.t[i], self.p[i]),('H2','O2','v','t','p')):
            data = []
            data.append(name)
            for box in range(1, 151):
                data.append(param[box])
            sostav[name] = data
        return sostav

    # def update_sensor_from_paint(self):
    #     sensor_coord = [0,0,0]
    #     sensor_coord[0] = (self.sensor_points[-1][0] / self.dx * 0.495) - 22.5
    #     sensor_coord[1] = (self.sensor_points[-1][1] / self.dy * 0.495) - 22.5
    #     sensor_coord[2] =  self.sensor_points[-1][2]

    #     window.tabname_for_screen.append(self.sensor_points[-1][4])
    #     window.sensor_points.append(sensor_coord)
    #     window.setPointsOnTable()

    # def update_printfire_from_paint(self):
    #     prinFire_coord = [0, 0, 0]
    #     prinFire_coord[0] = (self.printFire[0] / self.dx * 0.495) - 22.5
    #     prinFire_coord[1] = (self.printFire[1] / self.dy * 0.495) - 22.5
    #     prinFire_coord[2] = self.printFire[2]

    #     window.printFire = prinFire_coord

    #     line = '\nPNTFIRE   Y= ' + '%1.2f' % window.printFire[1] + ' X= ' + '%1.2f' % window.printFire[0] + ' Z= ' + '%1.2f' % window.printFire[2] + ' P0(Pa)= ' + '%1.0f' % window.p[window.fire_i_recommend][window.fire_box_recommend] + ' T0(K)= 1072 ENDINFO'
    #     window.add_text(line)

    def button_write_allpoints(self):
        for i, j in zip(self.combust_i, self.combust_box):
            spisok = functions.get_spisok(i, j, self.Time, self.H2, self.O2, self.v, self.p, self.t)
            self.add_text_from_spisok('Combustion', spisok)
        for i, j in zip(self.det_i, self.det_box):
            spisok = functions.get_spisok(i, j, self.Time, self.H2, self.O2, self.v, self.p, self.t)
            self.add_text_from_spisok('Detonation', spisok)


    def button_write_points(self):
        self.add_text('BOX   Time           H2         O2           v             p         t')
        for i, j, k in (self.fire_i_max, self.fire_box_max, 'Maximum'), (self.fire_i_recommend, self.fire_box_recommend, 'Filtered'):
            spisok = functions.get_spisok(i, j, self.Time, self.H2, self.O2, self.v, self.p, self.t)
            for check in zip(self.det_i,self.det_box):
                if i == check[0] and j == check[1]:
                    k +=' Detonation'
            self.add_text_from_spisok(k, spisok)


    def button_deleteClicked(self):
        if len(stv.sensor_points):
            stv.sensor_points.pop()
            

    def button_writeClicked(self):

        new_name = self.comboBox.currentText()
        
        if new_name == 'firecon':
            new_name = '00000'  

        self.task_name = new_name

        if os.path.exists(new_name + '\\') != True:
            shutil.copytree("firecon\\", new_name + '\\')

        self.path_geom, self.path_limits, self.path_cmp, self.path_sensor, self.path_work = functions.set_path(self.task_name)

        self.write_rnd()
        self.write_sostav()
        self.write_cmp()
        self.write_cmd()
        self.write_egak3d()
        self.write_sensor()
        self.write_combust_param()
        self.textBrowser.clear()

        self.add_text('File creation is complete')

    def button_PrnScrButton(self):
        path_name = "Photo_sensors"

        if os.path.exists(path_name) != True:
            os.mkdir(path_name)
        else:
            shutil.rmtree(path_name)
            os.mkdir(path_name)

        self.tabname_for_screen = list(set(self.tabname_for_screen))
        for tab in self.tabname_for_screen:
            self.tab_paint[tab].grab().save(path_name + '\\' + tab.split('\\')[3].split('.')[0] + '.png' , 'png')
            self.add_text(path_name+ '/' + tab.split('\\')[3].split('.')[0] + '.png')

    def button_PrnScrButtonSostav(self):
        self.plane_paint = {}
        k = 0

        path_name = "Photo_fields"

        if os.path.exists(path_name) != True:
            os.mkdir(path_name)
        else:
            shutil.rmtree(path_name)
            os.mkdir(path_name)

        plane_list = ['X', 'Y', 'Z']
        for N_coord, plane in enumerate(plane_list):
            for param in 'H2', 'O2', 'v':
                tab = QtWidgets.QWidget()
                name = plane + '.' + param

                if plane != 'Z':
                    size_horizont = self.width() / 2.9
                    size_wertical = self.height() * 0.75
                else:
                    size_horizont = self.width() / 2
                    size_wertical = self.height() * 0.65
                tab.setFixedWidth(round(size_horizont))
                tab.setFixedHeight(round(size_wertical))
                self.tabWidget.insertTab(k, tab, name)

                self.plane_paint[plane] = paint_plane(tab, tab.width(), tab.height(), self.geom, self.geom_files,
                                                      self.geom_minH, self.geom_maxH, self.printFire, N_coord, plane,
                                                      param, self.sostav[param])

                self.plane_paint[plane].grab().save(path_name + '\\' + name + '.png', 'png')
                self.add_text(path_name + '/' + name + '.png')

                self.tabWidget.removeTab(0)


    def add_text_from_spisok(self, word, spisok):
        data = ''
        for x in spisok:
            if x >= 1:
                data += '%0.0f' % x + '     '
                continue
            data += ' %0.3f' % x + '   '
        data += word
        self.textBrowser.append(data)

    def add_text(self, text):
        self.textBrowser.append(text)

    def write_rnd(self):
        rnd_file = glob.glob(self.path_geom + "rnd*")
        rnd_file_new = self.path_geom + "rnd_" + self.task_name + '.txt'

        for file in rnd_file:
            with open(file, 'w') as f:
                for row in self.rnd:
                    if row.split()[0] != 'FILEPRN' and row.split()[0] != 'PNTFIRE' and row.split()[0] != 'ENDTEXT':
                        f.write(row)
                f.write('\nFILEPRN SOSTAV_' + self.task_name + '.txt')
                f.write('\nPNTFIRE Y= ' + '%1.2f' % stv.init_combust_point_coord[1] + ' X= ' + '%1.2f' % stv.init_combust_point_coord[0] + ' Z= ' + '%1.2f' % stv.init_combust_point_coord[2] + ' P0(Pa)= ' + '%1.0f' % self.p[self.fire_i_recommend][self.fire_box_recommend] + ' T0(K)= 1072 ENDINFO')
                f.write('\nENDTEXT')
            os.rename(file, rnd_file_new)

    def write_sostav(self):
        sostav_file = glob.glob(self.path_geom + "SOSTAV_" + self.task_name + '.txt')
        if not sostav_file:
            sostav_file.append(self.path_geom + "SOSTAV_" + self.task_name + '.txt')
        for file in sostav_file:
            with open(file, 'w') as f:
                f.write('N H2 O2 H2O T(C) P \n')
                for box in range(1, 151):
                    f.write(str(box) + ' ')
                    for param in self.H2[self.fire_i_recommend], self.O2[self.fire_i_recommend], self.v[self.fire_i_recommend],  self.t[self.fire_i_recommend], self.p[self.fire_i_recommend]:
                        f.write('%5.4f' % param[box] + ' ')
                    f.write('\n')

    def write_cmp(self):
        cmp_file = glob.glob(self.path_cmp + self.task_name + '.cmp')
        if not cmp_file:
            cmp_file.append(self.path_cmp + self.task_name + '.cmp')
        for file in cmp_file:
            with open(file, 'w') as f:
                f.write('Identification \nuser 2369\npRoBleM ' + self.task_name + '\nvariant 0\ntype (egak_3D)\n0113\nComputer\nprocessor_cart(dim0=1 dim1=1 dim2='+ str(self.spinBoxNt.value()*self.spinBoxNn.value()) + ')\nProcess\nGas(gas_type=pressure)\nTransport(approximation=donor)\nBurning(fire_velocity = -1)\nMonotonization()\n\nCommand\n\npre_init(ni=92 nj=92 nk=176 math_comp=3 phys_comp=3)\n\nfirecon_rnd(rnd_' + self.task_name + '.txt)\n//read(filetype=rec n=Lastrecord)\ninstall(tau= 0.000001)     //!!!\ninstall(tau_max= 0.00005)   //!!! \ngraph(vol_concentration beta ro ro_aver e p_aver e_aver p H2_fire O2_fire N_fire H2O_fire H2_initial O2_initial N_initial H2O_initial temp_fire temp_initial speed_fire uz_aver) \ntrap\ntime++ 0 0.1 1.001 record(compress=yes n=Lastrecord)\nstep++ 1 1 500000 sensor(sensor ' + self.task_name + '_dat.txt ' + self.task_name + '_out)\ntime++ 0 0.1 1.001 graph(vol_concentration beta ro ro_aver e p_aver e_aver p H2_fire O2_fire N_fire H2O_fire H2_initial O2_initial N_initial H2O_initial temp_fire temp_initial speed_fire uz_aver)\ntime= 1.001 endproblem\nendtrap\ncalc')

    def write_cmd(self):
        cmd_file = glob.glob(self.path_work + self.task_name + '.cmd')
        if not cmd_file:
            cmd_file.append(self.path_work + self.task_name + '.cmd')
        for file in cmd_file:
            with open(file, 'w') as f:
                f.write(
                    '#!/bin/sh \n#SBATCH -U "dep 816, user kuhtevich, theme 00000.000, prog FIRECON, task ' + self.task_name + ', cust SAEP, tel 28774, class 99" \n#SBATCH -N '+ str(self.spinBoxNn.value())  +' -n '+ str(self.spinBoxNn.value()*self.spinBoxNt.value()) +' --ntasks-per-node=' + str(self.spinBoxNt.value()) + ' --nice=0  -p BATCH -t 300:00:00 -o go_' + self.task_name + '.o%j -e go_' + self.task_name + '.e%j	\nexport MPIRUN_USE_TREES=1	\nexport MPIRUN_USE_GATHER_TREE=1 \nexport MPIRUN_USE_BCAST_TREE=1 \nexport VIADEV_USE_SHMEM_COLL=0 \n/opt/slurm/bin/srun --mpi=mvapich ./EGAK_3 ' + self.task_name)


    def write_egak3d(self):
        egak_file = glob.glob(self.path_work + 'egak3d.ini')
        if not egak_file:
            egak_file.append(self.path_work + 'egak3d.ini')
        for file in egak_file:
            with open(file, 'w') as f:
                f.write(
                    'computer\nmp100\nos\nlinux\nmemory\n1200\ninstruction\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/_cmp/\nout\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/_out/\nsystem_dll\n/seg3/saep/kuhtevich/hanh/vab/dab/' + self.task_name + '/razrez_3d/dlls/system_dlls\nprocess_dll\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/dlls/process_dlls\ncommand_dll\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/dlls/command_dlls\nmedium_dll\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/dlls/medium_dlls\nnonstandart_dll\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/dlls/nonstandart_dlls\ntest_dll\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/dlls/test_dlls\nmgd_2d\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/dlls/test_dlls\nbound_table\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/bound_table/\nrecord\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/record/\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/record1/\ntimetable\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/timetable/\ngraph_rezult\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/_graph/\ncontroll\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/controll/\nmirror\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/mirror/\nshadow\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/shadow/\ninf\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/inf/\nprotocol\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/protocol/\nlook2\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/look2/\nstandart_rebrov\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/standart_rebrov/\ngd\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/gd/\ncommon\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/common/\nprocessing\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/processing/\ninf_processing\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/inf_processing/\nefr\n/seg3/saep/kuhtevich/hanh/vab/' + self.task_name + '/razrez_3d/_efr/')

    def write_sensor(self):

        file_sensor = glob.glob(self.path_sensor + self.task_name + "_dat.txt")

        if not file_sensor:
            file_sensor.append(self.path_sensor + self.task_name + "_dat.txt")
        for file in file_sensor:
            with open(file, 'w') as f:
                for N,point in enumerate(self.sensor_points):
                    print_line = str(N) + ' ' + '%1.2f' % (point[0]) + ' ' + '%1.2f' % (point[1]) + ' ' +'%1.2f' % (point[2]) + ' x y z p t endinfo\n'
                    f.write(print_line)

    def write_combust_param(self):

        file = glob.glob("combust_param.txt")

        if not file:
            file.append("combust_param.txt")
        for file in file:
            with open(file, 'w') as f:
                f.write('BOX  Time     H2    O2     v      p        t \n')
                f.write('%1.0f' % self.fire_box_recommend + '   ')
                f.write('%1.0f' % self.Time[self.fire_i_recommend] + '  ')
                for i in self.H2,self.O2,self.v,self.p,self.t:
                    f.write('%1.3f' % i[self.fire_i_recommend][self.fire_box_recommend] + ' ')
                f.write('\nPNTFIRE Y= ' + '%1.2f' % stv.init_combust_point_coord[0] + ' X= ' + '%1.2f' % stv.init_combust_point_coord[1] + ' Z= ' + '%1.2f' % stv.init_combust_point_coord[2] + ' P0(Pa)= ' + '%1.0f' % self.p[self.fire_i_recommend][self.fire_box_recommend] + ' T0(K)= 1072 ENDINFO')


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

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())