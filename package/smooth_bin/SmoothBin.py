from PyQt5.QtWidgets import (QMainWindow, QWidget, QGridLayout, QApplication, QLabel, QPushButton, QLineEdit, QFrame,
                             QComboBox, QFileDialog)
from PyQt5.QtGui import QIcon, QFont
import pandas as pd
import os
import statistics
import sys
import hyproicons


class SmoothBinner(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(':/assets/2dropsshadow.svg'))
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.file_path = ""
        self.output_path = ""

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
                    font: 14px;
                }
                ''')

    def init_ui(self):
        self.setFont(QFont('Segoe UI'))

        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        self.setGeometry(0, 0, 450, 350)
        qtRectangle = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.setWindowTitle('Smooth and Bin Data')

        file_select_label = QLabel('<b>Select a .csv file:</b>')
        self.file_path_lineedit = QLineEdit()
        self.file_path_lineedit.setReadOnly(True)
        file_path_button = QPushButton('Browse')
        file_path_button.clicked.connect(self.browse_file)

        linesep1 = QFrame()
        linesep1.setFrameShape(QFrame.HLine)
        linesep1.setFrameShadow(QFrame.Sunken)

        output_file_label = QLabel('<b>Output file location:</b>')
        self.output_file_lineedit = QLineEdit()
        self.output_file_lineedit.setReadOnly(True)
        output_file_button = QPushButton('Browse')
        output_file_button.clicked.connect(self.browse_output)

        linesep2 = QFrame()
        linesep2.setFrameShape(QFrame.HLine)
        linesep2.setFrameShadow(QFrame.Sunken)

        smoothing_method_label = QLabel('Smoothing method:')
        self.smoothing_method_combo = QComboBox()
        self.smoothing_method_combo.addItems(['Median', 'Average'])

        calculate_button = QPushButton('Calculate')
        calculate_button.clicked.connect(self.calculate_function)

        output_label = QLabel('Output:')

        self.output = QLineEdit()
        self.output.setReadOnly(True)

        grid_layout.addWidget(file_select_label, 0, 0, 1, 2)
        grid_layout.addWidget(self.file_path_lineedit, 1, 0, 1, 2)
        grid_layout.addWidget(file_path_button, 2, 1, 1, 1)
        grid_layout.addWidget(linesep1, 3, 0, 1, 2)

        grid_layout.addWidget(output_file_label, 4, 0, 1, 2)
        grid_layout.addWidget(self.output_file_lineedit, 5, 0, 1, 2)
        grid_layout.addWidget(output_file_button, 6, 1, 1, 1)
        grid_layout.addWidget(linesep2, 7, 0, 1, 2)

        grid_layout.addWidget(smoothing_method_label, 8, 0, 1, 1)
        grid_layout.addWidget(self.smoothing_method_combo, 8, 1, 1, 1)

        grid_layout.addWidget(calculate_button, 10, 0, 1, 2)

        grid_layout.addWidget(output_label, 11, 0, 1, 2)
        grid_layout.addWidget(self.output, 12, 0, 1, 2)

        self.centralWidget().setLayout(grid_layout)

        self.show()

    def browse_file(self):
        """
        Allows the user to navigate to a folder so the file can be saved
        """
        file_path = str(QFileDialog.getOpenFileUrl(self, 'Select File')[0].path())
        if os.path.isfile(file_path[1:]):
            self.file_path_lineedit.setText(file_path[1:])
            self.file_path = file_path[1:]

    def browse_output(self):
        """
        Allows the use to create a file for saving to
        """
        file_path = str(QFileDialog.getSaveFileUrl(self, 'Save File', 'c:\\', "CSV file (*.csv)")[0].path())
        self.output_file_lineedit.setText(file_path)
        self.output_path = file_path[1:]


    def calculate_function(self):
        """
        Runs the calculation function to reduce the dataset into 1 second bins and also applies some smoothin
        :return:
        """

        smooth_type = self.smoothing_method_combo.currentText()

        # Create the file
        try:
            f = open(self.output_path, "a")
            f.write('signal, time \n')
            f.close()
        except Exception as e:
            print(e)

        # Check if the files DO exist first
        if os.path.exists(self.file_path) and os.path.isfile(self.output_path):

            # Pull in the data that needs to be binned and smoothed.
            in_df = pd.read_csv(self.file_path, dtype={'time': 'float'})

            # If the columns are present then we can proceed
            if ('time' in in_df.columns) and ('signal' in in_df.columns):

                time = in_df['time']
                signal = in_df['signal']

                smoothed_signal = self.smooth(signal, smooth_type)

                signal_bins = []
                time_bins = []
                appending_count = 1
                creating_measurement = True

                f = open(self.output_path, "a")

                for i, x in enumerate(time):

                    if creating_measurement:
                        # This is the start of every subset
                        start_time = x
                        start_index = i
                        creating_measurement = False
                    else:
                        # Add to the subset and check if we are getting close to a second
                        end_time = x
                        end_index = i
                        if (end_time - start_time) > 0.76:
                            signal_subset = smoothed_signal[start_index: end_index]
                            signal_subset_median = statistics.median(signal_subset)

                            signal_bins.append(signal_subset_median)
                            time_bins.append(end_time)

                            creating_measurement = True

                            f.write(f'{appending_count}, {signal_subset_median}, {end_time} \n')
                            appending_count = appending_count + 1
                f.close()

                self.output.setText('Successfully created binned file')

            else:
                self.output.setText('CSV does not match expected format')

        else:
            self.output.setText('Paths do not exist!')


    def smooth(self, signal, type):
        """
        Smooths the signal with either a median or average
        :param signal: list
        :param type: str
        :return: list
        """
        smoothed_signal = []
        temp_subset = []
        for i, x in enumerate(signal):
            temp_subset.append(x)
            if i < 5:
                smoothed_signal.append(x)
            if i > 5:
                if type == 'Median':
                    smoothed_signal.append(statistics.median(temp_subset))
                elif type == 'Average':
                    smoothed_signal.append(statistics.mean(temp_subset))
                temp_subset.pop(0)
        return smoothed_signal


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SmoothBinner()
    sys.exit(app.exec_())
