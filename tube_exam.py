#coding：utf-8
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import * 
from PyQt5.QtSql import *
import numpy as np
import copy

import ui_TEW
import TSE


class TubeExameWindow (QDialog, ui_TEW.Ui_Dialog):
	def __init__(self, parent=None):
		super(TubeExameWindow,self).__init__(parent)
		self.setupUi(self)
		self.comboBox_model.addItem(u"仿真结果")
		self.comboBox_model.addItem(u"生产结果")
		self.comboBox_model.setCurrentIndex (1)
		self.comboBox_model.currentIndexChanged.connect(self.model_changed)
		
		self.pushButton_apply.clicked.connect(self.apply_edit)
		try:
			self.db = QSqlDatabase.addDatabase(u"QODBC");
			self.db.setDatabaseName(u"Driver={Microsoft Access Driver (*.mdb, *.accdb)};\
									DSN='';\
									DBQ=..\导管弯曲.mdb")
			r = self.db.open()
			if not r:
				raise ValueError(u"数据库连接异常！")
			
			query = QSqlQuery(u"select SAMPLE_ID from INTEGRATION_NEW",self.db)
			#uni_result = uni_query.execute
			while query.next():
				sample_ID = query.value(0)
				
			self.lineEdit_ID.setText(sample_ID)
			sample_ID = u"".join([u"'",sample_ID,u"'"])
			
			self.model_design = QSqlTableModel(self,self.db)
			self.model_design.setTable(u"YBC_INFO")
			self.model_design.setEditStrategy(QSqlTableModel.OnManualSubmit)
			self.model_design.setFilter(u"SAMPLE_ID = {0}".format(sample_ID))
			self.model_design.select()
			
			self.tableView_design.setModel(self.model_design)
			self.tableView_design.setEditTriggers(QAbstractItemView.NoEditTriggers)
			self.tableView_design.hideColumn (0)
			self.tableView_design.hideColumn (1)
			self.tableView_design.hideColumn (5)
			
			
			self.model_cae = QSqlTableModel(self,self.db)
			self.model_cae.setTable(u"CAE_INFO")
			self.model_cae.setEditStrategy(QSqlTableModel.OnManualSubmit)
			self.model_cae.setFilter(u"SAMPLE_ID = {0}".format(sample_ID))
			self.model_cae.select()			
			
			
			self.model_manu = QSqlTableModel(self,self.db)
			self.model_manu.setTable(u"MANU_INFO")
			self.model_manu.setEditStrategy(QSqlTableModel.OnManualSubmit)
			self.model_manu.setFilter(u"SAMPLE_ID = {0}".format(sample_ID))
			self.model_manu.select()
			
			
			self.tableView_test.setModel(self.model_manu)
			self.tableView_test.setEditTriggers(QAbstractItemView.DoubleClicked)
			self.tableView_test.hideColumn (0)
			self.tableView_test.hideColumn (1)
			self.tableView_test.hideColumn (5)
			#self.tableView_test.dataChanged.connect(self.data_changed_test)
			
			#print(self.model_design)
			#self.conn = pyodbc.win_connect_mdb(u"C:/Users/Noah/Documents/GitHub/TubeShapeExam/导管弯曲.mdb")
			#self.cur = self.conn.cursor()
			#self.uni_sql = u"select SAMPLE_ID from INTEGRATION_NEW"
			#self.cur.execute(self.uni_sql)
			#self.cur.commit()
			#self.sample_ID =  self.cur.fetchone()[0]
			
			#self.uni_sql = u"".join([u"select * from YBC_INFO where SAMPLE_ID = '",\
			#						self.sample_ID, "'"])
			#print(self.uni_sql)
			#self.cur.execute(self.uni_sql)
			#print (self.cur.fetchone())
		except ValueError as e:
			print(e)
			
	def accept(self):
		try:
			self.db.close()
		except AttributeError as e:
			print(e)
		super().accept()
		
	def reject(self):
		try:
			self.db.close()
		except AttributeError as e:
			print(e)
		super().reject()
		
	def model_changed(self, index):
		if index == 0:
			self.tableView_test.setModel(self.model_cae)
		else :
			self.tableView_test.setModel(self.model_manu)
		self.tableView_test.hideColumn (0)
		self.tableView_test.hideColumn (1)
		self.tableView_test.hideColumn (5)
		
	def apply_edit(self):
		model = self.tableView_test.model()
		model.database().transaction()
		if model.submitAll():
			model.database().commit()
		else:
			model.database().rollback()
			print(model.lastError().text())
		
		row = self.model_design.rowCount()
		#print(self.model_design.columnCount())
		self.ybc_design = np.zeros([row, 4])
		self.ybc_cae = np.zeros([row, 4])
		self.ybc_manu = np.zeros([row, 4])
		try:
			for ii in range(row):
				for jj, kk in enumerate([2,3,4,6]):
					self.ybc_design[ii, jj] = self.model_design.data(\
											self.model_design.index(ii, kk),\
											Qt.DisplayRole)
					self.ybc_cae[ii, jj] = self.model_cae.data(\
											self.model_cae.index(ii, kk),\
											Qt.DisplayRole)				
					self.ybc_manu[ii, jj] = self.model_manu.data(\
											self.model_manu.index(ii, kk),\
											Qt.DisplayRole)
			#print(self.ybc_design,"\n", self.ybc_cae, "\n", self.ybc_manu)
		except ValueError as e:
			print(e)
		
		if self.comboBox_model.currentIndex() == 0:
			ybc_test = self.ybc_cae
		else:
			ybc_test = self.ybc_manu
			
		r = np.array([self.ybc_design[:,3].tolist(),])
		#print(self.ybc_design[:,0:3].shape,r)
		self.model_gaps = QStandardItemModel(self.tableView_gap)
		xyz0, xyz_mod = TSE.tube_shape_exam(self.ybc_design[:,0:3], \
							ybc_test[:,0:3], r)
		line0 = TSE.fit_line(xyz0)
		line_mod = TSE.fit_line(xyz_mod)
		#print(self.comboBox_model.currentIndex(),ybc_test)
		try:
			self.gaps = np.sqrt(np.sum((line0 - line_mod) ** 2,\
								axis = 1))
			str_gaps = ((self.gaps * 100).astype(np.int) / 100)
			for ii, f in enumerate(str_gaps):
				self.model_gaps.setItem(0, ii, QStandardItem(str(f)))
				#print(f)
				#print(f)
			self.tableView_gap.setModel(self.model_gaps)
		except Exception as e:
			print(e)
		
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