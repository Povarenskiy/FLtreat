from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys, glob, os
import shutil, math



Form,_ = uic.loadUiType("Interface.ui")

class paint_plane(QtWidgets.QWidget):

    def __init__(self, parent, width, height, geom, geom_files, minH, maxH, printFire, N_coord, plane, param, sostav):
        super(QtWidgets.QWidget, self).__init__(parent)

        self.palitra = {0: '#0000ff', 1: '#0072ff', 2: '#00e4ff', 3: '#00ffae', 4: '#00ff36',5: '#36ff00', 6: '#aeff00', 7: '#ffe400', 8: '#ff7200', 9: '#ff0000' , 10: '#ff0000'}
        self.sostav = sostav
        self.N_coord = N_coord
        self.printFire = printFire
        self.plane = plane
        self.param = param
        self.minH = minH
        self.maxH = maxH
        self.geom = geom
        self.geom_files = geom_files

        self.setFixedWidth(width)
        self.setFixedHeight(height)
        self.setObjectName(parent.objectName())

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)

        qp.setBrush(QColor('White'))
        qp.drawRect(0, 0, self.width(), self.height())

        if self.plane == 'X':
            self.drawRectangles_X(qp)
        if self.plane == 'Y':
            self.drawRectangles_Y(qp)
        if self.plane == 'Z':
            self.drawRectangles_Z(qp)

        qp.end()

    def getColor(self, value, maxsostav):
        if value!=1:
            color = self.palitra[math.trunc((self.sostav[value]/maxsostav)*10)]
        else:
            color = self.palitra[0]
        return color

    def drawRectangles_X(self, qp):

        hmin = float(self.minH[self.geom_files[0]])
        hmax = float(self.maxH[self.geom_files[-1]])
        param = self.height()/(hmax-hmin)
        Z = self.height()
        Len_X = len(self.geom[self.geom_files[0]])-3

        for x in range(Len_X):
            dx = 45.5 / Len_X
            if x * dx <= self.printFire[self.N_coord] + 22.5   <= (x + 1) * dx:
                N_x = x

        maxsostav = 0
        for file in self.geom_files:
            row = self.geom[file][N_x]
            for colum in row:
                if self.sostav[colum] > maxsostav:
                    maxsostav = self.sostav[colum]

        for file in self.geom_files:
            dz = (float(self.maxH[file]) - float(self.minH[file])) * param
            row = self.geom[file][N_x]
            dy = 45.5 / len(row) * param
            for j,colum in enumerate(row):
                color = self.getColor(colum,maxsostav)
                qp.setPen(QColor(color))
                qp.setBrush(QColor(color))
                qp.drawRect(round(j*dy), round(Z), round(dy), -round(dz))
            Z -= dz


        self.drawprintFire(qp, param, param, dy, hmin)
        self.drawrainbow(qp,0,maxsostav, j, dy)
    def drawRectangles_Y(self, qp):

        hmin = float(self.minH[self.geom_files[0]])
        hmax = float(self.maxH[self.geom_files[-1]])
        param = self.height()/(hmax-hmin)
        Z = self.height()
        Len_Y = len(self.geom[self.geom_files[0]][0])

        for y in range(Len_Y):
            dy = 45.5 / Len_Y
            if y * dy <= self.printFire[self.N_coord] + 22.5 <= (y + 1) * dy:
                N_y = y

        maxsostav = 0

        for file in self.geom_files:
            for colum in self.geom[file]:
                if len(colum) > 1:
                    if self.sostav[colum[N_y]] > maxsostav:
                        maxsostav = self.sostav[colum[N_y]]


        for file in self.geom_files:
            dz = (float(self.maxH[file]) - float(self.minH[file])) * param
            for j,colum in enumerate(self.geom[file]):
                if len(colum)>1:
                    dx = 45.5 / len(colum) * param
                    color = self.getColor(colum[N_y], maxsostav)
                    qp.setPen(QColor(color))
                    qp.setBrush(QColor(color))
                    qp.drawRect(round(j*dx), round(Z), round(dx), -round(dz))
            Z -= dz

        self.drawprintFire(qp,param, param, dx, hmin)
        self.drawrainbow(qp,0,maxsostav, j, dx)
    def drawRectangles_Z(self, qp):

        Z = self.height()

        otstyp_hor = 1/6*Z
        otstyp_ver = 0

        for z,file in enumerate(self.geom_files):
            if float(self.minH[file]) <= self.printFire[self.N_coord] <= float(self.maxH[file]):
                name_z = file

        maxsostav = 0
        for x in range(0, len(self.geom[name_z]) - 3):
            for y in range(0, len(self.geom[name_z][x])):
                if self.sostav[self.geom[name_z][x][y]] > maxsostav:
                    maxsostav = self.sostav[self.geom[name_z][x][y]]

        Len_Y = len(self.geom[name_z][0])
        Len_X = len(self.geom[name_z]) - 3
        dx = (self.height() - otstyp_ver ) / (Len_X)
        dy = (self.width() - otstyp_hor) / (Len_Y)
        for x in range(0, Len_X):
            for y in range(0, Len_Y):
                color = self.getColor(self.geom[name_z][x][y], maxsostav)
                qp.setPen(QColor(color))
                qp.setBrush(QColor(color))
                qp.drawRect(round(dy * y), round(dx * x), round(dy), round(dx))

        param_ver = (self.height() - otstyp_ver ) / 45.5
        param_hor = (self.width() -otstyp_hor) / 45.5
        self.drawprintFire(qp, param_hor, param_ver, dy, 0)
        self.drawrainbow(qp,0, maxsostav, y, dy)

    def drawprintFire(self, qp, param_hor, param_ver, dy, hmin):

        Z = self.height() - (self.printFire[2] - hmin) * param_ver

        if self.N_coord == 0:
            Y = (self.printFire[1] + 22.5) * param_hor
            k = 1.5
        if self.N_coord == 1:
            Y = (self.printFire[0] + 22.5) * param_hor
            k = 1.5
        if self.N_coord == 2:
            Y = (self.printFire[1] + 22.5) * param_hor
            Z = (self.printFire[0] + 22.5) * param_ver
            k = 1

        qp.setPen(QPen(Qt.black, 3, Qt.SolidLine))
        qp.drawLine(round(Y - k * dy), round(Z - k * dy), round(Y + k * dy), round(Z + k * dy))
        qp.drawLine(round(Y - k * dy), round(Z + k * dy), round(Y + k * dy), round(Z - k * dy))
    def drawrainbow(self , qp, sdvig, maxsostav, j , dy):

        Z = self.height() - sdvig
        dz = Z / (len(self.palitra) - 1)
        sostav = 0

        if maxsostav < 0.1:
            round_ = '%1.3f'
        else:
            round_ = '%1.2f'

        spisok = [10,2,10]
        Coeff = spisok[self.N_coord]

        for i in self.palitra:
            color = self.palitra[i]
            qp.setPen(QColor(color))
            qp.setBrush(QColor(color))
            qp.drawRect(round(j * dy) + Coeff, round(Z), 15, -round(dz))
            qp.setFont(QFont('Decorative', 11))
            qp.setPen(QColor('Black'))
            qp.drawText(round(j * dy) + Coeff + 20, round(Z), round_ % sostav)
            sostav += maxsostav / (len(self.palitra) - 1)
            Z -= dz
        qp.drawText(round(j * dy) + Coeff + 20 , round(15), round_ % maxsostav)

