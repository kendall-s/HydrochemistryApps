import sys
from PyQt5.QtWidgets import (QApplication)
from package import Kenware

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Kenware.KenWareMain()
    sys.exit(app.exec_())