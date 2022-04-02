from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea, QMainWindow, QShortcut
from PyQt5.QtGui import QFont, QColor, QBrush, QKeySequence
from PyQt5.QtCore import Qt, QObject, pyqtSignal
import time
from util import *

class dataFormat():
    def __init__(self, name='', function='', log='', t=0):
        self.name = name
        self.function = function
        self.log = log
        self.time = t
        self.meta = {}

class beepSignals(QObject):
    data = pyqtSignal(object)
    end = pyqtSignal(str)
    request = pyqtSignal(object)
    returnData = pyqtSignal(object,object)

class addSignal(QObject):
    add = pyqtSignal(int)

class mainToSignal(QObject):
    data = pyqtSignal(object)
    command = pyqtSignal(object)
    returnData = pyqtSignal(object)

class underTable(QWidget):
    def __init__(self, x=0, y=0, permission={}, labels=[], sabotage=False):
        super().__init__()
        self.x = x
        self.y = y
        self.paralyzed = False
        self.born = time.time()
        self.last_update = time.time()
        self.labels = labels
        self.permission = permission
        for func in ["self-request", "receiveD", "request", "upload", "download"]:
            if func not in self.permission.keys():
                self.permission[func] = len(self.labels) - 1
        self.name = self.nameMaker(self.y, self.x)
        self.layouta = QHBoxLayout()
        self.nBtn1=QPushButton("A") #age
        self.nBtn2=QPushButton("F") #send_keys
        self.nBtn3=QPushButton("P") #Paralyze
        for nnn in [self.nBtn1, self.nBtn2, self.nBtn3]:
            nnn.setMaximumHeight(20)
            nnn.setMinimumHeight(20)
        self.nBtn1.clicked.connect(self.btn1_clicked)
        self.nBtn2.clicked.connect(self.btn2_clicked)
        self.nBtn3.clicked.connect(self.btn3_clicked)
        self.layouta.addWidget(self.nBtn1)
        self.layouta.addWidget(self.nBtn2)
        self.layouta.addWidget(self.nBtn3)
        self.setLayout(self.layouta)
        self.signals = beepSignals()
        self.data = {}
    
    def nameMaker(self, y, x):
        return f"{self.labels[y]}_{x}"
    
    def btn1_clicked(self): #return age
        ret = dataFormat(self.name, self.btn1_clicked.__name__)
        age = time.time()-self.born
        ret.log = f"Age: {fo2(age)}s"
        ret.meta['born'] = self.born
        ret.meta['age'] = age
        ret.meta['last_update'] = self.last_update
        ret.time = time.time()
        self.signals.data.emit(ret)
        
    def btn2_clicked(self): #get file names
        ret = dataFormat(self.name, self.btn2_clicked.__name__)
        keys = list(self.data.keys())
        ret.log = f"Files: {', '.join(keys)}"
        ret.meta['files'] = keys
        ret.time = time.time()
        self.signals.data.emit(ret)
        
    def btn3_clicked(self): #paralyze
        self.paralyzed = True
        
    def receiveD(self, inp_ret): #receive data
        ret = dataFormat(self.name, self.receiveD.__name__)
        if self.y <= self.permission[self.receiveD.__name__]:
            if self.name == inp_ret.meta['to']:
                file_name = inp_ret.meta['file_name']
                self.data[file_name] = inp_ret.meta['data']
                ret.meta['code'] = inp_ret.meta['code']
                ret.log = f"{self.name} received {file_name} from {inp_ret.meta['from']}"
                ret.time = time.time()
                self.signals.data.emit(ret)
                self.signals.end.emit(inp_ret.meta['code'])
                self.last_update = time.time()
            else:
                ret.log = "Wrong address"
                ret.time = time.time()
                self.signals.data.emit(ret)
        else:
            ret.log = "No permission"
            ret.time = time.time()
            self.signals.data.emit(ret)
    
    def commandR(self, inp_ret): #others e.g. upload
        command = inp_ret.meta['command'].lower()
        ret = dataFormat(self.name, command)
        if command == 'upload':        
            if self.y <= self.permission[command]:
                file_name = inp_ret.meta['file_name']
                with open(file_name, "rb") as f:
                    self.data[file_name] = f.read()
                ret.meta['code'] = inp_ret.meta['code']
                ret.log = f"{file_name} uploaded successfully"
                ret.time = time.time()
                self.signals.end.emit(inp_ret.meta['code'])
                self.signals.data.emit(ret)
                self.last_update = time.time()
            else:
                ret.log = "No permission"
                ret.time = time.time()
                self.signals.data.emit(ret)
        
        elif command == 'request':        
            if self.y <= self.permission[command]:
                #check permission here using nameSplitter(inp_ret.meta['from'])[0] if needed
                file_name = inp_ret.meta['file_name']
                if file_name in self.data.keys():
                    ret.log = f"Return {file_name}"
                    ret.meta['file_name'] = file_name
                    ret.meta['data'] = self.data[file_name]
                    #ret.meta['original'] = inp_ret #retweet
                    ret.meta['from'] = self.name
                    ret.meta['to'] = inp_ret.meta['from']
                    ret.meta['code'] = inp_ret.meta['code']
                    ret.time = time.time()
                    self.signals.end.emit(inp_ret.meta['code'])
                    self.signals.data.emit(ret)
                else:
                    ret.log = "File not found"
                    ret.time = time.time()
                    self.signals.data.emit(ret)
            else:
                ret.log = "No permission"
                ret.time = time.time()
                self.signals.data.emit(ret)
            
        elif command == 'self-request': #useless?
            if self.y <= self.permission[command.lower()]:
                file_name = inp_ret.meta['file_name']
                ret.meta['file_name'] = file_name
                ret.log = f"Requested {file_name}"
                ret.time = time.time()
                self.signals.request.emit(ret) 
            else:
                ret.log = "No permission"
                ret.time = time.time()
                self.signals.data.emit(ret)
        
        elif command == 'download':        
            if self.y <= self.permission[command]:
                file_name = inp_ret.meta['file_name']
                if file_name in self.data.keys():
                    save_as = inp_ret.meta['save_as']
                    with open(save_as, "wb") as f:
                         f.write(self.data[file_name])
                    ret.meta['code'] = inp_ret.meta['code']
                    ret.log = f"{file_name} downloaded as {save_as} successfully"
                    ret.time = time.time()
                    self.signals.end.emit(inp_ret.meta['code'])
                    self.signals.data.emit(ret)
                else:
                    ret.log = "File not found"
                    ret.time = time.time()
                    self.signals.data.emit(ret)
            else:
                ret.log = "No permission"
                ret.time = time.time()
                self.signals.data.emit(ret)
            
        else:
            ret.log = "No command found"
            ret.time = time.time()
            self.signals.data.emit(ret)
    
    def returnData(self, etc=""): #to save
        self.signals.returnData.emit((self.y,self.x), self.data)

