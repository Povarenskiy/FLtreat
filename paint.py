from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys, glob, os
import shutil, math

import statusvariable as stv

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


class Paint(QtWidgets.QWidget):

    def __init__(self, parent, geom, minH, maxH, width, height, tab_name):
        super(QtWidgets.QWidget, self).__init__(parent)

        self.printFire = [0,0,0]
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
                if self.geom[x][y] == stv.init_combust_box:
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
        for point in (stv.sensor_points):
            if point[4] == self.tab_name:
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
                            if stv.place_fire_radio_button_checked:
                                self.printFire[0],self.printFire[1],self.printFire[2]=X,Y,Z
                                self.mModifiedFP = True
                            else:
                                sensor_number = len(stv.sensor_points) 
                                stv.sensor_points.append([X, Y, Z, sensor_number, self.tab_name])
                                self.mModified = True
        self.update()
