import sys
from time import sleep
from package import fix_qt_import_error
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QGridLayout, QLabel, QPushButton,
                             QFrame, QHBoxLayout)
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt

from package.oxygen import DOCalculator
from package.qc_reader import QCReader
from package.data_qc import DataQC
from package.nut_stat_plot import NutrientStatPlotter
from package.io_norm import IO3Norm
from package.time_stamps import Time_Stamp_Generator
from package.nc_checker import NC_Checker_Main
from package.glass_cal import GlassCal
from package.smooth_bin import SmoothBin

import hyproicons

class KenWareMain(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(':/assets/icon.svg'))
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.init_ui()

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f4f8ff;
                border: 0px;
                alpha: 0;
            }
            QFrame[bg=true] {
                background-color: #f4f8ff;
                border: 5px solid #4e546c;
                border-radius: 30px;
            }
            
            QFrame[headerframe=true] {
                background-color: #4e546c;
                border-radius: 10px;
            }
            QLabel[headertext=true] {
                font: 17px;
                color: #ffffff;
                font-weight: bold;
            }
            QLabel {
                font: 15px;
                font-weight: bold;
            }
            QFrame[bodyframe=true] {
                background-color: #f4f8ff;
                border-radius: 10px;
                padding-top: 10px;
            }
            QPushButton {
                font: 15px;
                border: 1px solid #ededed;
                background: #ededed;
                border-radius:5px;
            }
            QPushButton:hover {
                color: #222222;
                border: 1px solid #8f98a8;
                background: #f7f7f7;
            }
            QPushButton:pressed {
                background-color: #e8e8e8;
                border: 1px solid #8f98a8;
                border-style: inset;
            }
            QPushButton[close=true] {
                font: 16px;
                border: 0px solid;
                background-color: none;   
            }
            QPushButton[close=true]:hover {
                background-color: #d9d9d9;
                border-radius: 5px;
            }
            QPushButton[close=true]:pressed {
                font-weight: bold;
                border-style: inset;pip   
            }
                            """)

    def init_ui(self):
        self.setFont(QFont('Segoe UI'))

        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        self.setGeometry(0, 0, 400, 600)
        qtRectangle = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle('Hydro Apps')
        self.showNormal()

        x_close = QPushButton(' x ')
        x_close.setProperty('close', True)
        x_close.setFont(QFont('Verdana'))
        x_close.clicked.connect(self.close_app)
        x_close.setToolTip('Close')

        minimise = QPushButton(' - ')
        minimise.setProperty('close', True)
        minimise.setFont(QFont('Verdana'))
        minimise.clicked.connect(self.min_app)
        minimise.setToolTip('Minimise')

        header_logo = QLabel()
        header_logo.setPixmap(QPixmap(':/assets/2dropsshadow.ico').scaled(32, 32, Qt.KeepAspectRatio))

        header_label = QLabel('    Hydro Applications')
        header_label.setProperty('headertext', True)
        header_frame = QFrame()
        header_frame.setProperty('headerframe', True)

        docalc_label = QLabel('DO Calculator')
        docalc_launch = QPushButton('Launch DO Calc')
        docalc_launch.clicked.connect(self.open_docalc)
        docalc_label.setToolTip('The DO Calculator can reprocess results and format the results for HyLIMS upload.')

        linesep1 = QFrame()
        linesep1.setFrameShape(QFrame.HLine)
        linesep1.setFrameShadow(QFrame.Sunken)

        dataqc_label = QLabel('Hydrology Data QCer')
        dataqc_launch = QPushButton('Launch QCer')
        dataqc_launch.clicked.connect(self.open_dataqc)

        linesep2 = QFrame()
        linesep2.setFrameShape(QFrame.HLine)
        linesep2.setFrameShadow(QFrame.Sunken)

        qctable_label = QLabel('QC Table Stats')
        qctable_launch = QPushButton('Launch QCTab Stats')
        qctable_launch.clicked.connect(self.open_qctable)
        qctable_launch.setFixedWidth(160)

        baseline_label = QLabel('Base Offset Plotter')
        baseline_launch = QPushButton('Launch BO Plotter')
        baseline_launch.clicked.connect(self.open_boplot)

        iodate_label = QLabel('Analyte Normality')
        iodate_launch = QPushButton('Launch Analyte Norm')
        iodate_launch.clicked.connect(self.open_ionorm)

        glasscal_label = QLabel('Glass Calibration')
        glasscal_launch = QPushButton('Launch Glass Cal')
        glasscal_launch.clicked.connect(self.open_glasscal)

        nccheck_label = QLabel('NC Checker')
        nccheck_launch = QPushButton('Launch NC Checker')
        nccheck_launch.clicked.connect(self.open_nccheck)

        time_stamp_label = QLabel('SLK Time Stamps')
        time_stamp_launch = QPushButton('Launch Stamp Gen')
        time_stamp_launch.clicked.connect(self.open_time_gen)

        smooth_bin_label = QLabel('Smooth Bins')
        smooth_bin_launch = QPushButton('Launch Smooth Bins')
        smooth_bin_launch.clicked.connect(self.open_smooth_bin)

        linesep3 = QFrame()
        linesep3.setFrameShape(QFrame.HLine)
        linesep3.setFrameShadow(QFrame.Sunken)

        linesep4 = QFrame()
        linesep4.setFrameShape(QFrame.HLine)
        linesep4.setFrameShadow(QFrame.Sunken)

        linesep5 = QFrame()
        linesep5.setFrameShape(QFrame.HLine)
        linesep5.setFrameShadow(QFrame.Sunken)

        linesep6 = QFrame()
        linesep6.setFrameShape(QFrame.HLine)
        linesep6.setFrameShadow(QFrame.Sunken)

        linesep7 = QFrame()
        linesep7.setFrameShape(QFrame.HLine)
        linesep7.setFrameShadow(QFrame.Sunken)

        linesep8 = QFrame()
        linesep8.setFrameShape(QFrame.HLine)
        linesep8.setFrameShadow(QFrame.Sunken)

        window_surround = QFrame()
        window_surround.setProperty('bg', True)

        close = QPushButton('Close')
        close.clicked.connect(self.close_app)
        close.setFixedWidth(125)

        grid_layout.addWidget(window_surround, 0, 0, 22, 4)
        grid_layout.addWidget(header_frame, 1, 1, 2, 2)
        grid_layout.addWidget(header_logo, 1, 1, 2, 1, Qt.AlignHCenter)
        grid_layout.addWidget(header_label, 1, 1, 2, 2, Qt.AlignHCenter)
        #grid_layout.addWidget(body_frame, 1, 0, 5, 2)
        grid_layout.addWidget(docalc_label, 4, 1)
        grid_layout.addWidget(docalc_launch, 4, 2)
        grid_layout.addWidget(linesep1, 5, 1, 1, 2)
        grid_layout.addWidget(qctable_label, 6, 1)
        grid_layout.addWidget(qctable_launch, 6, 2)
        grid_layout.addWidget(linesep2, 7, 1, 1, 2)
        grid_layout.addWidget(dataqc_label, 8, 1)
        grid_layout.addWidget(dataqc_launch, 8, 2)
        grid_layout.addWidget(linesep3, 9, 1, 1, 2)
        grid_layout.addWidget(baseline_label, 10, 1)
        grid_layout.addWidget(baseline_launch, 10, 2)
        grid_layout.addWidget(linesep4, 11, 1, 1, 2)
        grid_layout.addWidget(iodate_label, 12, 1)
        grid_layout.addWidget(iodate_launch, 12, 2)
        grid_layout.addWidget(linesep5, 13, 1, 1, 2)
        grid_layout.addWidget(glasscal_label, 14, 1)
        grid_layout.addWidget(glasscal_launch, 14, 2)
        grid_layout.addWidget(linesep6, 15, 1, 1, 2)
        grid_layout.addWidget(nccheck_label, 16, 1)
        grid_layout.addWidget(nccheck_launch, 16, 2)
        grid_layout.addWidget(linesep7, 17, 1, 1, 2)
        grid_layout.addWidget(time_stamp_label, 18, 1)
        grid_layout.addWidget(time_stamp_launch, 18, 2)
        grid_layout.addWidget(linesep8, 19, 1, 1, 2)
        grid_layout.addWidget(smooth_bin_label, 20, 1)
        grid_layout.addWidget(smooth_bin_launch, 20, 2)
        #grid_layout.addWidget(close, 15, 1, 1, 2, Qt.AlignHCenter)

        dialog_buttons_layout = QHBoxLayout()

        grid_layout.addLayout(dialog_buttons_layout, 0, 2, Qt.AlignBottom | Qt.AlignRight)

        dialog_buttons_layout.addWidget(minimise)
        dialog_buttons_layout.addWidget(x_close)

        #grid_layout.addWidget(x_close, 0, 3, Qt.AlignLeft | Qt.AlignBottom)
        #grid_layout.addWidget(__min, 0, 2, Qt.AlignLeft | Qt.AlignBottom)
        self.centralWidget().setLayout(grid_layout)

        self.show()

    def open_boplot(self):
        self.bo_plot = NutrientStatPlotter.NutrientStatPlotter()
        sleep(0.3)

    def open_docalc(self):
        self.do_calc = DOCalculator.Mainmenu()
        sleep(0.3)

    def open_qctable(self):
        self.qc_table = QCReader.qcReaderMain()
        sleep(0.3)

    def open_dataqc(self):
        self.dat_qc = DataQC.Dataqc()
        sleep(0.3)

    def open_ionorm(self):
        self.io_norm = IO3Norm.IodateNorm()
        sleep(0.3)

    def open_glasscal(self):
        self.g_cal = GlassCal.GlassCalMain()
        sleep(0.3)

    def open_nccheck(self):
        self.nc_check = NC_Checker_Main.NC_check_main()
        sleep(0.3)

    def open_time_gen(self):
        self.time_gen = Time_Stamp_Generator.TimeStamps()
        sleep(0.3)

    def open_smooth_bin(self):
        self.smooth_bin = SmoothBin.SmoothBinner()
        sleep(0.3)

    def close_app(self):
        self.close()

    def min_app(self):
        self.showMinimized()

    # Reimplement dragging of window as with no title bar it doesn't exist
    def mousePressEvent(self, event, *args, **kwargs):
        if event.buttons() == Qt.LeftButton:
            self.drag_pos = event.globalPos()

    def mouseMoveEvent(self, event, *args, **kwargs):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.drag_pos)
            self.drag_pos = event.globalPos()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = KenWareMain()
    sys.exit(app.exec_())
