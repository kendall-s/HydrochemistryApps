
from PyQt5.QtWidgets import (QMainWindow, QWidget, QGridLayout, QApplication, QLabel, QPushButton, QLineEdit, QFrame)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
import traceback
from decimal import Decimal
import sys

# Based off of she384 IO3Norm Python re-write
# Equations are derived from excel spreadsheet circa 2005 used by Hydrochemistry
# References to equations are given, slight differences in calculations may be seen due to
# constant values which could differ.

# Created on the 14 of July 2020 to replace the DOS program Glasscalm intergrating into the Hydrochemistry apps suite

AIR_DENSITY = 0.0012 # g/cm3 - General density of air
CALIBRATED_WEIGHT_DENSITY = 8.36  # g/cm3 - Density of weights to calibrate balance

class GlassCalMain(QMainWindow):

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
        self.setFont(QFont('Segoe UI'))

        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        self.setGeometry(0, 0, 450, 350)
        qtRectangle = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.setWindowTitle('Calculate Flask Volume')

        measured_weight_label = QLabel('Water Weight (g):')
        self.measured_weight = QLineEdit(self)

        temperature_label = QLabel('Temperature of solution when weighed (°C):')
        self.temperature = QLineEdit(self)

        air_density_label = QLabel('Air Density (g/cm3):')
        self.air_density = QLineEdit('0.0012')

        balance_weight_density = QLabel('Calibrated Weight Density (g/cm3):')
        self.weight_density = QLineEdit('8.36')

        calculate = QPushButton('Calculate')
        calculate.pressed.connect(self.calculate_norm)
        calculate.setFixedWidth(200)

        linesep1 = QFrame()
        linesep1.setFrameShape(QFrame.HLine)
        linesep1.setFrameShadow(QFrame.Sunken)

        self.calculated_water_density_label = QLabel('Water density at XX°C:')
        self.calculated_water_density = QLineEdit(self)
        self.calculated_water_density.setReadOnly(True)

        water_true_mass_label = QLabel('True Mass of Water (g):')
        self.water_true_mass = QLineEdit(self)
        self.water_true_mass.setReadOnly(True)

        calculated_volume_label = QLabel('Calculated Volume (mL):')
        self.calculated_volume = QLineEdit(self)
        self.calculated_volume.setReadOnly(True)

        standard_volume_label = QLabel('Flask Volume @20°C (mL):')
        self.standard_volume = QLineEdit(self)
        self.standard_volume.setReadOnly(True)

        grid_layout.addWidget(measured_weight_label, 0, 0)
        grid_layout.addWidget(self.measured_weight, 0, 1)

        grid_layout.addWidget(temperature_label, 1, 0)
        grid_layout.addWidget(self.temperature, 1, 1)

        grid_layout.addWidget(air_density_label, 2, 0)
        grid_layout.addWidget(self.air_density, 2, 1)

        grid_layout.addWidget(balance_weight_density, 3, 0)
        grid_layout.addWidget(self.weight_density, 3, 1)

        grid_layout.addWidget(calculate, 6, 0, 1, 2, Qt.AlignHCenter)

        grid_layout.addWidget(linesep1, 7, 0, 1, 2)

        grid_layout.addWidget(self.calculated_water_density_label, 8, 0)
        grid_layout.addWidget(self.calculated_water_density, 8, 1)

        grid_layout.addWidget(water_true_mass_label, 9, 0)
        grid_layout.addWidget(self.water_true_mass, 9, 1)

        grid_layout.addWidget(calculated_volume_label, 10, 0)
        grid_layout.addWidget(self.calculated_volume, 10, 1)

        grid_layout.addWidget(standard_volume_label, 11, 0)
        grid_layout.addWidget(self.standard_volume, 11, 1)

        self.centralWidget().setLayout(grid_layout)

        self.show()

    def calculate_norm(self):
        try:
            measured_weight = float(self.measured_weight.text())
            temp = float(self.temperature.text())
            self.calculated_water_density_label.setText(f'Water density at {temp}°C:')
            air_density = float(self.air_density.text())
            weight_density = float(self.weight_density.text())

            # First need to determine accurate water density
            water_density = self.rhoddw(temp)
            self.calculated_water_density.setText(str(round(water_density, 6)))

            # Determine actual weight after accounting for effects
            true_weight = self.true_weight(measured_weight, water_density, weight_density, air_density)
            self.water_true_mass.setText(str(round(true_weight, 3)))

            volume = true_weight / water_density
            self.calculated_volume.setText(str(round(volume, 3)))

            # Convert this flask volume to standard at 20 deg C
            flask_std = self.glass_dvdt(volume, temp, 20)
            self.standard_volume.setText(str(round(flask_std, 3)))

        except ValueError:
            print('Need numbers in the fields')
        except Exception:
            print(traceback.print_exc())


    def true_weight(self, meas_weight, water_density, weight_density, air_density):
        # Calculated from Single pan balances, buoyancy and gravity, R. Battino 1984.
        tw = meas_weight * (1 + ((1/water_density) - (1/weight_density)) * air_density)

        return tw

    def rhoddw (self, temp):
        # The density of pure water, rhoddw, is calculated as give on page F-4 from
        # Volume Properties of Water, Equation 1, CRC Handbook, 69th Edition, 1989

        z0 = 999.83952
        z1 = 16.945176
        z2 = -0.0079870401
        z3 = -0.000046170461
        z4 = 0.00000010556302
        z5 = -2.8054253E-10
        z6 = 0.01687985

        rhot2 = z2 + temp * (z3 + temp * (z4 + temp * z5))
        rhot1 = z0 + temp * (z1 + temp * (rhot2))
        rhoddw = rhot1 * 0.001 / (1 + z6 * temp)

        return rhoddw

    def water_dvdt(self, volume, temperature_start, temperature_final):
        # Calculate the volume that would be occupied by a given amount of aqueous liquid at a
        # given temperature (temp final) if it were changed from an initial temperature (temp initial)
        # Determined by multiplying the volume by the density ratio, rho(temp_initial)/rho(temp_final)
        # Rho(temp) is extracted from F-4, Volume Properties of Water, Equation 1, CRC Handbook

        if temperature_start == 0:
            return 0

        else:
            ratio = self.rhoddw(temperature_start) / self.rhoddw(temperature_final)

            final_volume = volume * ratio

            return final_volume


    def glass_dvdt(self, volume, temperature_known, temperature_desired):
        # Calculates the actual volume of a glass container at a given temperature,
        # from the calibrated volume at a given temperature, e.g. 20 degrees C
        # Using glass coefficient for borosilicate glass from A. Dickson SOP13
        glass_coefficient = 0.00000975

        final_volume = volume * (1 + glass_coefficient * (temperature_desired - temperature_known))

        return final_volume
