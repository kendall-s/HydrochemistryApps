import sys, os, traceback
from package import fix_qt_import_error
import pandas as pd
from netCDF4 import Dataset
from time import sleep
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QGridLayout, QLabel, QPushButton,
                             QFrame, QLineEdit, QFileDialog, QComboBox, QListWidget, QAbstractItemView, QTableWidget,
                             QCheckBox, QHeaderView, QTableWidgetItem)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
import matplotlib as mpl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

import hyproicons

mpl.style.use('seaborn-muted')
mpl.rc('font', family='Segoe UI Symbol')  # Cast Segoe UI font onto all plot text


class Dataqc(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(':/assets/icon.svg'))
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.header_key = {'NOx': 'NOx (uM)', 'Phosphate': 'Phosphate (uM)', 'Silicate': 'Silicate (uM)',
                           'Ammonia': 'Ammonia (uM)', 'Nitrite': 'Nitrite (uM)', 'Salinity': 'Salinity (PSU)',
                           'Oxygen': 'Oxygen (uM)'}
        self.flag_key = {'NOx': 'NOx flag', 'Phosphate': 'Phosphate flag', 'Silicate': 'Silicate flag',
                         'Ammonia': 'Ammonia flag', 'Nitrite': 'Nitrite flag', 'Salinity': 'Salinity flag',
                         'Oxygen': 'Oxygen flag'}

        self.init_ui()

        self.csvdf = pd.DataFrame()
        self.csvtempdf = pd.DataFrame()
        self.ncdf = pd.DataFrame()

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
        ''')

    def init_ui(self):
        self.setFont(QFont('Segoe UI'))

        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        self.setGeometry(0, 0, 1350, 750)
        qtRectangle = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.setWindowTitle('Hydro Data QuickQCer')

        depscsv_label = QLabel('Hydro Deps CSV:')

        self.csv_path = QLineEdit('')
        self.csv_path.setReadOnly(True)

        csv_browse = QPushButton('Browse for CSV')
        csv_browse.clicked.connect(self.csv_browse_path)

        depnc_label = QLabel('Hydro Deps NC Folder:')

        self.nc_path = QLineEdit('')
        self.nc_path.setReadOnly(True)

        nc_browse = QPushButton('Browse for NC folder')
        nc_browse.clicked.connect(self.nc_browse_path)

        load_files = QPushButton('Load files')
        load_files.clicked.connect(self.load_filesf)

        self.csv_loaded = QCheckBox('CSV Loaded!')
        # self.csv_loaded.setCheckable(False)

        self.nc_loaded = QCheckBox('NC Loaded!')
        # self.nc_loaded.setCheckable(False)

        linesep1 = QFrame()
        linesep1.setFrameShape(QFrame.HLine)
        linesep1.setFrameShadow(QFrame.Sunken)

        param_label = QLabel('Parameter: ')

        self.params_combo = QComboBox()
        self.params_combo.addItems(['NOx', 'Phosphate', 'Silicate', 'Ammonia', 'Nitrite', 'Salinity', 'Oxygen'])
        self.params_combo.setEditable(True)
        self.params_combo.lineEdit().setAlignment(Qt.AlignHCenter)
        self.params_combo.lineEdit().setReadOnly(True)

        deps_label = QLabel('Deployments:')

        self.deps_list = QListWidget()
        self.deps_list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.draw_csv = QCheckBox('Draw CSV')
        self.draw_nc = QCheckBox('Draw NC')
        self.draw_woa = QCheckBox('Draw WOA18')


        view = QPushButton('View')
        view.setFixedWidth(130)
        view.clicked.connect(self.view_data)

        self.figure = plt.figure()
        self.figure.set_tight_layout(tight=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)

        self.flag_table = QTableWidget()
        self.flag_table.setColumnCount(7)
        self.flag_table.setHorizontalHeaderLabels(['Dep', 'RP', 'CSV Flag', 'NC Flag', 'Match', 'CSV Conc', 'NC Conc'])
        header = self.flag_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)

        grid_layout.addWidget(depscsv_label, 0, 0)
        grid_layout.addWidget(self.csv_path, 1, 0, 1, 2)
        grid_layout.addWidget(csv_browse, 2, 1)
        grid_layout.addWidget(depnc_label, 3, 0)
        grid_layout.addWidget(self.nc_path, 4, 0, 1, 2)
        grid_layout.addWidget(nc_browse, 5, 1)
        grid_layout.addWidget(load_files, 6, 0, 1, 2)
        grid_layout.addWidget(self.csv_loaded, 7, 0, Qt.AlignHCenter)
        grid_layout.addWidget(self.nc_loaded, 7, 1, Qt.AlignHCenter)
        grid_layout.addWidget(linesep1, 8, 0, 1, 2)
        grid_layout.addWidget(param_label, 9, 0)
        grid_layout.addWidget(self.params_combo, 9, 1)
        grid_layout.addWidget(deps_label, 10, 0)
        grid_layout.addWidget(self.deps_list, 11, 0, 14, 2)
        grid_layout.addWidget(self.draw_csv, 25, 0)
        grid_layout.addWidget(self.draw_nc, 26, 0)
        grid_layout.addWidget(self.draw_woa, 27, 0)

        grid_layout.addWidget(view, 25, 1, 3, 1, Qt.AlignHCenter)

        grid_layout.addWidget(self.canvas, 0, 3, 27, 5)

        grid_layout.addWidget(self.flag_table, 0, 9, 27, 3)

        self.mainplot = self.figure.add_subplot(111)
        self.mainplot.set_facecolor('#f4f4f4')

        self.centralWidget().setLayout(grid_layout)

        self.show()

    def increment_deployment(self):
        # Used to increment the deployment number by 1, this then updates the plot and tables
        # uses keyboard button/letter N to increment the deployment number
        try:
            selected_index = self.deps_list.currentRow()
            next_index = selected_index + 1
            self.deps_list.setCurrentRow(next_index)

            self.view_data()

        except Exception:
            print(traceback.print_exc())

    def view_flags(self):
        # The function that populates the table with all the flags and concentrations for each point

        # Get current parameter of interest and convert it the relevant header name
        current_param = self.params_combo.currentText()
        param_header_key = self.header_key[current_param]
        param_flag_key = self.flag_key[current_param]

        deps = []
        rp = []
        match = []
        csvflags = []
        csvconc = []
        ncflags = []
        ncconc = []

        # Need to check if either dataset is getting drawn, as the draw function initially creates
        # the subsetted data to use
        if self.draw_csv.isChecked() == True:
            deps = self.csvdf['Deployment']
            rp = self.csvdf['RP']
            csvflags = self.csvdf[param_flag_key]
            csvflags = [int(x) for x in csvflags]
            csvconc = self.csvdf[param_header_key]
            csvconc = [round(x, 3) for x in csvconc]

        if self.draw_nc.isChecked() == True:
            ncflags = self.ncdf[param_flag_key]
            ncconc = self.ncdf[param_header_key]
            ncconc = [round(x, 3) for i, x in enumerate(ncconc) if x != '--' and ncflags[i] != 133]
            ncflags = [x for x in ncflags if x != 141 and x != 133]

            # Checking if the flags match and adding the result to a list to get displayed
            if self.draw_csv.isChecked() == True:
                match = []
                for i, x in enumerate(csvflags):
                    if x == ncflags[i]:
                        match.append('OK')
                    elif int(ncflags[i]) == 141:
                        match.append('OK')
                    elif int(ncflags[i] == 133):
                        match.append('OK')
                    else:
                        match.append('*DIF*')

        # If both are csv and nc are ticked to be drawn, package data from both and populate table
        if self.draw_csv.isChecked() == True and self.draw_nc.isChecked() == True:
            packed = list(zip(deps, rp, csvflags, ncflags, match, csvconc, ncconc))

            self.flag_table.setRowCount(len(packed))

            for row, x in enumerate(packed):
                for col, y in enumerate(x):
                    self.flag_table.setItem(row, col, QTableWidgetItem(str(y)))


    def view_data(self):
        # This subsets the data from the initial datasets based on the deployments selected to be viewed
        # this will also plot the nc data with varying markers based on bad data, csv includes no bad data so it is
        # just a straight plot
        self.mainplot.clear()

        self.csvdf = pd.DataFrame()
        self.ncdf = pd.DataFrame()
        data_hold = pd.DataFrame()
        legend_labels = []

        current_param = self.params_combo.currentText()
        param_header_key = self.header_key[current_param]
        param_flag_key = self.flag_key[current_param]

        selected_deps = self.deps_list.selectedItems()
        sel_deps = [item.text() for item in selected_deps]

        try:
            if self.draw_csv.isChecked() == True:
                # If draw csv checkbox is checked draw the csv data to the plot, this is basic due to
                # the csv not carrying any bad data, the load data function already made the csv a DF for us
                for x in sel_deps:
                    data_hold = data_hold.append(self.csvtempdf.loc[self.csvtempdf['Deployment'] == int(x)])
                    data_hold = data_hold.dropna(0, subset=[param_header_key])
                    self.mainplot.plot(data_hold[param_header_key], data_hold['Pressure'], marker='o', ms=5, mfc='none',
                                       linewidth=0.75)
                    legend_labels.append('Deployment ' + str(x))
                    self.csvdf = self.csvdf.append(data_hold)
                    data_hold = pd.DataFrame()
                if self.draw_woa.isChecked() == True and self.params_combo.currentText() == 'NOx':
                    #The WOA data is separated by month, so work out the closest month data that will match the CTD
                    time_check = self.csvdf['Time'].iloc[0]
                    month = time_check[5:7]
                    # Open file that corresponds to that month

                    file_path = 'C:/Users/she384/Documents/woa18nitratecsv/woa18_all_n' + str(month) + 'mn01.csv'
                    print(file_path)
                    woa_df = pd.read_csv(file_path, header=1)

                    lat_check = round(self.csvdf['Latitude'].iloc[0], 1)
                    string_lat_check = str(lat_check)
                    if int(string_lat_check[-1]) > 5:
                        tt = float(str(string_lat_check[:-2] + '.5'))
                        pp = lat_check - tt
                        lat_check = lat_check - pp
                    else:
                        tt = float(str(string_lat_check[:-2] + '.5'))
                        pp = tt - lat_check
                        lat_check = lat_check + pp

                    lon_check = round(self.csvdf['Longitude'].iloc[0], 1)
                    string_lon_check = str(lon_check)
                    if int(string_lon_check[-1]) > 5:
                        tt = float(str(string_lon_check[:-2] + '.5'))
                        pp = lon_check - tt
                        lon_check = lon_check - pp
                    else:
                        tt = float(str(string_lon_check[:-2] + '.5'))
                        pp = tt - lon_check
                        lon_check = lon_check + pp

                    woa_df2 = woa_df.loc[woa_df['#COMMA SEPARATED LATITUDE'] == lat_check]
                    woa_df3 = woa_df2.loc[woa_df2[' LONGITUDE'] == lon_check]

                    print(str(lat_check) + '  ' + str(lon_check))
                    print(woa_df3)
                    woa_depths = []
                    woa_concs = []
                    if not woa_df3.empty:
                        for i, col in enumerate(woa_df3):
                            if i > 1:
                                if i == 2:
                                    woa_depths.append(0)
                                else:
                                    woa_depths.append(int(col))
                                woa_concs.append(woa_df3[col].iloc[0])

                    print(woa_depths)
                    self.mainplot.plot(woa_concs, woa_depths, marker='o', ms=7, mfc='none', linewidth=0.75)




            if self.draw_nc.isChecked() == True:
                # If the nc checkbox is checked draw the nc data to the plot, this is more complicated due to a number
                # of factors, 1: the nc includes bad data, 2: missing data is stored as '--' which we need to get
                # rid of, 3: for missing data it includes an extra flag which needs to be discarded

                files_in_direc = os.listdir(self.nc_path.text())
                for file in files_in_direc: # Cycle through the files in the specified directory
                    if file[-2:] == 'nc':
                        ds = Dataset(self.nc_path.text() + '/' + file)
                        deploy = ds.Deployment
                        for x in sel_deps: # Loop through the selected deployments to find the right file
                            if int(x) == int(deploy):
                                deps_list = []
                                for y in range(ds.dimensions['pressure'].size):
                                    deps_list.append(deploy) # Make a list of the dep number the length of data

                                # Zip up the data so it can be easily input into a dataframe, the 3rd dimension
                                # contains the data we want, this is the dimension based along pressure
                                dszipped = list(zip(deps_list,
                                                    ds.variables['pressure'][:],
                                                    ds.variables['rosettePosition'][0, 0, :, 0],
                                                    ds.variables['oxygen'][0, 0, :, 0],
                                                    ds.variables['oxygenFlag'][0, 0, :, 0],
                                                    ds.variables['salinity'][0, 0, :, 0],
                                                    ds.variables['salinityFlag'][0, 0, :, 0],
                                                    ds.variables['nox'][0, 0, :, 0],
                                                    ds.variables['noxFlag'][0, 0, :, 0],
                                                    ds.variables['phosphate'][0, 0, :, 0],
                                                    ds.variables['phosphateFlag'][0, 0, :, 0],
                                                    ds.variables['silicate'][0, 0, :, 0],
                                                    ds.variables['silicateFlag'][0, 0, :, 0],
                                                    ds.variables['ammonia'][0, 0, :, 0],
                                                    ds.variables['ammoniaFlag'][0, 0, :, 0],
                                                    ds.variables['nitrite'][0, 0, :, 0],
                                                    ds.variables['nitriteFlag'][0, 0, :, 0]))

                                tempdf = pd.DataFrame(dszipped,
                                                         columns=['Deployment', 'Pressure', 'RP', 'Oxygen (uM)',
                                                                  'Oxygen flag',
                                                                  'Salinity (PSU)', 'Salinity flag',
                                                                  'NOx (uM)',
                                                                  'NOx flag', 'Phosphate (uM)', 'Phosphate flag',
                                                                  'Silicate (uM)',
                                                                  'Silicate flag',
                                                                  'Ammonia (uM)', 'Ammonia flag', 'Nitrite (uM)',
                                                                  'Nitrite flag'])

                                # Plot the NC data onto the figure
                                self.mainplot.plot(tempdf[param_header_key], tempdf['Pressure'], marker='o',
                                                   ms=0, mfc='none',
                                                   linewidth=0.0)

                                ncflags = tempdf[param_flag_key]
                                pres = tempdf['Pressure']
                                for i, v in enumerate(tempdf[param_header_key]):
                                    #print(ncflags[i])
                                    if ncflags[i] == 133 or ncflags[i] == 134 or ncflags[i] == 129:
                                        self.mainplot.plot(v, pres[i], marker='x', ms=7, linewidth=0, mec='#ac3232',
                                                           mfc='none')
                                    if ncflags[i] == 69 or ncflags[i] == 65:
                                        self.mainplot.plot(v, pres[i], marker='x', ms=9, linewidth=0, mec='#5fcde4',
                                                           mfc='none')
                                    else:
                                        self.mainplot.plot(v, pres[i], marker='s', ms=2, linewidth=0, mec='#39c88e',
                                                           mfc='#39c88e')
                                # For use in matching up flags an instance var is used to hold the selected deployments
                                # worth of data, appending using ignore index so it will just tack each dep on
                                # to the bottom of the dataframe for each loop
                                self.ncdf = self.ncdf.append(tempdf, ignore_index=True)

            # At the end of the whole fiasco format the figure to how we like
            self.mainplot.invert_yaxis()
            self.mainplot.set_facecolor('#f4f4f4')
            self.mainplot.grid(alpha=0.2, linewidth=0.5)
            self.mainplot.legend(legend_labels)
            self.mainplot.set_xlabel(self.header_key[str(current_param)])
            self.mainplot.set_ylabel('Pressure (db)')

            self.canvas.draw()

            self.view_flags()

        except Exception:
            print(traceback.print_exc())

    def load_filesf(self):
        # This function is a bit of a facade, it only really loads in the CSV file as a dataframe, this is to
        # populate the deployments list so a user can select a dep, it checks to make sure a nc file is in the
        # directory then ticks the nc loaded checkbox as a visual indicator for the user
        try:
            if os.path.exists(self.csv_path.text()):
                self.csvtempdf = pd.read_csv(self.csv_path.text())
                deps = list(set(self.csvtempdf['Deployment']))
                self.populate_list(deps)
                self.csv_loaded.setChecked(True)

            if os.path.exists(self.nc_path.text()):
                files_in_direc = os.listdir(self.nc_path.text())
                for file in files_in_direc:
                    if file[-2:] == 'nc':
                        self.nc_loaded.setChecked(True)

        except Exception:
            print(traceback.print_exc())

    def populate_list(self, items):
        # Adds the dep numbers to the qlistwidget
        self.deps_list.clear()
        for x in items:
            self.deps_list.addItem(str(x))

    def csv_browse_path(self):
        path = QFileDialog.Options()
        files = QFileDialog.getOpenFileName(self, "Select CSV", 'c://', "csv (*.csv)")
        if os.path.exists(files[0]):
            self.csv_path.setText(files[0])

    def nc_browse_path(self):
        path = QFileDialog.Options()
        files = QFileDialog.getExistingDirectory(self, "Select Folder containing NC files")
        if os.path.exists(files):
            self.nc_path.setText(files)

    def keyPressEvent(self, event):
        #print(event.key())
        # Used for incrementing the deployment number to quickly zoom through plots
        if event.key() == 78:
            self.increment_deployment()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Dataqc()
    sys.exit(app.exec_())