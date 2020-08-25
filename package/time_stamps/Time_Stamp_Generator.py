from PyQt5.QtWidgets import (QMainWindow, QWidget, QGridLayout, QDesktopWidget, QLabel, QPushButton, QLineEdit,
                             QApplication, QFileDialog, QMessageBox)
from PyQt5.QtGui import QIcon, QFont
import sys, time, calendar, csv
import hyproicons

# Generates a series of timestamps for a nutrient run, uses simple UI for the required fields. Includes user
# input validation so no errors are raised, instead produces error messages for user to correct mistakes

class TimeStamps(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(':/assets/icon.svg'))
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

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
        # Initialise all the GUI elements and place them in a pretty grid, force Segoe UI as font because I like it.
        self.setFont(QFont('Segoe UI'))

        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        self.setGeometry(0, 0, 440, 455)
        qtRectangle = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.setWindowTitle('Generate Time Stamps')

        stamp_format_label = QLabel('Time Stamp Format: ')
        self.stamp_format = QLineEdit('%d/%m/%Y %I:%M:%S %p')
        self.stamp_format.setToolTip('This is the format to match AACE - only change if necessary')

        start_time_label = QLabel('Start Time:')
        self.start_time = QLineEdit('e.g. 27/09/2019 03:10:00 PM')

        length_label = QLabel('Number of stamps:')
        self.length = QLineEdit(self)

        spacing_label = QLabel('Spacing (sample period):')
        self.spacing = QLineEdit(self)

        path_label = QLabel('Output path:')
        self.path = QLineEdit(self)

        path_browse = QPushButton('Browse')
        path_browse.clicked.connect(self.browse_path)

        generate = QPushButton('Generate')
        generate.clicked.connect(self.user_input_validation)

        grid_layout.addWidget(stamp_format_label, 0, 0)
        grid_layout.addWidget(self.stamp_format, 0, 1)

        grid_layout.addWidget(start_time_label, 1, 0)
        grid_layout.addWidget(self.start_time, 1, 1)

        grid_layout.addWidget(length_label, 2, 0)
        grid_layout.addWidget(self.length, 2, 1)

        grid_layout.addWidget(spacing_label, 3, 0)
        grid_layout.addWidget(self.spacing, 3, 1)

        grid_layout.addWidget(path_label, 4, 0)
        grid_layout.addWidget(self.path, 4, 1)
        grid_layout.addWidget(path_browse, 5, 1)

        grid_layout.addWidget(generate, 6, 0, 1, 2)

        self.centralWidget().setLayout(grid_layout)

        self.show()


    def browse_path(self):
        # Allows the user to browse for a file path and create a new file to save the output to, sets the
        # output path line to read only so it cannot be changed unless a new path is browsed for
        path = QFileDialog.Options()
        files = QFileDialog.getSaveFileName(self, "Save File", 'c://', "csv (*.csv)")
        if files:
            self.path.setText(files[0])
            self.path.setReadOnly(True)

    def validate_time_format(self, format):
        # Check whether the inputted time format is usable
        current_time = time.time()
        try:
            convert_time = time.strftime(format, time.gmtime(current_time))
            return True
        except ValueError:

            return False


    def validate_time_start(self, format, start_time):
        # Check whether the start time matches the expected format, if not a message box error is
        # pushed to alert the user
        try:
            struc_time = time.strptime(start_time, format)
            epoch_time = calendar.timegm(struc_time)
            return epoch_time

        except ValueError:
            messagebox = QMessageBox(QMessageBox.Information, 'Error',
                                     "Start time does not match format, please refer to "
                                     "<a href='https://docs.python.org/3/library/time.html#time.strftime'>here</a>"
                                     " for how a time string functions and what it is expecting.",
                                     buttons=QMessageBox.Ok, parent=self)
            messagebox.exec_()
            return False

    def validate_stamp_number(self, length):
        # Check if the number of stamps required is a whole number otherwise push a error message to user
        try:
            length_number = int(length)
            return length_number

        except ValueError:
            messagebox = QMessageBox(QMessageBox.Information, 'Error',
                                     "A whole number was not entered as the number of time stamps required.",
                                     buttons=QMessageBox.Ok, parent=self)
            messagebox.exec_()
            return False

    def validate_spacing(self, spacing):
        # Check if the spacing number in seconds is a whole number otherwise push an error message to the user
        try:
            spacing_number = int(spacing)
            return spacing_number
        except ValueError:
            messagebox = QMessageBox(QMessageBox.Information, 'Error',
                                     "A whole number was not entered as the spacing of time stamps. This is the spacing"
                                     " in seconds. ",
                                     buttons=QMessageBox.Ok, parent=self)
            messagebox.exec_()
            return False


    def user_input_validation(self):
        # Grab all the user input fields
        stamp_format = self.stamp_format.text()
        start_time = self.start_time.text()
        number = self.length.text()
        spacing = self.spacing.text()

        # Run through each and check if it is acceptable - if it all matches continue to generate the stamps
        if self.validate_time_format(stamp_format):
            epoch_time = self.validate_time_start(stamp_format, start_time)
            if epoch_time:
                length_int = self.validate_stamp_number(number)
                if length_int:
                    spacing_int = self.validate_spacing(spacing)
                    if spacing_int:
                        self.generate_stamps(epoch_time, stamp_format, length_int, spacing_int)


    def generate_stamps(self, epoch_start, format, length, spacing):
        # Loops the range of the length, multiples each number by the spacing and adds it to the starting time
        # Appends formatted strings to a list and passes along for saving
        time_strings = []
        for x in range(length):
            temp_time = epoch_start + (x * spacing)
            struct_time = time.gmtime(temp_time)
            utc_time = time.strftime(format, struct_time)
            time_strings.append(utc_time)

        self.save_stamps(time_strings)

    def save_stamps(self, time_strings):
        # Saves each time stamp string as a row in a .csv file, raises an error message if the path is non existant
        if self.path.text() != '':
            with open(self.path.text(), 'w+', newline='') as file:
                writer = csv.writer(file)

                for x in time_strings:
                    writer.writerow([x])

            print('Completed')
        else:
            messagebox = QMessageBox(QMessageBox.Information, 'Error',
                                     "A path was not supplied, please use the browse button so pick a spot to save the "
                                     "output file. ",
                                     buttons=QMessageBox.Ok, parent=self)
            messagebox.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TimeStamps()
    sys.exit(app.exec_())