class paint(QtWidgets.QWidget):

    def __init__(self, parent, geom, minH, maxH, width, height, tab_name):
        super(QtWidgets.QWidget, self).__init__(parent)

        self.printFire = [0,0,0]
        self.sensor_points = []
        self.palitra = {0:'#ffffff',1:'#000000',2:'#ffffff',3:'#ff0000',4:'#00ff00',5:'#0000ff',6:'#ffff00',7:'#ff00fd',8:'#00ffff',9:'#810000',10:'#008100',11:'#000081',12:'#818100',13:'#810081',14:'#008181',15:'#c1c1c1',16:'#818181',17:'#9a9aff',18:'#9a3066',19:'#ffffcd',20:'#cdffff',21:'#660066',22:'#ff8181',23:'#0066cd',24:'#cdcdff',25:'#000081',26:'#ff00fd',27:'#ffff00',28:'#00ffff',29:'#810081',30:'#810000',31:'#008181',32:'#0000ff',33:'#00cdff',34:'#cdffff',35:'#cdffcd',36:'#ffff9a',37:'#9acdff',38:'#ff9acd',39:'#cf9aff',40:'#ffcd9a',41:'#ff0000',42:'#00ff00',43:'#0000ff',44:'#ffff00',45:'#ff00fd',46:'#00ffff',47:'#810000',48:'#008100',49:'#000081',50:'#818100',51:'#810081',52:'#008181',53:'#c1c1c1',54:'#818181',55:'#9a9aff',56:'#9a3066',57:'#ffffcd',58:'#cdffff',59:'#660066',60:'#ff8181',61:'#0066cd',62:'#cdcdff',63:'#000081',64:'#ff00fd',65:'#ffff00',66:'#00ffff',67:'#810081',68:'#810000',69:'#008181',70:'#0000ff',71:'#00cdff',72:'#cdffff',73:'#cdffcd',74:'#ffff9a',75:'#9acdff',76:'#ff9acd',77:'#cf9aff',78:'#ffcd9a',79:'#2f66ff',80:'#ffffff',81:'#ff0000',82:'#00ff00',83:'#0000ff',84:'#ffff00',85:'#ff00fd',86:'#00ffff',87:'#810000',88:'#008100',89:'#000081',90:'#818100',91:'#810081',92:'#008181',93:'#c1c1c1',94:'#818181',95:'#9a9aff',96:'#9a3066',97:'#ffffcd',98:'#cdffff',99:'#660066',100:'#ff8181',101:'#0066cd',102:'#cdcdff',103:'#000081',104:'#ff00fd',105:'#ffff00',106:'#00ffff',107:'#810081',108:'#810000',109:'#008181',110:'#0000ff',111:'#00cdff',112:'#cdffff',113:'#cdffcd',114:'#ffff9a',115:'#9acdff',116:'#ff9acd',117:'#cf9aff',118:'#ffcd9a',119:'#2f66ff',120:'#ffffff',121:'#ff0000',122:'#00ff00',123:'#0000ff',124:'#ffff00',125:'#ff00fd',126:'#00ffff',127:'#810000',128:'#008100',129:'#000081',130:'#818100',131:'#810081',132:'#008181',133:'#c1c1c1',134:'#818181',135:'#9a9aff',136:'#9a3066',137:'#ffffcd',138:'#cdffff',139:'#660066',140:'#ff8181',141:'#0066cd',142:'#cdcdff',143:'#000081',144:'#ff00fd',145:'#ffff00',146:'#00ffff',147:'#810081',148:'#810000',149:'#008181',150:'#0000ff',151:'#00cdff'}
        self.mModified, self.mModifiedFP = False, False
        self.X, self.Y = 0, 0

        self.tab_name = tab_name
        self.geom = geom
        self.minH = float(minH)
        self.maxH = float(maxH)
        self.width  = width
        self.height = height



        self.setObjectName(parent.objectName())
        self.setGeometry(0, 0, self.width, self.height)
        self.dx = self.height/(len(geom) -3)
        self.dy = self.width/(len(geom[0]))

    def paintEvent(self, e):

        qp = QPainter()
        qp.begin(self)
        self.drawRectangles(qp)
        if self.mModifiedFP == True:
            self.dwarprintFire(qp)
        if self.mModified == True:
            self.drawSensor(qp)
        qp.end()
    def drawRectangles(self, qp):

        for x in range(0, len(self.geom)-3):
            for y in range(0, len(self.geom[x])):
                if self.geom[x][y] == window.fire_box_recommend:
                    qp.setPen(QColor(self.palitra[self.geom[x][y]]))
                    qp.setBrush(Qt.BrushStyle(Qt.Dense4Pattern))
                    qp.drawRect(round(self.dy * y), round(self.dx * x), round(self.dy), round(self.dx))
                else:
                    qp.setPen(QColor(self.palitra[self.geom[x][y]]))
                    qp.setBrush(QColor(self.palitra[self.geom[x][y]]))
                    qp.drawRect(round(self.dy*y), round(self.dx*x), round(self.dy), round(self.dx))
        qp.setPen(QColor('White'))
        qp.setFont(QFont('Decorative', 10))
        qp.drawText(self.width-90, 20,'H=' + '%1.1f' % self.minH + ':' + '%1.1f' % self.maxH + ' m')

    def dwarprintFire(self, qp):
            qp.setPen(QColor('Black'))
            qp.setBrush(QColor('White'))
            X = self.printFire[0]
            Y = self.printFire[1]
            coef = 4
            qp.drawEllipse(round(Y-0.5*coef*self.dy), round(X-0.5*coef*self.dx), round(coef*self.dy), round(coef*self.dx))
            qp.setPen(QPen(Qt.red, 3, Qt.SolidLine))
            qp.drawLine(round(Y-0.9*self.dy), round(X-self.dx), round(Y+1.1*self.dy), round(X+1*self.dx))
            qp.drawLine(round(Y-0.9*self.dy), round(X+self.dx), round(Y+1.1*self.dy), round(X-1*self.dx))
    def drawSensor(self, qp):
        for point in (self.sensor_points):

            X = point[0]
            Y = point[1]
            N = point[3]
            coef = 4
            qp.setPen(QColor('Black'))
            qp.setBrush(QColor('White'))
            qp.drawEllipse(round(Y-0.5*coef*self.dy),round(X-0.5*coef*self.dx), round(coef*self.dy),round(coef*self.dx))
            if N<10:
                coef = 0.5
            else:
                coef = 1.3
            qp.setFont(QFont('Decorative', 11))
            qp.drawText(round(Y-coef*self.dy),round(X+self.dx), str(N) )

    def mousePressEvent(self, event):

        X = event.y()
        Y = event.x()
        Z = (self.maxH+self.minH)/2

        for x in range(1, len(self.geom) - 3):
            if x * self.dx < X < (x+1) * self.dx:
                for y in range(1, len(self.geom[x])):
                    if (y) * self.dy < Y < (y+1) * self.dy:
                        X = x * self.dx + 0.5*self.dx
                        Y = y * self.dy + 0.5*self.dy
                        if self.geom[x][y]!= 1:
                            if window.radioButton.isChecked():
                                self.printFire[0],self.printFire[1],self.printFire[2]=X,Y,Z
                                Ui.update_printfire_from_paint(self)
                                self.mModifiedFP = True
                            else:
                                N = len(window.sensor_points)
                                self.sensor_points.append([X, Y, Z, N, self.tab_name])
                                Ui.update_sensor_from_paint(self)
                                self.mModified = True
        self.update()


