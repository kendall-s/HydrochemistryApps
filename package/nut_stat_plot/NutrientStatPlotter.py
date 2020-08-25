import sys, os, traceback, io, csv, time
from time import sleep
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QGridLayout, QDesktopWidget, QLabel, QPushButton,
                             QFrame, QLineEdit, QFileDialog, QComboBox, QListWidget, QAbstractItemView, QTableWidget,
                             QCheckBox, QHeaderView, QRadioButton, QButtonGroup)
from PyQt5.QtGui import QIcon, QFont, QImage
from PyQt5.QtCore import Qt
import matplotlib as mpl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt
import hyproicons

mpl.style.use('seaborn-muted')
mpl.rc('font', family='Segoe UI Symbol')  # Cast Segoe UI font onto all plot text


class NutrientStatPlotter(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(':/assets/icon.svg'))
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.header_key = {'NOx': 'NOx', 'Phosphate': 'PHOSPHATE', 'Silicate': 'SILICATE',
                           'Ammonia': 'AMMONIA', 'Nitrite': 'NITRITE', 'Salinity': 'Salinity (PSU)',
                           'Oxygen': 'Oxygen (uM)'}

        self.init_ui()

        self.reagent_colour = '#000000'
        self.reaglines = []
        self.legend_label = ''
        self.rad_sel = 'none'

        self.setStyleSheet('''
        QLabel {
            font: 14px;
        }   
        QPushButton {
            font: 14px;
        }
        QComboBox {
            font: 14px;
        }
        QListWidget {

            font: 14px;
        }
        QTableWidget {
            font: 14px;
        }
        QCheckBox {
            font: 14px;
        }
        QRadioButton {
            font: 14px;
        }
        ''')

    def init_ui(self):
        self.setFont(QFont('Segoe UI'))

        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        self.setGeometry(0, 0, 950, 500)
        qtRect = self.frameGeometry()
        centrePoint = QDesktopWidget().availableGeometry().center()
        qtRect.moveCenter(centrePoint)
        self.move(qtRect.topLeft())

        self.setWindowTitle('Hydro Nut Base/Gain Plotter')

        folder_label = QLabel('Find folder that contains a voyages worth \nof nutrient .SLK files: ')

        self.folder_path = QLineEdit('')

        folder_browse = QPushButton('Browse...')
        folder_browse.clicked.connect(self.locate_folder)

        linesep1 = QFrame()
        linesep1.setFrameShape(QFrame.HLine)
        linesep1.setFrameShadow(QFrame.Sunken)

        nutrient_label = QLabel('Select Nutrient to view: ')

        self.select_nutrient = QComboBox()
        self.select_nutrient.addItems(['NOx', 'Phosphate', 'Silicate', 'Ammonia', 'Nitrite'])
        self.select_nutrient.currentTextChanged.connect(self.populate_radios)

        self.draw_base = QCheckBox('Draw Baseline Offset')

        self.draw_gain = QCheckBox('Draw Gain')

        plot_by_label = QLabel('Plot Data By: ')

        self.plot_by_option = QComboBox()
        self.plot_by_option.addItems(['Analysis', 'Date'])

        draw = QPushButton('View Data')
        draw.clicked.connect(self.draw_data)

        linesep2 = QFrame()
        linesep2.setFrameShape(QFrame.HLine)
        linesep2.setFrameShadow(QFrame.Sunken)

        plot_drawing_label = QLabel('Draw Line for Fresh Reagent')

        self.nox_colour = QRadioButton('NEDD Colour')
        self.nox_colour.toggled.connect(lambda: self.radio_selected(self.nox_colour))
        self.nox_buffer = QRadioButton('Amm Chl Buffer')
        self.nox_buffer.toggled.connect(lambda: self.radio_selected(self.nox_buffer))
        self.nox_column = QRadioButton('Cadmium Column')
        self.nox_column.toggled.connect(lambda: self.radio_selected(self.nox_column))

        self.nitrite_colour = QRadioButton('NEDD Colour')
        self.nitrite_colour.toggled.connect(lambda: self.radio_selected(self.nitrite_colour))

        self.phosphate_colour = QRadioButton('Phos Molybdate Colour')
        self.phosphate_colour.toggled.connect(lambda: self.radio_selected(self.phosphate_colour))
        self.phoshphate_acid = QRadioButton('Ascorbic Acid')
        self.phoshphate_acid.toggled.connect(lambda: self.radio_selected(self.phoshphate_acid))

        self.silicate_colour = QRadioButton('Sil Molybdate Colour')
        self.silicate_colour.toggled.connect(lambda: self.radio_selected(self.silicate_colour))
        self.silicate_acid = QRadioButton('Tartaric Acid')
        self.silicate_acid.toggled.connect(lambda: self.radio_selected(self.silicate_acid))
        self.silicate_reductant = QRadioButton('Stannous Chloride')
        self.silicate_reductant.toggled.connect(lambda: self.radio_selected(self.silicate_reductant))

        self.ammonia_reagent = QRadioButton('OPA')
        self.ammonia_reagent.toggled.connect(lambda: self.radio_selected(self.ammonia_reagent))

        self.erase = QPushButton('Undo')
        self.erase.clicked.connect(self.undo_plot)

        self.copy = QPushButton('Copy')
        self.copy.clicked.connect(self.copy_plot)

        self.figure = plt.figure()
        self.figure.set_tight_layout(tight=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)

        self.toolbar = NavigationToolbar(self.canvas, self)

        grid_layout.addWidget(folder_label, 0, 0, 1, 3)
        grid_layout.addWidget(self.folder_path, 1, 0, 1, 3)
        grid_layout.addWidget(folder_browse, 2, 2, 1, 1)
        grid_layout.addWidget(linesep1, 3, 0, 1, 3)

        grid_layout.addWidget(nutrient_label, 4, 0, 1, 3)
        grid_layout.addWidget(self.select_nutrient, 4, 2)
        grid_layout.addWidget(self.draw_base, 6, 0, 1, 1)
        grid_layout.addWidget(self.draw_gain, 7, 0, 1, 1)
        grid_layout.addWidget(plot_by_label, 5, 0, 1, 3)
        grid_layout.addWidget(self.plot_by_option, 5, 2, 1, 1)

        grid_layout.addWidget(draw, 8, 0, 1, 3)

        grid_layout.addWidget(linesep2, 9, 0, 1, 3)

        grid_layout.addWidget(plot_drawing_label, 10, 0, 1, 3)
        grid_layout.addWidget(self.nox_colour, 11, 0, 1, 2)
        grid_layout.addWidget(self.nox_buffer, 12, 0, 1, 2)
        grid_layout.addWidget(self.nox_column, 13, 0, 1, 2)
        grid_layout.addWidget(self.nitrite_colour, 11, 0, 1, 2)
        grid_layout.addWidget(self.phosphate_colour, 11, 0, 1, 2)
        grid_layout.addWidget(self.phoshphate_acid, 12, 0, 1, 2)
        grid_layout.addWidget(self.silicate_colour, 11, 0, 1, 2)
        grid_layout.addWidget(self.silicate_acid, 12, 0, 1, 2)
        grid_layout.addWidget(self.silicate_reductant, 13, 0, 1, 2)
        grid_layout.addWidget(self.ammonia_reagent, 11, 0, 1, 2)

        grid_layout.addWidget(self.erase, 14, 0)
        grid_layout.addWidget(self.copy, 14, 2)

        grid_layout.addWidget(self.canvas, 0, 3, 14, 7)
        grid_layout.addWidget(self.toolbar, 14, 3)

        self.mainplot = self.figure.add_subplot(111)
        self.mainplot.set_facecolor('#f9f9f9')
        self.second = self.mainplot.twinx()

        self.centralWidget().setLayout(grid_layout)

        self.populate_radios()

        self.show()

        clicker = self.figure.canvas.mpl_connect("button_press_event", self.on_click)

    def undo_plot(self):
        try:
            self.mainplot.lines.pop(-1)
            self.reaglines.pop(-1)
            self.canvas.draw()

        except Exception:
            print(traceback.print_exc())

    def copy_plot(self):
        buffer = io.BytesIO()
        self.figure.savefig(buffer, dpi=300)
        QApplication.clipboard().setImage(QImage.fromData(buffer.getvalue()))

    def draw_reagent_line(self, x):
        if self.rad_sel != 'none':
            current_ledge = self.mainplot.get_legend().texts
            current_labs = []
            for item in current_ledge:
                current_labs.append(item.get_text())

            if self.legend_label in current_labs:
                self.legend_label = ''

            bot, top = self.mainplot.get_ylim()
            self.reaglines.append(
                self.mainplot.plot([x+self.x_offset, x+self.x_offset], [-10000, 10000], color=self.reagent_colour,
                                   ls=self.line_styl, lw=1, label=self.legend_label))
            self.mainplot.set_ylim(bot, top)

            self.mainplot.legend()

            self.canvas.draw()

    def populate_radios(self):
        nut = self.select_nutrient.currentText()
        if nut == 'NOx':
            self.nox_colour.show()
            self.nox_buffer.show()
            self.nox_column.show()
            self.phoshphate_acid.hide()
            self.phosphate_colour.hide()
            self.silicate_acid.hide()
            self.silicate_colour.hide()
            self.silicate_reductant.hide()
            self.ammonia_reagent.hide()
            self.nitrite_colour.hide()

        if nut == 'Phosphate':
            self.nox_colour.hide()
            self.nox_buffer.hide()
            self.nox_column.hide()
            self.phoshphate_acid.show()
            self.phosphate_colour.show()
            self.silicate_acid.hide()
            self.silicate_colour.hide()
            self.silicate_reductant.hide()
            self.ammonia_reagent.hide()
            self.nitrite_colour.hide()

        if nut == 'Silicate':
            self.nox_colour.hide()
            self.nox_buffer.hide()
            self.nox_column.hide()
            self.phoshphate_acid.hide()
            self.phosphate_colour.hide()
            self.silicate_acid.show()
            self.silicate_colour.show()
            self.silicate_reductant.show()
            self.ammonia_reagent.hide()
            self.nitrite_colour.hide()

        if nut == 'Ammonia':
            self.nox_colour.hide()
            self.nox_buffer.hide()
            self.nox_column.hide()
            self.phoshphate_acid.hide()
            self.phosphate_colour.hide()
            self.silicate_acid.hide()
            self.silicate_colour.hide()
            self.silicate_reductant.hide()
            self.ammonia_reagent.show()
            self.nitrite_colour.hide()

        if nut == 'Nitrite':
            self.nox_colour.hide()
            self.nox_buffer.hide()
            self.nox_column.hide()
            self.phoshphate_acid.hide()
            self.phosphate_colour.hide()
            self.silicate_acid.hide()
            self.silicate_colour.hide()
            self.silicate_reductant.hide()
            self.ammonia_reagent.hide()
            self.nitrite_colour.show()

    def radio_selected(self, but):

        if but.text() == 'NEDD Colour':
            self.rad_sel = 'NEDD'
            self.reagent_colour = '#1664b7'
            self.line_styl = '--'
            self.x_offset = -0.1
            self.legend_label = 'NEDD Colour'

        if but.text() == 'Amm Chl Buffer':
            self.rad_sel = 'AmmChl'
            self.reagent_colour = '#52adce'
            self.line_styl = '-.'
            self.x_offset = 0.1
            self.legend_label = 'AmmChl Buffer'

        if but.text() == 'Cadmium Column':
            self.rad_sel = 'Cd Col'
            self.reagent_colour = '#3e536d'
            self.line_styl = ':'
            self.x_offset = 0.001
            self.legend_label = 'Cadmium Column'

        if but.text() == 'Phos Molybdate Colour':
            self.rad_sel = 'Molyb'
            self.reagent_colour = '#af2f21'
            self.line_styl = '--'
            self.x_offset = -0.1
            self.legend_label = 'Molybdate Colour'

        if but.text() == 'Ascorbic Acid':
            self.rad_sel = 'AA'
            self.reagent_colour = '#f79999'
            self.line_styl = '-.'
            self.x_offset = 0.1
            self.legend_label = 'Ascorbic Acid'

        if but.text() == 'Sil Molybdate Colour':
            self.rad_sel = 'Molyb'
            self.reagent_colour = '#056b1d'
            self.line_styl = '--'
            self.x_offset = -0.2
            self.legend_label = 'Molybdate Colour'

        if but.text() == 'Tartaric Acid':
            self.reagent_colour = '#4bb769'
            self.rad_sel = 'Tart'
            self.line_styl = '-.'
            self.x_offset = 0.2
            self.legend_label = 'Tartaric Acid'

        if but.text() == 'Stannous Chloride':
            self.reagent_colour = '#25893c'
            self.rad_sel = 'SnCl'
            self.line_styl = ':'
            self.x_offset = -0.02
            self.legend_label = 'Stannous Chloride'

        if but.text() == 'OPA':
            self.reagent_colour = '#d8d145'
            self.rad_sel = 'OPA'
            self.line_styl = '--'
            self.x_offset = 0
            self.legend_label = 'OPA'

    def draw_data(self):
        try:
            nutrient = self.header_key[self.select_nutrient.currentText()]
            folder_path = self.folder_path.text()
            plot_by = self.plot_by_option.currentText()
            draw_base = self.draw_base.isChecked()
            draw_gain = self.draw_gain.isChecked()

            count = 0
            runs = []
            base = []
            gain = []
            dates = []
            times = []
            filesindirec = os.listdir(folder_path)

            for file in filesindirec:
                print(file)
                if file[-4:] == '.SLK':

                    filearray = self.read_slk(folder_path + '/' + file)

                    nutx, nuty = self.getindex(filearray, '"' + nutrient + '"')

                    if nutx != 'no':
                        basex, basey = self.getindex(filearray, '"Base"')
                        base.append(int(filearray[basex][nuty]))

                        gainx, gainy = self.getindex(filearray, '"Gain"')
                        gain.append(filearray[gainx][nuty])

                        findx, findy = self.getindex(filearray, '"TIME"')
                        times.append(filearray[findx][findy + 1][1:-1])

                        findx, findy = self.getindex(filearray, '"DATE"')
                        dates.append(filearray[findx][findy + 1][1:-1])
                        count = count + 1
                        runs.append(count)

            self.mainplot.cla()
            self.second.cla()

            if self.plot_by_option.currentText() == 'Analysis':
                xaxis = runs
                xlabel = 'Analysis'
            else:
                tdstampformat = '%d/%m/%Y %H:%M:%S %p'
                tdstampconverts = []
                for i, x in enumerate(times):
                    tdstamp = dates[i] + ' ' + x
                    tdstampconverts.append(time.mktime(time.strptime(tdstamp, tdstampformat)))

                xaxis = tdstampconverts
                xlabel = 'Date'
                plotTimeFormat = '%d/%m/%y'
                xticks = self.linspace(min(xaxis), max(xaxis), 7)
                xlabels = [time.strftime(plotTimeFormat, time.gmtime(x)) for x in xticks]

            if draw_base == True:

                self.mainplot.plot(xaxis, base, marker='o', ms=6, lw=1, color='#bec2c4', mec='#999999',
                                   label='Baseline Offset')
                self.mainplot.grid(alpha=0.2)
                self.mainplot.set_ylabel('Baseline Offset', fontsize=12)

                if max(base) < 0:
                    self.mainplot.invert_yaxis()

            if draw_gain == True:
                if draw_base == True:
                    self.second.plot(xaxis, gain, marker='s', mfc='#a8a8a8', ms=6, lw=1, color='#bec2c4', label='Gain',
                                     mec='none', alpha=0.6)
                    self.second.set_ylabel('Gain', fontsize=12)
                else:
                    self.mainplot.plot(xaxis, gain, marker='o', mfc='#a8a8a8', ms=7, lw=1, color='#bec2c4', label='Gain',
                                       mec='none')
                    self.mainplot.grid(alpha=0.2)
                    self.second.set_yticks([])
                    self.second.set_yticklabels([])
                    self.mainplot.set_ylabel('Gain', fontsize=12)
            if draw_gain == False:
                self.second.set_yticks([])
                self.second.set_yticklabels([])

            self.mainplot.set_title(str(self.select_nutrient.currentText()), fontsize=15)
            self.mainplot.set_xlabel(xlabel, fontsize=12)
            if self.plot_by_option.currentText() == 'Date':
                plt.xticks(xticks, xlabels)

            self.mainplot.legend()

            self.canvas.draw()

        except Exception:
            print(traceback.print_exc())

    def linspace(self, start, stop, n):
        if n == 1:
            yield stop
            return
        h = (stop - start) / (n - 1)
        for i in range(n):
            yield start + h * i

    def on_click(self, event):
        if event.button == 1 and event.inaxes:
            xcoord = int(event.xdata)
            self.draw_reagent_line(xcoord)

    def locate_folder(self):
        path = QFileDialog.Options()
        files = QFileDialog.getExistingDirectory(self, "Select Folder containing NC files")
        if os.path.exists(files):
            self.folder_path.setText(files)

    def read_slk(self, file):

        with open(file) as fileread:
            read = csv.reader(fileread, delimiter=';')
            readlist = list(read)

        datasection = []
        # Now the .SLK will be parsed, this is messy because there are different 'versions' of the
        # .slk as there isn't a defined standard..
        # THe .slk is essentially a spreadshet and it will be broken up into an array
        for x in readlist:
            if x[0] == 'C' or x[0] == 'F':
                datasection.append(x)
                # Get size of spreadsheet to make array to hold data
            if x[0] == 'B':
                if x[1][0] == 'X':
                    w = int(x[1][1:])
                if x[2][0] == 'X':
                    w = int(x[2][1:])
                if x[2][0] == 'Y':
                    h = int(x[2][1:])
                if x[1][0] == 'Y':
                    h = int(x[1][1:])

        dataarray = [['' for i in range(w)] for j in range(h)]

        row = 0
        col = 0
        for x in datasection:
            try:
                if x[1][0] == 'Y':
                    row = int(x[1][1:]) - 1
                if len(x) > 2:
                    if x[2][0] == 'X':
                        col = int(x[2][1:]) - 1
                if x[1][0] == 'X':
                    col = int(x[1][1:]) - 1
                if x[0][0] == 'F':
                    if len(x) == 4:
                        if x[3][0] == 'M':
                            fake = 0
                        else:
                            col = int(x[3][1:]) - 1
                    else:
                        if x[1][0] != 'W':
                            col = int(x[3][1:]) - 1

                dataarray[row][col] = x[-1][1:]


            except Exception as e:
                print(x)
                # print('len: ' + str(len(x)))

        return dataarray

    def getindex(self, arr, item):
        for i, x in enumerate(arr):
            for j, y in enumerate(x):
                if y == item:
                    return i, j
        return 'no', 'no'


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NutrientStatPlotter()
    sys.exit(app.exec_())
