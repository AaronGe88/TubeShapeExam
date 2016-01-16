# coding=utf-8
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import ui_TEW
import numpy as np
import pypyodbc
class TubeExameWindow (QMainWindow, ui_TEW.Ui_Dialog):
	def __init__(self, parent=None):
		super(TubeExameWindow,self).__init__(parent)
		self.setupUi(self)
		#ascii_conn = uni_conn.encode("ascii")
		
		self.conn = pypyodbc.win_connect_mdb("D:/Works2015/TubeBendingSystem V2/导管弯曲.mdb")
		self.cur = conn.cursor()
		
	def accept(self):
		self.cur.close()
		self.conn.commit()
		self.conn.close()
		
	def reject(self):
		self.cur.close()
		self.conn.commit()
		self.conn.close()
if __name__== '__main__':
	import sys
	app = QApplication(sys.argv)
	#splash = splash_window.SplashScreen()
	#splash.effect()
	#app.processEvents()
	w = TubeExameWindow()
	w.show()
	#splash.finish(w)
	sys.exit(app.exec_())