class Ui(QtWidgets.QMainWindow, Form):

    def __init__(self):

        super(Ui,self).__init__()
        self.setupUi(self)

        self.sensor_points,self.printFire,self.tabname_for_screen = [],[0,0,0],[]
        self.tab_paint = {}

        self.task_name = 'firecon'
        self.work_dir = os.getcwd().split('\\')[-1]
        self.comboBox.addItem(self.work_dir)

        self.path_geom, self.path_limits, self.path_cmp, self.path_sensor, self.path_work = self.set_path(self.task_name)
        self.rnd, self.geom_files, self.geom_minH, self.geom_maxH = self.read_rnd(self.path_geom)
        self.geom = self.read_geom(self.geom_files)

        self.H2, self.Time, self.O2, self.v, self.p, self.t, self.regims = self.read_limitsfiles(self.path_limits)
        self.combust_i, self.combust_box, self.det_i, self.det_box = self.treat_files(self.regims)
        self.fire_i_max, self.fire_box_max, self.fire_i_recommend, self.fire_box_recommend = self.find_max(self.H2,self.O2,self.combust_i,self.combust_box,self.det_i,self.det_box)
        self.sostav = self.set_sostav(self.fire_i_recommend)

        self.MyTable()
        self.SetTabs(self.geom_files, self.geom, self.geom_minH, self.geom_maxH)
        self.setSlider()

        self.deleteButton.clicked.connect(self.button_deleteClicked)
        self.writeButton.clicked.connect(self.button_writeClicked)
        self.PrnScrButton.clicked.connect(self.button_PrnScrButton)
        self.PrnScrButtonSostav.clicked.connect(self.button_PrnScrButtonSostav)
        self.writeCPButton.clicked.connect(self.button_write_points)
        self.writeAllCPButton.clicked.connect(self.button_write_allpoints)
        self.horizontalSlider.valueChanged.connect(self.updateSlider)
        self.openDirButton.clicked.connect(self.getDirectory)

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

    def setSlider(self):
        self.label_O2.setText('%1.2f' % (self.horizontalSlider.value()/10) + '%')
    def updateSlider(self):
        self.label_O2.setText('%1.2f' % (self.horizontalSlider.value()/10) + '%')
        self.fire_i_max, self.fire_box_max, self.fire_i_recommend, self.fire_box_recommend = self.find_max(self.H2,self.O2,self.combust_i,self.combust_box,self.det_i,self.det_box)
        self.tab_paint[self.geom_files[self.tabWidget.currentIndex()]].update()

    def SetTabs(self, files, geom, minH, maxH):

        for file in files:

            tab = QtWidgets.QWidget()
            tab.setFixedWidth(round(self.width()/2))
            tab.setFixedHeight(round(self.height()*0.75))
            tab.setObjectName(file)
            self.tabWidget.addTab(tab, file.split('\\')[3].split('.')[0])
            self.tab_paint[file] = paint(tab, geom[file], minH[file], maxH[file], tab.width(), tab.height(), file)

    def MyTable(self):
        self.table.setRowCount(0)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["X", "Y", "Z"])


    def setTableWidth(self):
        width = self.table.verticalHeader().width()
        width += self.table.horizontalHeader().length()
        if self.table.verticalScrollBar().isVisible():
            width += self.table.verticalScrollBar().width()
        width += self.table.frameWidth() * 2
        self.table.setFixedWidth(width)
    def setPointsOnTable(self):
        self.table.setRowCount(len(self.sensor_points))
        for i in 0,1,2:
            self.table.setItem(len(self.sensor_points) - 1, i, QtWidgets.QTableWidgetItem('%1.2f' % self.sensor_points[-1][i]))
        self.setTableWidth()

    def setPrintFireCoord(self, X, Y, Z):
        self.printFireX = X
        self.printFireY = Y
        self.printFireZ = Z
        self.radioButton_2.setChecked(True)
        line = '\nPNTFIRE   Y= ' + '%1.2f' % Y + ' X= ' + '%1.2f' % X + ' Z= ' + '%1.2f' % Z + ' P0(Pa)= ' + '%1.0f' % \
               self.p[self.fire_i_recommend][self.fire_box_recommend] + ' T0(K)= 1072 ENDINFO'
        self.add_text(line)

    def set_taskName(self):
        name = self.comboBox.currentText()
        if name == 'firecon':
            name = '00000'
        return name
    def set_path(self, task_name):
        path = task_name
        path_geom = path + '\\razrez_3d\\geom\\'
        path_limits = 'limits\\'
        path_cmp = path + '\\razrez_3d\\_cmp\\'
        path_sensor = path + '\\razrez_3d\\sensor\\'
        path_work = path + '\\work\\'
        return path_geom, path_limits, path_cmp, path_sensor, path_work
    def set_sostav(self,i):
        sostav =  {}
        for param,name in zip( (self.H2[i], self.O2[i], self.v[i], self.t[i], self.p[i]),('H2','O2','v','t','p')):
            data = []
            data.append(name)
            for box in range(1, 151):
                data.append(param[box])
            sostav[name] = data




        return sostav

    def update_sensor_from_paint(self):
        sensor_coord = [0,0,0]
        sensor_coord[0] = (self.sensor_points[-1][0] / self.dx * 0.495) - 22.5
        sensor_coord[1] = (self.sensor_points[-1][1] / self.dy * 0.495) - 22.5
        sensor_coord[2] =  self.sensor_points[-1][2]

        window.tabname_for_screen.append(self.sensor_points[-1][4])
        window.sensor_points.append(sensor_coord)
        window.setPointsOnTable()
        # if self.radioButton.isChecked():
        #     self.setPrintFireCoord(X, Y, Z)
        # else:
    def update_printfire_from_paint(self):
        prinFire_coord = [0, 0, 0]
        prinFire_coord[0] = (self.printFire[0] / self.dx * 0.495) - 22.5
        prinFire_coord[1] = (self.printFire[1] / self.dy * 0.495) - 22.5
        prinFire_coord[2] = self.printFire[2]

        window.printFire = prinFire_coord

        line = '\nPNTFIRE   Y= ' + '%1.2f' % window.printFire[1] + ' X= ' + '%1.2f' % window.printFire[0] + ' Z= ' + '%1.2f' % window.printFire[2] + ' P0(Pa)= ' + '%1.0f' % window.p[window.fire_i_recommend][window.fire_box_recommend] + ' T0(K)= 1072 ENDINFO'
        window.add_text(line)

    def button_write_allpoints(self):
        for i, j in zip(self.combust_i, self.combust_box):
            spisok = self.get_spisok(i, j, self.Time, self.H2, self.O2, self.v, self.p, self.t)
            self.add_text_from_spisok('Combustion', spisok)
        for i, j in zip(self.det_i, self.det_box):
            spisok = self.get_spisok(i, j, self.Time, self.H2, self.O2, self.v, self.p, self.t)
            self.add_text_from_spisok('Detonation', spisok)
    def button_write_points(self):
        self.add_text('BOX   Time           H2         O2           v             p         t')
        for i, j, k in (self.fire_i_max, self.fire_box_max, 'Maximum'), (self.fire_i_recommend, self.fire_box_recommend, 'Filtered'):
            spisok = self.get_spisok(i, j, self.Time, self.H2, self.O2, self.v, self.p, self.t)
            for check in zip(self.det_i,self.det_box):
                if i == check[0] and j == check[1]:
                    k +=' Detonation'
            self.add_text_from_spisok(k, spisok)
    def button_deleteClicked(self):
        if len(self.sensor_points) > 0:
            del self.sensor_points[-1]
            del(self.tab_paint[self.geom_files[self.tabWidget.currentIndex()]].sensor_points[-1])

        if len(self.sensor_points) == 0:
            self.table.removeRow(0);
            self.tab_paint[self.geom_files[self.tabWidget.currentIndex()]].mModified = False
        else:
            self.setPointsOnTable()
        self.tab_paint[self.geom_files[self.tabWidget.currentIndex()]].update()

    def button_writeClicked(self):

        self.task_name = self.set_taskName()
        if os.path.exists(self.task_name + '\\') != True:
            shutil.copytree("firecon\\", self.task_name + '\\')

        self.path_geom, self.path_limits, self.path_cmp, self.path_sensor, self.path_work = self.set_path(self.task_name)

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

                # tab.setObjectName(name)
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





    def get_spisok(self, i, j, Time, H2, O2, v, p, t ):
        line = [j]
        for x in Time, H2, O2, v, p, t:
            if isinstance(x[0], list) == True:
                line.append(x[i][j])
            else:
                line.append(x[i])
        return line
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


    def read_limitsfiles(self, path):

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
        return H2,Time,O2,v,p,t,regims
    def read_geom(self, files_list):
        geom = {}
        for file in files_list:
            with open(file) as f:
                data_geom = []
                for row in f:
                    data_geom.append([int(x) for x in row.split()])
                geom[file] = data_geom
        return geom
    def read_rnd(self, path):
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

    def treat_files(self, regims):
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
        return combust_i,combust_j,det_i,det_j

    def find_max(self, H2, O2, combust_N_dt, combust_box, det_N_dt, det_box):

        H2_min = 0.00
        O2_min = self.horizontalSlider.value()/10/100

        O2_max = 0
        H2_max = H2_min
        H2_recommend = H2_min
        O2_recommend = 0

        i_max, j_max, i_recommend, j_recommend = 0,0,0,0

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


    def write_rnd(self):

        rnd_file = glob.glob(self.path_geom + "rnd*")
        rnd_file_new = self.path_geom + "rnd_" + self.task_name + '.txt'

        for file in rnd_file:
            with open(file, 'w') as f:
                for row in self.rnd:
                    if row.split()[0] != 'FILEPRN' and row.split()[0] != 'PNTFIRE' and row.split()[0] != 'ENDTEXT':
                        f.write(row)
                f.write('\nFILEPRN SOSTAV_' + self.task_name + '.txt')
                f.write('\nPNTFIRE Y= ' + '%1.2f' % self.printFire[1] + ' X= ' + '%1.2f' % self.printFire[0] + ' Z= ' + '%1.2f' % self.printFire[2] + ' P0(Pa)= ' + '%1.0f' % self.p[self.fire_i_recommend][self.fire_box_recommend] + ' T0(K)= 1072 ENDINFO')
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

        # endregion
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
                f.write('\nPNTFIRE Y= ' + '%1.2f' % self.printFire[0] + ' X= ' + '%1.2f' % self.printFire[1] + ' Z= ' + '%1.2f' % self.printFire[2] + ' P0(Pa)= ' + '%1.0f' % self.p[self.fire_i_recommend][self.fire_box_recommend] + ' T0(K)= 1072 ENDINFO')

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())