# To package into app - in cmd:
# pyinstall QCReader.py -n QCReader --windowed --onefile --icon=dropsicon.ico

import sys, os, csv, statistics
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QPushButton, QLabel, QGridLayout, QComboBox,
                             QLineEdit, QFileDialog, QTableWidget, QFrame)
import matplotlib.pyplot as plt
import hyproicons


class qcReaderMain(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'QC Table Stat Maker'

        self.setWindowIcon(QtGui.QIcon(':/assets/2dropsshadow.svg'))

        self.left = 400
        self.top = 400
        self.width = 800
        self.height = 300

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.qcfile = []
        self.existinganalytes = []
        self.runos = []
        self.sampleids = []
        self.datetypes = []
        self.procvalues = []

        self.initUI()

        self.setStyleSheet("""

            QListWidget{

            }
            QLabel {
                font: 13px;
            }
            QListWidget {
                font: 13px;
            }
            QPushButton {
                font: 14px;
            }
            QLineEdit {
                font:14px;
            } 
            QComboBox {
                font: 13px;
            }

                            """)

    def initUI(self):

        deffont = QFont('Segoe UI')
        self.setFont(deffont)
        self.setGeometry(self.left, self.top, self.width, self.height)
        qtRectangle = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.setWindowTitle(self.title)

        gridlayout = QGridLayout()
        gridlayout.setSpacing(5)

        self.headerlabel = QLabel('Select a QC Table file produced/exported by HyPro, not the QC summary!', self)

        self.filepathline = QLineEdit('', self)
        self.filepathline.setReadOnly(True)

        self.browsebutton = QPushButton('Browse...', self)
        self.browsebutton.setFont(deffont)
        self.browsebutton.clicked.connect(self.browsepath)

        self.nutrientlabel = QLabel('Select Nutrient:', self)
        self.nutrientlabel.setFont(deffont)

        self.nutrientdropdown = QComboBox(self)
        self.nutrientdropdown.setFont(deffont)
        self.nutrientdropdown.activated.connect(self.populatedatatypes)

        self.datatypelabel = QLabel('Select data to look at:')
        self.datatypelabel.setFont(deffont)

        self.datatypedropdown = QComboBox(self)
        self.datatypedropdown.setFont(deffont)

        self.loadstats = QPushButton('Load Stats', self)
        self.loadstats.setFont(deffont)
        self.loadstats.clicked.connect(self.loadstatsmethod)

        self.saveall = QPushButton('Save data', self)
        self.saveall.setFont(deffont)
        self.saveall.clicked.connect(self.saveallmethod)

        self.loadplot = QPushButton('Load Plot', self)
        self.loadplot.setFont(deffont)
        self.loadplot.clicked.connect(self.loadplotmethod)

        self.loadtable = QPushButton('Load Table', self)
        self.loadtable.setFont(deffont)
        self.loadtable.clicked.connect(self.loadtablemethod)

        self.minvallabel = QLabel('Minimum:', self)
        self.minvallabel.setFont(deffont)

        self.minval = QLineEdit('', self)
        self.minval.setFont(deffont)
        self.minval.setReadOnly(True)

        self.maxvallabel = QLabel('Maximum:', self)
        self.maxvallabel.setFont(deffont)

        self.maxval = QLineEdit('', self)
        self.maxval.setFont(deffont)
        self.maxval.setReadOnly(True)

        self.meanlabel = QLabel('Average:', self)
        self.meanlabel.setFont(deffont)

        self.meanval = QLineEdit('', self)
        self.meanval.setFont(deffont)
        self.meanval.setReadOnly(True)

        self.medianlabel = QLabel('Median:', self)
        self.medianlabel.setFont(deffont)

        self.medianval = QLineEdit('', self)
        self.medianval.setFont(deffont)
        self.medianval.setReadOnly(True)

        self.stdevlabel = QLabel('Overall Standard Dev:', self)
        self.stdevlabel.setFont(deffont)

        self.stdevval = QLineEdit('', self)
        self.stdevval.setFont(deffont)
        self.stdevval.setReadOnly(True)

        self.intrastdevlabel = QLabel('Inter-run Standard Dev Mean:', self)
        self.stdevlabel.setFont(deffont)

        self.minstdevlabel = QLabel('Min Stdev:', self)
        self.minstdevlabel.setFont(deffont)

        self.minstdev = QLineEdit('', self)
        self.minstdev.setFont(deffont)
        self.minstdev.setReadOnly(True)

        self.maxstdevlabel = QLabel('Max Stdev:', self)
        self.maxstdevlabel.setFont(deffont)

        self.maxstdev = QLineEdit('', self)
        self.maxstdev.setFont(deffont)
        self.maxstdev.setReadOnly(True)

        self.meanstdevlabel = QLabel('Mean Stdev:', self)
        self.meanstdevlabel.setFont(deffont)

        self.meanstdev = QLineEdit('', self)
        self.meanstdev.setFont(deffont)
        self.meanstdev.setReadOnly(True)

        self.medianstdevlabel = QLabel('Median Stdev:', self)
        self.medianstdevlabel.setFont(deffont)

        self.medianstdev = QLineEdit('', self)
        self.medianstdev.setFont(deffont)
        self.medianstdev.setReadOnly(True)

        self.intrastdevval = QLineEdit('', self)
        self.intrastdevval.setFont(deffont)

        linesep1 = QFrame()
        linesep1.setFrameShape(QFrame.HLine)
        linesep1.setFrameShadow(QFrame.Sunken)

        linesep2 = QFrame()
        linesep2.setFrameShape(QFrame.HLine)
        linesep2.setFrameShadow(QFrame.Sunken)

        gridlayout.addWidget(self.headerlabel, 0, 0, 1, 3)
        gridlayout.addWidget(self.filepathline, 1, 0, 1, 4)
        gridlayout.addWidget(self.browsebutton, 1, 4, 1, 1)
        gridlayout.addWidget(self.nutrientlabel, 3, 0)
        gridlayout.addWidget(self.nutrientdropdown, 3, 1)
        gridlayout.addWidget(self.loadstats, 3, 4, 1, 1)
        gridlayout.addWidget(self.saveall, 12, 3, 1, 1)
        gridlayout.addWidget(self.loadplot, 12, 1, 1, 1)
        gridlayout.addWidget(self.loadtable, 12, 2, 1, 1)

        gridlayout.addWidget(self.datatypelabel, 3, 2)
        gridlayout.addWidget(self.datatypedropdown, 3, 3)

        gridlayout.addWidget(self.minvallabel, 6, 0)
        gridlayout.addWidget(self.minval, 7, 0)

        gridlayout.addWidget(self.maxvallabel, 6, 1)
        gridlayout.addWidget(self.maxval, 7, 1)

        gridlayout.addWidget(self.medianlabel, 6, 2)
        gridlayout.addWidget(self.medianval, 7, 2)

        gridlayout.addWidget(self.meanlabel, 6, 3)
        gridlayout.addWidget(self.meanval, 7, 3)

        gridlayout.addWidget(self.stdevlabel, 6, 4)
        gridlayout.addWidget(self.stdevval, 7, 4)

        gridlayout.addWidget(self.intrastdevlabel, 8, 4)
        gridlayout.addWidget(self.intrastdevval, 9, 4)

        gridlayout.addWidget(self.minstdevlabel, 8, 0)
        gridlayout.addWidget(self.minstdev, 9, 0)

        gridlayout.addWidget(self.maxstdevlabel, 8, 1)
        gridlayout.addWidget(self.maxstdev, 9, 1)

        gridlayout.addWidget(self.meanstdevlabel, 8, 3)
        gridlayout.addWidget(self.meanstdev, 9, 3)

        gridlayout.addWidget(self.medianstdevlabel, 8, 2)
        gridlayout.addWidget(self.medianstdev, 9, 2)

        gridlayout.addWidget(linesep1, 2, 0, 1, 6)

        gridlayout.addWidget(linesep2, 11, 0, 1, 6)

        self.centralWidget().setLayout(gridlayout)

        self.show()

    def browsepath(self):
        path = QFileDialog.Options()
        file = QFileDialog.getOpenFileName(self, 'Select file')

        if os.path.exists(file[0]):
            self.filepathline.setText(file[0])
            filebuffer = open(file[0])
            readbuffer = csv.reader(filebuffer, delimiter=',')
            self.qcfile = list(readbuffer)
            filebuffer.close()
            self.splitcolumns(self.qcfile)
            self.nutrientdropdown.addItems(self.existinganalytes)

    def splitcolumns(self, file):
        runnoindex = file[0].index('Run no.')
        self.runnos = [row[runnoindex] for row in file]
        sampleidindex = file[0].index('Sample ID')
        self.sampleids = [row[sampleidindex] for row in file]
        datatypeindex = file[0].index('Data type')
        self.datatypes = [row[datatypeindex] for row in file]
        procvalueindex = file[0].index('Proc Value')
        self.procvalues = [row[procvalueindex] for row in file]
        analytelist = ['Silicate', 'Phosphate', 'NOx', 'Nitrite', 'Ammonia']
        existingana = []

        for i in analytelist:
            if i in self.datatypes:
                existingana.append(i)

        self.existinganalytes = existingana

    def populatedatatypes(self):
        nutrient = self.nutrientdropdown.currentText()
        selectedindexes = [k for k, i in enumerate(self.datatypes) if i == nutrient]
        selectedsampleids = [self.sampleids[v] for v in selectedindexes]
        nametypes1 = [k for k in selectedsampleids if k.isdigit() == False]
        nametypes2 = []
        self.datatypedropdown.clear()
        for i in nametypes1:
            if i[0:4] == 'RMNS':
                nametypes2.append(i[0:7])
            else:
                nametypes2.append(i)
        distillednametypes = set(nametypes2)
        nametypesinlist = distillednametypes
        sortednametypes = sorted(nametypesinlist)
        self.datatypedropdown.addItems(sortednametypes)

    def loadstatsmethod(self):

        try:
            nuttouse = self.nutrientdropdown.currentText()
            datatypetouse = self.datatypedropdown.currentText()
            selectedindexes = [k for k, i in enumerate(self.datatypes) if i == nuttouse]
            nutrientdatatypes = [self.sampleids[k] for k in selectedindexes]
            nutrientprocvals = [self.procvalues[k] for k in selectedindexes]
            nutrientrunnos = [self.runnos[k] for k in selectedindexes]
            selecteddatatypeindexes = [k for k, i in enumerate(nutrientdatatypes) if i[0:7] == datatypetouse[0:7]]
            selectednutrientprocvals = [float(nutrientprocvals[k]) for k in selecteddatatypeindexes]
            selectednutrientrunnos = [nutrientrunnos[k] for k in selecteddatatypeindexes]
            mean = (sum(selectednutrientprocvals) / len(selectednutrientprocvals))
            roundedmean = round(mean, 3)
            self.meanval.setText(str(roundedmean))

            sortedprocvals = sorted(selectednutrientprocvals)
            middleindex = ((len(sortedprocvals)) - 1) // 2
            if len(sortedprocvals) % 2:
                median = sortedprocvals[middleindex]
            else:
                median = (sortedprocvals[middleindex] + sortedprocvals[middleindex + 1]) / 2
            roundedmedian = round(median, 3)
            self.medianval.setText(str(roundedmedian))

            maxnum = max(selectednutrientprocvals)
            self.maxval.setText(str(maxnum))

            minnum = min(selectednutrientprocvals)
            self.minval.setText(str(minnum))

            runnoset = set(nutrientrunnos)
            stdevbuffer = []
            stdevbuffer2 = []
            stdevlist = []
            intrastdevlist = []

            for i in runnoset:
                stdevcounter = 0
                for k in range(len(selectednutrientrunnos)):
                    if i == selectednutrientrunnos[k]:
                        stdevbuffer.append(selectednutrientprocvals[k])
                        stdevbuffer2.append(selectednutrientprocvals[k])
                        stdevcounter = stdevcounter + 1
                if stdevcounter > 1:
                    intrastdev = statistics.stdev(stdevbuffer2)
                    intrastdevlist.append(intrastdev)
                    stdevbuffer2 = []

            maxstdev = round(max(intrastdevlist), 3)
            minstdev = round(min(intrastdevlist), 3)
            meanstdev = round(statistics.mean(intrastdevlist), 3)
            medianstdev = round(statistics.median(intrastdevlist), 3)

            self.minstdev.setText(str(minstdev))
            self.maxstdev.setText(str(maxstdev))
            self.meanstdev.setText(str(meanstdev))
            self.medianstdev.setText(str(medianstdev))

            intrastdevmeans = statistics.mean(intrastdevlist)
            stdevlist.append(statistics.stdev(stdevbuffer))
            stdevbuffer = []

            stdevmean = (sum(stdevlist) / len(stdevlist))
            roundedstdevmean = round(stdevmean, 3)
            self.stdevval.setText(str(roundedstdevmean))

            roundintrastdev = round(intrastdevmeans, 3)
            self.intrastdevval.setText(str(roundintrastdev))
        except Exception as e:
            print(e)

    def loadtablemethod(self):
        try:
            nuttouse = self.nutrientdropdown.currentText()
            datatypetouse = self.datatypedropdown.currentText()

            selectedindexes = [k for k, i in enumerate(self.datatypes) if i == nuttouse]
            nutrientdatatypes = [self.sampleids[k] for k in selectedindexes]
            nutrientprocvals = [self.procvalues[k] for k in selectedindexes]
            nutrientrunnos = [self.runnos[k] for k in selectedindexes]
            selecteddatatypeindexes = [k for k, i in enumerate(nutrientdatatypes) if i[0:7] == datatypetouse[0:7]]
            selectednutrientprocvals = [float(nutrientprocvals[k]) for k in selecteddatatypeindexes]
            selectednutrientrunnos = [nutrientrunnos[k] for k in selecteddatatypeindexes]

            runnoset = set(nutrientrunnos)
            secondarycount = 0
            for i in runnoset:
                count = 0
                for k in range(len(selectednutrientrunnos)):
                    if i == selectednutrientrunnos[k]:
                        count = count + 1
                if count > secondarycount:
                    secondarycount = count
            columncount = secondarycount + 2
            rowcount = len(runnoset)

            self.tab = displayTable(nuttouse, datatypetouse, columncount, runnoset, selectednutrientprocvals,
                                    selectednutrientrunnos)
            self.tab.show()
        except Exception as e:
            print(e)

    def saveallmethod(self):
        if os.path.exists(self.filepathline.text()):
            try:
                nuttouse = self.nutrientdropdown.currentText()
                datatypetouse = self.datatypedropdown.currentText()

                selectedindexes = [k for k, i in enumerate(self.datatypes) if i == nuttouse]
                nutrientdatatypes = [self.sampleids[k] for k in selectedindexes]
                nutrientprocvals = [self.procvalues[k] for k in selectedindexes]
                nutrientrunnos = [self.runnos[k] for k in selectedindexes]
                selecteddatatypeindexes = [k for k, i in enumerate(nutrientdatatypes) if i[0:7] == datatypetouse[0:7]]
                selectednutrientprocvals = [float(nutrientprocvals[k]) for k in selecteddatatypeindexes]
                selectednutrientrunnos = [nutrientrunnos[k] for k in selecteddatatypeindexes]

                meantemp = []
                means = []
                runnos = []
                runnumbers = sorted(list(set(selectednutrientrunnos)))

                for x in runnumbers:
                    for i, y in enumerate(selectednutrientprocvals):
                        if x == selectednutrientrunnos[i]:
                            meantemp.append(y)

                    means.append(statistics.mean(meantemp))
                    runnos.append(x)
                    meantemp = []

                packeddata = list(zip(selectednutrientrunnos, selectednutrientprocvals))
                meanpackeddata = list(zip(runnos, means))

                savePath = QFileDialog.getSaveFileName(self, 'Save data', '', '(*.csv)')
                print(savePath)

                if savePath:
                    with open(savePath[0], 'w+', newline='') as file:
                        write = csv.writer(file)

                        write.writerow(['Minimum', 'Maximum', 'Median', 'Mean', 'OverallStdDev'])
                        write.writerow([self.minval.text(), self.maxval.text(), self.medianval.text(),
                                        self.meanval.text(), self.stdevval.text()])
                        write.writerow(['Min StDev', 'Max StDev', 'Mean StDev', 'Median StDev', 'Inter-run StDev Mean'])
                        write.writerow(
                            [self.minstdev.text(), self.maxstdev.text(), self.meanstdev.text(), self.medianstdev.text(),
                             self.intrastdevval.text()])
                        write.writerow(['All Values'])
                        write.writerow(['Run', 'Conc'])
                        for x in packeddata:
                            write.writerow(x)
                        write.writerow([''])
                        write.writerow(['Averaged Values'])
                        write.writerow(['Run', 'Mean Conc'])
                        for x in meanpackeddata:
                            write.writerow(x)

            except Exception as e:
                print(e)

    def loadplotmethod(self):
        try:
            nuttouse = self.nutrientdropdown.currentText()
            datatypetouse = self.datatypedropdown.currentText()

            selectedindexes = [k for k, i in enumerate(self.datatypes) if i == nuttouse]
            nutrientdatatypes = [self.sampleids[k] for k in selectedindexes]
            nutrientprocvals = [self.procvalues[k] for k in selectedindexes]
            nutrientrunnos = [self.runnos[k] for k in selectedindexes]
            selecteddatatypeindexes = [k for k, i in enumerate(nutrientdatatypes) if i[0:7] == datatypetouse[0:7]]
            selectednutrientprocvals = [float(nutrientprocvals[k]) for k in selecteddatatypeindexes]
            selectednutrientrunnos = [int(nutrientrunnos[k]) for k in selecteddatatypeindexes]
            holder = set(selectednutrientrunnos)
            runticks = list(holder)
            print(runticks)
            staggeredrunnos = []

            for i in runticks:
                counter = 0
                for k in selectednutrientrunnos:
                    if i == k:
                        counter = counter + 1
                denomenator = 1 / counter
                for j in range(counter):
                    runnumber = i + (denomenator * j)
                    staggeredrunnos.append(runnumber)

            meanval = statistics.mean(selectednutrientprocvals)
            yminlim = meanval * 0.97
            ymaxlim = meanval * 1.03
            plot = plt.plot(staggeredrunnos, selectednutrientprocvals, '-o', markerfacecolor="None", markersize=10,
                            linewidth=0.1)
            plt.xticks(range(max(runticks) + 2))
            plt.ylim(yminlim, ymaxlim)
            plt.xlim((min(runticks) - 1), (max(runticks) + 2))
            plt.xlabel('Run number')
            plt.ylabel('Concentration (uM)')
            plt.grid('-', linewidth=0.5, alpha=0.2)
            if nuttouse == 'NOx':
                if datatypetouse == 'RMNS CJ':
                    noxcj = 16.621
                    plt.plot([0, 1000], [noxcj, noxcj], '--', color="black", alpha=0.2, linewidth=1)
                    plt.plot([0, 1000], [noxcj * 0.99, noxcj * 0.99], color="green", alpha=0.7)
                    plt.plot([0, 1000], [noxcj * 1.01, noxcj * 1.01], color="green", alpha=0.7)
                    plt.plot([0, 1000], [noxcj * 0.98, noxcj * 0.98], color="orange", alpha=0.6)
                    plt.plot([0, 1000], [noxcj * 1.02, noxcj * 1.02], color="orange", alpha=0.6)

                if datatypetouse == 'RMNS CD':
                    noxcd = 5.648
                    plt.plot([0, 1000], [noxcd, noxcd], '--', color="black", alpha=0.2, linewidth=1)
                    plt.plot([0, 1000], [noxcd * 0.99, noxcd * 0.99], color="green", alpha=0.7)
                    plt.plot([0, 1000], [noxcd * 1.01, noxcd * 1.01], color="green", alpha=0.7)
                    plt.plot([0, 1000], [noxcd * 0.98, noxcd * 0.98], color="orange", alpha=0.6)
                    plt.plot([0, 1000], [noxcd * 1.02, noxcd * 1.02], color="orange", alpha=0.6)

            if nuttouse == 'Phosphate':
                if datatypetouse == 'RMNS CJ':
                    plt.plot([0, 1000], [1.219, 1.219], '--', color="black", alpha=0.2, linewidth=0.5)

                if datatypetouse == 'RMNS CD':
                    plt.plot([0, 1000], [0.457, 0.457], '--', color="black", alpha=0.2, linewidth=0.5)

            if nuttouse == 'Silicate':
                if datatypetouse == 'RMNS CJ':
                    plt.plot([0, 1000], [39.424, 39.424], '--', color="black", alpha=0.2, linewidth=0.5)

                if datatypetouse == 'RMNS CD':
                    plt.plot([0, 1000], [14.264, 14.264], '--', color="black", alpha=0.2, linewidth=0.5)

            if nuttouse == 'Nitrite':
                if datatypetouse == 'RMNS CJ':
                    plt.plot([0, 1000], [0.032, 0.032], '--', color="black", alpha=0.2, linewidth=0.5)

                if datatypetouse == 'RMNS CD':
                    plt.plot([0, 1000], [0.018, 0.018], '--', color="black", alpha=0.2, linewidth=0.5)
            plt.show()

        except Exception as e:
            print(e)

    def getindex(self, arr, searchitem):
        for i, x in enumerate(arr):
            for j, y in enumerate(x):
                if y == searchitem:
                    return i, j
        return "blueberry"  # if not found, but shouldn't happen unless doing check


class displayTable(QMainWindow):

    def __init__(self, nutrient, datatype, colcount, runnos, nutrientprocvals, nutrientrunnos):
        super().__init__()
        self.nutrient = nutrient
        self.datatype = datatype
        self.colcount = colcount
        self.runnos = runnos
        self.selectednutrientrunnos = nutrientrunnos
        self.selectednutrientprocvals = nutrientprocvals
        self.setWindowIcon(QtGui.QIcon(':/assets/2dropsshadow.svg'))
        self.left = 400
        self.top = 400
        self.width = 700
        self.height = 600

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.initUI()

    def initUI(self):
        deffont = QFont('Segoe UI')

        self.setGeometry(self.left, self.top, self.width, self.height)

        # self.setFixedSize(self.size())

        self.setWindowTitle('Data Table: ' + str(self.nutrient) + ' - ' + str(self.datatype))
        try:
            gridlayout = QGridLayout()
            self.datatable = QTableWidget(self)
            # datatable.setFont(deffont)
            self.datatable.setRowCount(len(self.runnos))
            self.datatable.setColumnCount((self.colcount - 1))
            headerlabels = []
            headerlabels.append('Mean')
            headerlabels.append('Stdev')
            reps = int(self.colcount) - 1
            for j in range(reps):
                num = j + 1
                headerlabels.append('Replicate ' + str(num))
            self.datatable.setHorizontalHeaderLabels(headerlabels)

            sortedrunnos = sorted(self.runnos, key=int)
            self.datatable.setVerticalHeaderLabels(sortedrunnos)

            rowcount = 0
            for i in sortedrunnos:

                meanbuffer = []
                rownumbers = []
                checker = 0
                for k in range(len(self.selectednutrientrunnos)):
                    if self.selectednutrientrunnos[k] == i:
                        meanbuffer.append(self.selectednutrientprocvals[k])
                        checker = checker + 1
                if checker > 1:
                    meanholder = statistics.mean(meanbuffer)
                    stdevholder = statistics.stdev(meanbuffer)
                    roundedmeanholder = round(meanholder, 3)
                    roundedstdevholder = round(stdevholder, 3)
                    rownumbers.append(roundedmeanholder)
                    rownumbers.append(roundedstdevholder)
                    for v in range(len(meanbuffer)):
                        rownumbers.append(meanbuffer[v])
                    for b in range(len(rownumbers)):
                        self.datatable.setItem((rowcount), b, QtWidgets.QTableWidgetItem(str(rownumbers[b])))

                if checker == 1:
                    oneresultheaderlabel = ['Result']
                    self.datatable.setHorizontalHeaderLabels(oneresultheaderlabel)
                    for v in range(len(meanbuffer)):
                        rownumbers.append(meanbuffer[v])
                    for b in range(len(rownumbers)):
                        self.datatable.setItem((rowcount), b, QtWidgets.QTableWidgetItem(str(rownumbers[b])))

                rowcount = rowcount + 1
                meanbuffer = []
                rownumbers = []

            gridlayout = QGridLayout()
            gridlayout.setSpacing(4)

            gridlayout.addWidget(self.datatable, 0, 0)

            self.centralWidget().setLayout(gridlayout)

        except Exception as e:
            print(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = qcReaderMain()
    sys.exit(app.exec_())
