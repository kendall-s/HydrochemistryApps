from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QPushButton, QLabel, QGridLayout, QTabWidget,
                             QLineEdit, QFileDialog, QTableWidget, QTableWidgetItem, QDesktopWidget, QFrame,
                             QVBoxLayout)
from PyQt5.QtGui import QIcon, QFont
# from PyQt5.QtCore import Qt.AlignCenter
import sys, os, csv
import pandas as pd
from netCDF4 import Dataset
import hyproicons
import traceback


class NC_check_main(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(':/assets/icon.svg'))
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.varis = ['salinity', 'salinityFlag', 'oxygen', 'oxygenFlag', 'nox', 'noxFlag', 'phosphate',
                      'phosphateFlag',
                      'silicate', 'silicateFlag', 'ammonia', 'ammoniaFlag', 'nitrite', 'nitriteFlag']

        self.csv_line_edits = ['salinity_name_csv', 'salinity_flag_csv', 'oxygen_name_csv', 'oxygen_flag_csv',
                               'nitrate_name_csv', 'nitrate_flag_csv', 'phosphate_name_csv', 'phosphate_flag_csv',
                               'silicate_name_csv', 'silicate_flag_csv', 'nitrite_name_csv', 'nitrite_flag_csv',
                               'ammonia_name_csv', 'ammonia_flag_csv']

        self.nc_line_edits = ['salinity_name_nc', 'salinity_flag_nc', 'oxygen_name_nc', 'oxygen_flag_nc',
                              'nitrate_name_nc', 'nitrate_flag_nc', 'phosphate_name_nc', 'phosphate_flag_nc',
                              'silicate_name_nc', 'silicate_flag_nc', 'nitrite_name_nc', 'nitrite_flag_nc',
                              'ammonia_name_nc', 'ammonia_flag_nc']

        self.resolutions = ['salinity_res', 'oxygen_res', 'nitrate_res', 'phosphate_res', 'silicate_res',
                            'nitrite_res', 'ammonia_res']

        self.diffs = [[], [], [], [], [], [], [], [], [], [], [], [], [], []]

        self.init_ui()

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
        QLineEdit {
            font: 13px;
        }
        ''')

    def init_ui(self):

        self.setFont(QFont('Segoe UI'))
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        self.setGeometry(0, 0, 690, 490)
        qtRect = self.frameGeometry()
        centrePoint = QDesktopWidget().availableGeometry().center()
        qtRect.moveCenter(centrePoint)
        self.move(qtRect.topLeft())

        self.setWindowTitle('Hydrology NC Checker')

        intro_label = QLabel('<b>Load in a .csv and the folder containing the .nc files</b>')

        csv_label = QLabel('Location of .csv file')
        self.csv_path = QLineEdit('')
        self.browse_csv = QPushButton('Browse')
        self.browse_csv.clicked.connect(self.browsecsv)

        nc_label = QLabel('Location of NC folder')
        self.nc_path = QLineEdit('')
        self.browse_nc = QPushButton('Browse')
        self.browse_nc.clicked.connect(self.browsenc)

        linesep1 = QFrame()
        linesep1.setFrameShape(QFrame.HLine)
        linesep1.setFrameShadow(QFrame.Sunken)

        options_label = QLabel('<b>Options</b>')

        csv_options_label = QLabel('CSV')

        nc_options_label = QLabel('NetCDF')

        salinity_label = QLabel('Salinity')
        self.salinity_name_csv = QLineEdit('Salinity (PSU)')
        self.salinity_flag_csv = QLineEdit('Salinity flag')
        self.salinity_name_nc = QLineEdit('salinity')
        self.salinity_flag_nc = QLineEdit('salinityFlag')
        self.salinity_res = QLineEdit('0.0001')

        oxygen_label = QLabel('Oxygen')
        self.oxygen_name_csv = QLineEdit('Oxygen (uM)')
        self.oxygen_flag_csv = QLineEdit('Oxygen flag')
        self.oxygen_name_nc = QLineEdit('oxygen')
        self.oxygen_flag_nc = QLineEdit('oxygenFlag')
        self.oxygen_res = QLineEdit('0.001')

        nitrate_label = QLabel('Nitrate')
        self.nitrate_name_csv = QLineEdit('NOx (uM)')
        self.nitrate_flag_csv = QLineEdit('NOx flag')
        self.nitrate_name_nc = QLineEdit('nox')
        self.nitrate_flag_nc = QLineEdit('noxFlag')
        self.nitrate_res = QLineEdit('0.01')

        phosphate_label = QLabel('Phosphate')
        self.phosphate_name_csv = QLineEdit('Phosphate (uM)')
        self.phosphate_flag_csv = QLineEdit('Phosphate flag')
        self.phosphate_name_nc = QLineEdit('phosphate')
        self.phosphate_flag_nc = QLineEdit('phosphateFlag')
        self.phosphate_res = QLineEdit('0.01')

        silicate_label = QLabel('Silicate')
        self.silicate_name_csv = QLineEdit('Silicate (uM)')
        self.silicate_flag_csv = QLineEdit('Silicate flag')
        self.silicate_name_nc = QLineEdit('silicate')
        self.silicate_flag_nc = QLineEdit('silicateFlag')
        self.silicate_res = QLineEdit('0.1')

        nitrite_label = QLabel('Nitrite')
        self.nitrite_name_csv = QLineEdit('Nitrite (uM)')
        self.nitrite_flag_csv = QLineEdit('Nitrite flag')
        self.nitrite_name_nc = QLineEdit('nitrite')
        self.nitrite_flag_nc = QLineEdit('nitriteFlag')
        self.nitrite_res = QLineEdit('0.001')

        ammonia_label = QLabel('Ammonia')
        self.ammonia_name_csv = QLineEdit('Ammonia (uM)')
        self.ammonia_flag_csv = QLineEdit('Ammonia flag')
        self.ammonia_name_nc = QLineEdit('ammonia')
        self.ammonia_flag_nc = QLineEdit('ammoniaFlag')
        self.ammonia_res = QLineEdit('0.01')

        name_label = QLabel('Name')
        flag_label = QLabel('Flag Name')
        name2_label = QLabel('Name')
        flag2_label = QLabel('Flag Name')
        res_label = QLabel('Resolution')

        linesep2 = QFrame()
        linesep2.setFrameShape(QFrame.HLine)
        linesep2.setFrameShadow(QFrame.Sunken)

        self.process_table = QPushButton('Show Differences Table')
        self.process_table.clicked.connect(self.diff_table)

        self.process_csv = QPushButton('Export Differences CSV')
        self.process_csv.clicked.connect(self.diff_csv)

        self.data_table = QTableWidget()

        grid_layout.addWidget(intro_label, 0, 0, 1, 3)

        grid_layout.addWidget(csv_label, 1, 0, 1, 2)
        grid_layout.addWidget(self.csv_path, 2, 0, 1, 5)
        grid_layout.addWidget(self.browse_csv, 2, 5)

        grid_layout.addWidget(nc_label, 3, 0, 1, 2)
        grid_layout.addWidget(self.nc_path, 4, 0, 1, 5)
        grid_layout.addWidget(self.browse_nc, 4, 5)

        grid_layout.addWidget(linesep1, 5, 0, 1, 6)

        grid_layout.addWidget(options_label, 6, 0)

        grid_layout.addWidget(csv_options_label, 6, 1, 1, 2)
        grid_layout.addWidget(nc_options_label, 6, 3, 1, 2)

        grid_layout.addWidget(name_label, 7, 1)
        grid_layout.addWidget(flag_label, 7, 2)
        grid_layout.addWidget(name2_label, 7, 3)
        grid_layout.addWidget(flag2_label, 7, 4)
        grid_layout.addWidget(res_label, 7, 5)

        grid_layout.addWidget(salinity_label, 8, 0)
        grid_layout.addWidget(self.salinity_name_csv, 8, 1)
        grid_layout.addWidget(self.salinity_flag_csv, 8, 2)
        grid_layout.addWidget(self.salinity_name_nc, 8, 3)
        grid_layout.addWidget(self.salinity_flag_nc, 8, 4)
        grid_layout.addWidget(self.salinity_res, 8, 5)

        grid_layout.addWidget(oxygen_label, 9, 0)
        grid_layout.addWidget(self.oxygen_name_csv, 9, 1)
        grid_layout.addWidget(self.oxygen_flag_csv, 9, 2)
        grid_layout.addWidget(self.oxygen_name_nc, 9, 3)
        grid_layout.addWidget(self.oxygen_flag_nc, 9, 4)
        grid_layout.addWidget(self.oxygen_res, 9, 5)

        grid_layout.addWidget(nitrate_label, 10, 0)
        grid_layout.addWidget(self.nitrate_name_csv, 10, 1)
        grid_layout.addWidget(self.nitrate_flag_csv, 10, 2)
        grid_layout.addWidget(self.nitrate_name_nc, 10, 3)
        grid_layout.addWidget(self.nitrate_flag_nc, 10, 4)
        grid_layout.addWidget(self.nitrate_res, 10, 5)

        grid_layout.addWidget(phosphate_label, 11, 0)
        grid_layout.addWidget(self.phosphate_name_csv, 11, 1)
        grid_layout.addWidget(self.phosphate_flag_csv, 11, 2)
        grid_layout.addWidget(self.phosphate_name_nc, 11, 3)
        grid_layout.addWidget(self.phosphate_flag_nc, 11, 4)
        grid_layout.addWidget(self.phosphate_res, 11, 5)

        grid_layout.addWidget(silicate_label, 12, 0)
        grid_layout.addWidget(self.silicate_name_csv, 12, 1)
        grid_layout.addWidget(self.silicate_flag_csv, 12, 2)
        grid_layout.addWidget(self.silicate_name_nc, 12, 3)
        grid_layout.addWidget(self.silicate_flag_nc, 12, 4)
        grid_layout.addWidget(self.silicate_res, 12, 5)

        grid_layout.addWidget(nitrite_label, 13, 0)
        grid_layout.addWidget(self.nitrite_name_csv, 13, 1)
        grid_layout.addWidget(self.nitrite_flag_csv, 13, 2)
        grid_layout.addWidget(self.nitrite_name_nc, 13, 3)
        grid_layout.addWidget(self.nitrite_flag_nc, 13, 4)

        grid_layout.addWidget(self.nitrite_res, 13, 5)

        grid_layout.addWidget(ammonia_label, 14, 0)
        grid_layout.addWidget(self.ammonia_name_csv, 14, 1)
        grid_layout.addWidget(self.ammonia_flag_csv, 14, 2)
        grid_layout.addWidget(self.ammonia_name_nc, 14, 3)
        grid_layout.addWidget(self.ammonia_flag_nc, 14, 4)
        grid_layout.addWidget(self.ammonia_res, 14, 5)

        grid_layout.addWidget(linesep2, 15, 0, 1, 6)

        grid_layout.addWidget(self.process_table, 16, 1, 1, 2)
        grid_layout.addWidget(self.process_csv, 16, 3, 1, 2)

        self.centralWidget().setLayout(grid_layout)

        self.show()

    def diff_csv(self):

        try:
            differences = self.proc_differences()

            csv_savepath = QFileDialog.getSaveFileName(self, 'Save File', '.csv')

            temp = []

            for x in range(13):
                for y in differences[x]:
                    y.append(x)
                    temp.append(y)

            print(temp)

            temp = sorted(temp, key=lambda t: (t[0], t[1]))

            print(temp)

            header_row = ['Deployment', 'RP', 'Salinity', '', '', 'Salinity Flag', '', '', 'Oxygen', '', '',
                          'Oxygen Flag', '', '', 'Nitrate', '', '', 'Nitrate Flag', '', '',
                          'Phosphate', '', '', 'Phosphate Flag', '', '', 'Silicate', '', '', 'Silicate Flag', '',
                          '', 'Nitrite', '', '', 'Nitrite Flag', '', '', 'Ammonia', '', '', 'Ammonia Flag', '', '']
            subheader_row = ['', '', 'CSV', 'NC', 'Diff', 'CSV', 'NC', 'Diff', 'CSV', 'NC', 'Diff', 'CSV', 'NC', 'Diff',
                             'CSV', 'NC', 'Diff', 'CSV', 'NC', 'Diff', 'CSV', 'NC', 'Diff', 'CSV', 'NC', 'Diff',
                             'CSV', 'NC', 'Diff', 'CSV', 'NC', 'Diff', 'CSV', 'NC', 'Diff', 'CSV', 'NC', 'Diff',
                             'CSV', 'NC', 'Diff']
            with open(csv_savepath[0], 'w+', newline='') as file:
                write = csv.writer(file)

                write.writerow(header_row)
                write.writerow(subheader_row)

                write_string = ['' for x in header_row]

                for i, row in enumerate(temp):
                    if i > 0:
                        # Uses index 5 of row to get the column number
                        if row[0] == temp[i - 1][0] and row[1] == temp[i - 1][1]:
                            write_string[int(3 * (row[5]) + 2)] = row[2]
                            write_string[int(1 + (3 * (row[5])) + 2)] = row[3]
                            write_string[int(2 + (3 * (row[5])) + 2)] = row[4]
                        else:
                            write_string[0] = row[0]
                            write_string[1] = row[1]
                            write_string[int(3 * (row[5]) + 2)] = row[2] 
                            write_string[int(1 + (3 * (row[5])) + 2)] = row[3]
                            write_string[int(2 + (3 * (row[5])) + 2)] = row[4]
                            write.writerow(write_string)
                            write_string = ['' for row in header_row]
                    try:
                        if row[0] != temp[i+1][0]:

                            write.writerow([''])
                    except IndexError:
                        continue

        except Exception:

            print(traceback.print_exc())

    def diff_table(self):

        differences = self.proc_differences()

        # Open the table view and shoot all the data into it
        self.view_dat = view_Data(differences[0], differences[1], differences[2], differences[3], differences[4],
                                  differences[5], differences[6], differences[7], differences[8], differences[9],
                                  differences[10], differences[11], differences[12], differences[13])
        self.view_dat.show()

    def proc_differences(self):
        try:
            csv_path = self.csv_path.text()
            nc_path = self.nc_path.text()

            if os.path.exists(csv_path) and os.path.isdir(nc_path):
                # Pull out all the entered header names from the line edits and put into lists
                csv_entered_names = [getattr(self, "{}".format(x)).text() for x in self.csv_line_edits]
                nc_entered_names = [getattr(self, "{}".format(x)).text() for x in self.nc_line_edits]
                res_entered = [getattr(self, "{}".format(x)).text() for x in self.resolutions]

                # Read csv file in
                csv_file = pd.read_csv(csv_path, skiprows=1)

                # Check if headers present as first or second row changes depending on HyPro version
                try:
                    test = csv_file.loc[csv_file['Deployment'] == 1]
                except KeyError:
                    csv_file = pd.read_csv(csv_path)

                nc_files = os.listdir(nc_path)

                # Loop through the different deployments and then subset the dataframe
                for dep in set(csv_file['Deployment']):
                    csv_subset = csv_file[csv_file['Deployment'] == dep]
                    csv_subset = csv_subset.sort_values(by='RP')
                    # Loop through all files in the folder provided and then open the NC that matches the deployment
                    # The matched nc file is opened and the rosette positions are extracted to sort the data by
                    # as data in the NC file is not always sorted 1-24 RP...
                    # The header names that are entered are then looped through and used to pull out the relevant data
                    # which is then compared between the NC and CSV

                    for nc in nc_files:
                        if nc[-2:] == 'nc' and int(nc[-6:-3]) == dep:
                            matched_nc = Dataset(nc_path + '/' + nc)
                            ros_pos = matched_nc.variables['rosettePosition'][0, 0, :, 0][:]

                            for header_count, csv_header in enumerate(csv_entered_names):
                                try:
                                    resolution_index = header_count / 2
                                    # Extract the correct NC variable to match and then make sure it is sorted correctly
                                    curr_nc_variable = matched_nc.variables[nc_entered_names[header_count]][0, 0, :, 0][:]
                                    curr_nc_variable = [x for _, x in sorted(zip(ros_pos, curr_nc_variable))]

                                    for value_index, nc_value in enumerate(curr_nc_variable):
                                        if header_count % 2 == 0:
                                            difference = abs(csv_subset[csv_header].iloc[value_index] - nc_value)
                                            # Concentration comparison as every even is concentration comparison
                                            if difference > float(res_entered[int(resolution_index)]):
                                                self.diffs[header_count].append(
                                                    [dep, (value_index + 1), csv_subset[csv_header].iloc[value_index],
                                                     nc_value, difference])
                                        else:
                                            difference = str(csv_subset[csv_header].iloc[value_index]) + ' | ' + str(
                                                nc_value)
                                            # Flag comparison as every odd value of header_count is looking at flags
                                            # Disregard CSV values that have NaN flag, if real should have numbered flag
                                            if nc_value != csv_subset[csv_header].iloc[value_index]:
                                                if not pd.isna(csv_subset[csv_header].iloc[value_index]):
                                                    self.diffs[header_count].append([dep, (value_index + 1),
                                                                                     csv_subset[csv_header].iloc[
                                                                                         value_index], nc_value,
                                                                                     difference])

                                except KeyError as e:
                                    continue

                return self.diffs

        except Exception as e:
            print(traceback.print_exc())

    def loadcsv(self):
        if os.path.exists(self.csv_path.text()):
            csv_df = pd.read_csv(self.csv_path.text())
        return csv_df

    def browsecsv(self):
        path = QFileDialog.Options()
        files = QFileDialog.getOpenFileName(self, "Select CSV", 'c://', "csv (*.csv)")
        if os.path.exists(files[0]):
            self.csv_path.setText(files[0])

    def browsenc(self):
        path = QFileDialog.Options()
        files = QFileDialog.getExistingDirectory(self, "Select Folder containing NC files")
        if os.path.exists(files):
            self.nc_path.setText(files)


class view_Data(QWidget):

    def __init__(self, salinity, salinity_flag, oxygen, oxygen_flag, nitrate, nitrate_flag, phosphate, phosphate_flag,
                 silicate, silicate_flag, nitrite, nitrite_flag, ammonia, ammonia_flag):
        super().__init__()
        self.setWindowIcon(QIcon(':/assets/icon.svg'))
        self.setFont(QFont('Segoe UI'))

        self.salinity = salinity
        self.salinity_flag = salinity_flag
        self.oxygen = oxygen
        self.oxygen_flag = oxygen_flag
        self.nitrate = nitrate
        self.nitrate_flag = nitrate_flag
        self.phosphate = phosphate
        self.phosphate_flag = phosphate_flag
        self.silicate = silicate
        self.silicate_flag = silicate_flag
        self.nitrite = nitrite
        self.nitrite_flag = nitrite_flag
        self.ammonia = ammonia
        self.ammonia_flag = ammonia_flag

        self.tabs = ['salinity', 'salinity_flag', 'oxygen', 'oxygen_flag', 'nitrate', 'nitrate_flag', 'phosphate',
                     'phosphate_flag', 'silicate', 'silicate_flag', 'nitrite', 'nitrite_flag', 'ammonia',
                     'ammonia_flag']

        self.init_ui()

        self.setStyleSheet('''
             QLabel {
                 font: 14px;
             }   
             QListWidget {

                 font: 14px;
             }
             QTableWidget {
                 font: 14px;
             }
             QTabWidget {
                font: 14px;
             }
             ''')

    def init_ui(self):

        self.setGeometry(0, 0, 700, 600)
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.setWindowTitle('NC Check Output')

        self.gridlayout = QGridLayout()
        self.gridlayout.setSpacing(5)

        self.output_tabs = QTabWidget()

        self.gridlayout.addWidget(self.output_tabs, 0, 0)

        self.salinity_tab = QWidget()
        self.output_tabs.addTab(self.salinity_tab, 'Salinity')
        self.salinity_tab.layout = QVBoxLayout()
        self.salinity_table = QTableWidget()

        self.salinity_flag_tab = QWidget()
        self.output_tabs.addTab(self.salinity_flag_tab, 'Salinity Flag')
        self.salinity_flag_tab.layout = QVBoxLayout()
        self.salinity_flag_table = QTableWidget()

        self.oxygen_tab = QWidget()
        self.output_tabs.addTab(self.oxygen_tab, 'Oxygen')
        self.oxygen_tab.layout = QVBoxLayout()
        self.oxygen_table = QTableWidget()

        self.oxygen_flag_tab = QWidget()
        self.output_tabs.addTab(self.oxygen_flag_tab, 'Oxygen Flag')
        self.oxygen_flag_tab.layout = QVBoxLayout()
        self.oxygen_flag_table = QTableWidget()

        self.nitrate_tab = QWidget()
        self.output_tabs.addTab(self.nitrate_tab, 'Nitrate')
        self.nitrate_tab.layout = QVBoxLayout()
        self.nitrate_table = QTableWidget()

        self.nitrate_flag_tab = QWidget()
        self.output_tabs.addTab(self.nitrate_flag_tab, 'Nitrate Flag')
        self.nitrate_flag_tab.layout = QVBoxLayout()
        self.nitrate_flag_table = QTableWidget()

        self.phosphate_tab = QWidget()
        self.output_tabs.addTab(self.phosphate_tab, 'Phosphate')
        self.phosphate_tab.layout = QVBoxLayout()
        self.phosphate_table = QTableWidget()

        self.phosphate_flag_tab = QWidget()
        self.output_tabs.addTab(self.phosphate_flag_tab, 'Phosphate Flag')
        self.phosphate_flag_tab.layout = QVBoxLayout()
        self.phosphate_flag_table = QTableWidget()

        self.silicate_tab = QWidget()
        self.output_tabs.addTab(self.silicate_tab, 'Silicate')
        self.silicate_tab.layout = QVBoxLayout()
        self.silicate_table = QTableWidget()

        self.silicate_flag_tab = QWidget()
        self.output_tabs.addTab(self.silicate_flag_tab, 'Silicate Flag')
        self.silicate_flag_tab.layout = QVBoxLayout()
        self.silicate_flag_table = QTableWidget()

        self.ammonia_tab = QWidget()
        self.output_tabs.addTab(self.ammonia_tab, 'Ammonia')
        self.ammonia_tab.layout = QVBoxLayout()
        self.ammonia_table = QTableWidget()

        self.ammonia_flag_tab = QWidget()
        self.output_tabs.addTab(self.ammonia_flag_tab, 'Ammonia Flag')
        self.ammonia_flag_tab.layout = QVBoxLayout()
        self.ammonia_flag_table = QTableWidget()

        self.nitrite_tab = QWidget()
        self.output_tabs.addTab(self.nitrite_tab, 'Nitrite')
        self.nitrite_tab.layout = QVBoxLayout()
        self.nitrite_table = QTableWidget()

        self.nitrite_flag_tab = QWidget()
        self.output_tabs.addTab(self.nitrite_flag_tab, 'Nitrite Flag')
        self.nitrite_flag_tab.layout = QVBoxLayout()
        self.nitrite_flag_table = QTableWidget()

        for x in self.tabs:
            getattr(self, "{}".format(x + str('_tab'))).layout.addWidget(getattr(self, "{}".format(x + str('_table'))))
            getattr(self, "{}".format(x + str('_tab'))).setLayout(getattr(self, "{}".format(x + str('_tab'))).layout)
            getattr(self, "{}".format(x + str('_table'))).setRowCount(len(getattr(self, "{}".format(x))))
            getattr(self, "{}".format(x + str('_table'))).setColumnCount(5)

        self.setLayout(self.gridlayout)

        self.fill_tables()

    def fill_tables(self):

        for x in self.tabs:
            getattr(self, "{}".format(x + str('_table'))).setHorizontalHeaderLabels(
                ['Deployment', 'RP', 'CSV', 'NC', 'Diff'])

            for row, y in enumerate(getattr(self, "{}".format(x))):
                for col, z in enumerate(y):
                    getattr(self, "{}".format(x + str('_table'))).setItem(row, col, QTableWidgetItem(str(z)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NC_check_main()
    sys.exit(app.exec_())