class cellTable(QTableWidget):
    def __init__(self):
        super().__init__(2,1)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setMaximumWidth(100)
        self.setMaximumHeight(110)
        self.setMinimumWidth(100)
        self.setMinimumHeight(110)
        self.verticalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

class cellCol(QTableWidgetItem):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.colorLis = [QColor(122, 174, 196),
            QColor(238, 238, 155),
            QColor(120, 152, 133),
            QColor(217,152,136)]
        self.tableFont=QFont()
        self.tableFont.setPointSize(30)
        self.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setFont(self.tableFont)
        self.setBackground(self.colorLis[self.y])
        self.setFlags(Qt.ItemIsDragEnabled)
        self.setForeground(QBrush(QColor(0, 0, 0)))

class addBtnClass(QPushButton):
    def __init__(self, number):
        super().__init__("+")
        self.num = number
        self.font=QFont()
        self.font.setPointSize(25)
        self.setFont(self.font)
        self.setMinimumWidth(60)
        self.setMinimumHeight(60)
        self.setMaximumWidth(60)
        self.setMaximumHeight(60)
        self.setStyleSheet("background-color: gray; color: white; border: none;")
        self.addSignal = addSignal()
        self.clicked.connect(self.add)
    
    def add(self):
        self.addSignal.add.emit(self.num)