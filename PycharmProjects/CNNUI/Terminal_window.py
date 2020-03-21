# -*- coding: utf-8 -*-
import sys
from terminal_info import Ui_mainWindow
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QFileDialog,QMessageBox,QMainWindow,QApplication

sys.setrecursionlimit(1000000)

class EmittingStr(QObject):  
    textWritten = pyqtSignal(str)  #定义一个发送str的信号

    def write(self, text):
        self.textWritten.emit(str(text))
    
class terminalwindow(QMainWindow, Ui_mainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_mainWindow.__init__(self)
        self.setupUi(self)
        self.Button_clear.clicked.connect(self.clear_screen)
        emitstr = EmittingStr(textWritten=self.outputWritten)
        sys.stdout = emitstr
        sys.stderr = emitstr
        
    def outputWritten(self, text):
        cursor = self.textBrowser_info.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.textBrowser_info.setTextCursor(cursor)
        self.textBrowser_info.ensureCursorVisible()
        
    def __del__(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
    def windowOpen(self):
        self.__init__()
        self.show()
   
    def clear_screen(self):
        self.textBrowser_info.setText('')
        
    def closeEvent(self, event):
        reply = QMessageBox.question(self,'信息',"是否退出？",QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.tb_train_info.setText('')
            self.close()
        else:
            event.ignore()
# 测试函数
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = terminalwindow()
#     window.show()
#     for letter in 'Python':  # 第一个实例
#         print('当前字母 :', letter)
#
#     fruits = ['banana', 'apple', 'mango']
#     for fruit in fruits:  # 第二个实例
#         print('当前水果 :', fruit)
#
#     print("Good bye!")
#     sys.exit(app.exec_())

