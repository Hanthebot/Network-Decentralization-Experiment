from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDesktopWidget, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,QScrollArea, QMainWindow
from PyQt5.QtGui import QFont, QColor, QBrush
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from functools import partial
from PIL import Image, ImageOps
from datetime import datetime
import os, time, traceback, string, random, pyautogui,sys
import numpy as np

def mkIfNone(path):
    if not os.path.exists(path):
        if path.replace("\\","/").split("/")[-1].replace(".","")!=path.replace("\\","/").split("/")[-1]:
            path="/".join(path.replace("\\","/").split("/")[:-1])
        try:
            os.makedirs(path)
        except:
            pass

mkIfNone("./data")

code = sys.argv[1] if len(sys.argv) >1 else "default"
if code in [G.replace("\"","'").replace(".txt","") for G in glob.glob("./data/*.txt")]:
    print("File already existing. Loading...")
    load = True

def fo(a):    
    return "{0:.2f}".format(a).ljust(15)

def fo2(a):
    return "{0:.2f}".format(a).ljust(len("{0:.2f}".format(a)))

def fo5(a):
    return "{0:.1f}".format(a).ljust(len("{0:.1f}".format(a)))

def fo6(a):
    return "{0:.4f}".format(a).ljust(len("{0:.4f}".format(a)))

def fo3(a):    
    return "{0:.6f}".format(a).ljust(15)

def fo4(a):    
    return "{0:.6f}".format(a).ljust(len("{0:.6f}".format(a)))

class beepSignals(QObject):
    data = pyqtSignal(str, object)
    beep = pyqtSignal(str, int)
    tim = pyqtSignal(float, float)

class responseSignal(QObject):
    data = pyqtSignal(str, object)

class addSignal(QObject):
    add = pyqtSignal(int)

class mainToSignal(QObject):
    data = pyqtSignal(str, object)
    request = pyqtSignal(str, object)
    command = pyqtSignal(str, object)

class underTable(QWidget):
    def __init__(self, x=0, y=0, sabotage=False):
        super().__init__()
        self.x = x
        self.y = y
        self.labels=['Admin','Manager','Node','User']
        self.name = f"{self.labels[self.y]}_{self.x}"
        self.layouta = QHBoxLayout()
        self.nBtn1=QPushButton("A") #request?
        self.nBtn2=QPushButton("S") #send_message
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
        
    def btn1_clicked(self):
        self.signals.data.emit(self.name, str(random.randint(10000,99999)))
        
    def btn2_clicked(self):
        self.signals.beep.emit(self.name,1)
        
    def btn3_clicked(self):
        self.signals.beep.emit(self.name,2)
        
    def request(self, fileName):
        self.signals.request.emit(self.name, [fileName, {"req_from":self.name, "req_at":time.time()}])
    
    def receiveD(self, dataR):
        fileName, data, meta = dataR
        self.data[fileName] = data
        #signal emit time done
    
    def receiveR(self, dataReq):
        fileName, meta = dataReq
        #check permision if needed
        if fileName in self.data.keys():
            self.signals.data.emit(self.name, [fileName, self.data[fileName], {"dat_from":self.name, "dat_at":time.time()}])
        else:
            self.signals.data.emit(self.name, 404)
    
    def commandR(self, dataReq):
        fileName, meta = dataReq
        #check permision if needed
        if fileName in self.data.keys():
            self.signals.data.emit(self.name, [fileName, self.data[fileName], {"dat_from":self.name, "dat_at":time.time()}])
        else:
            self.signals.data.emit(self.name, 404)
    
    def returnData(self):
        return self.data

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
        """
        nBtn.setStyleSheet("border: none;background-color:rgb"+str(self.colNum[g]['color']));
        #nBtn.clicked.connect(partial(self.prompt,self.boxes[eval("\""+box+"\"")]))"""

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
        self.setStyleSheet("background-color: gray; color: white;border: none;")
        self.addSignal = addSignal()
        self.clicked.connect(self.add)
    
    def add(self):
        self.addSignal.add.emit(self.num)

class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.Q=QWidget()
        self.setCentralWidget(self.Q)
        self.initUI()
        
    def initUI(self):
        self.ol=""
        self.result=""
        self.ti=""
        self.QQ=QHBoxLayout()
        self.A=QVBoxLayout()
        self.Sc=QVBoxLayout()
        self.btnA=QVBoxLayout()
        self.btnB=QVBoxLayout()
        self.btnWhole=QHBoxLayout()
        self.time=QLabel("",self)
        
        self.table_num = 4
        #------------------------------------------------------------------------------------------------------------------------------------------
        self.colNum = [3, 4, 5, 6]
        self.tables = []
        self.buttons = []
        self.main_signal = [[mainToSignal() for j in range(self.colNum[i])] for i in range(self.table_num)]
        for g in range(self.table_num):
            btns=QHBoxLayout()
            undButtons = []
            for num in range(self.colNum[g]):
                nBtn=cellTable()
                cell=cellCol(num, g)
                nBtn.setItem(0,0, cell)
                bbtn = underTable(num, g)
                bbtn.signals.data.connect(self.logUpdate)
                bbtn.signals.beep.connect(self.receive_func)
                self.main_signal[g][num].request.connect(bbtn.receiveR)
                self.main_signal[g][num].command.connect(bbtn.commandR)
                self.main_signal[g][num].data.connect(bbtn.receiveD)
                nBtn.setCellWidget(1,0, bbtn)
                btns.addWidget(nBtn)
                undButtons.append(nBtn)
            self.buttons.append(undButtons)
            self.tables.append(btns)
        
        self.labels=['Admin','Manager','Node','User']
        
        for btns in self.tables:
            self.A.addLayout(btns)
            
            
        #self.btnWhole.addLayout(self.btnA)
        self.addBtnLis = [addBtnClass(g) for g in range(self.table_num)]
        for addbtn in self.addBtnLis:
            addbtn.addSignal.add.connect(self.addCell)
            self.btnB.addWidget(addbtn)
        #self.btnWhole.addLayout(self.btnB)
        #self.A.addLayout(self.btnWhole)
        
        self.commandText=QLineEdit(self)
        self.commandText.returnPressed.connect(self.entered)
        
        self.A.addWidget(self.commandText)
        
        self.scrollWidth = 250
        self.Btn=QPushButton("refresh", self)
        self.Btn.clicked.connect(self.box)
        self.Btn.setMaximumWidth(self.scrollWidth)
        self.BtnS=QPushButton("save", self)
        self.BtnS.clicked.connect(self.save)
        self.BtnS.setMaximumWidth(self.scrollWidth)
        self.scrollArea = QScrollArea()
        self.scrollArea.setMaximumWidth(self.scrollWidth)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.verticalScrollBar().rangeChanged.connect(self.moveToEnd)
        self.logScr=QLabel(self)
        self.logScr.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.logScr.setWordWrap(True)
        self.scrollArea.setWidget(self.logScr)
        self.Sc.addWidget(self.scrollArea)
        self.Sc.addWidget(self.Btn)
        
        self.QQ.addLayout(self.A)
        self.QQ.addLayout(self.btnB)
        self.QQ.addLayout(self.Sc)
        
        self.statusBar().addPermanentWidget(self.time,0)
        self.Q.setLayout(self.QQ)
        self.setGeometry(300,300,1000,500)
        self.setWindowTitle("Network Simulation")
        self.center()
        self.show()
    
    def paintEvent(self, QPaintEvent):
        if self.ol!=self.result:
            lns=[l.split(" ") for l in self.result.split("\n")]
            for Y in range(self.table_num):
                for X in range(self.colNum[Y]):
                    self.buttons[Y][X].item(0, 0).setText(lns[Y][X])
                    #self.buttons[Y][X].setText(f"{Y}_{X}"+"\n"+lns[Y][X])
            self.ol=self.result
            self.time.setText(self.ti)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def box(self):
        t=time.time()
        txt=""
        for Y in range(self.table_num):
            xls = []
            for X in range(self.colNum[Y]):
                xls.append(self.labels[Y][0])
                #xls.append(str(random.randint(0,10)))
            txt+=" ".join(xls)+"\n"
        self.ti="time spent: "+fo2(time.time()-t)+"s"
        self.result=txt
        self.logUpdate("system", "Data updated", '808080')
    
    def moveToEnd(self):
        self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().maximum())
        
    def logUpdate(self, name, string, col=''):
        logText = self.logScr.text()
        logText += "<br>"
        if len(col) == 6:
            logText += "<span style=\"color:#"+col+"\">"
            logText += f"[{datetime.now().strftime('%H:%M:%S.%f')[:-4]}] {name}: {string}"
            logText +="</span>"
        else:
            logText += f"[{datetime.now().strftime('%H:%M:%S.%f')[:-4]}] {name}: {string}"
        addText = f"[{datetime.now().strftime('%H:%M:%S.%f')[:-4]}] {name}: {string}"
        print(addText)
        self.logScr.setText(logText)
    
    def entered(self):
        text=self.commandText.text()
        self.commandText.clear()
        self.prompt(text)
    
    def prompt(self, command):
        cwords = command.split(" ")
        if len(cwords) > 1:
            if '#' in cwords[1]: #have a target node
                target = cwords[1].split('#')
                target = [self.labels.index(target[0]), int(target[1])]
                if cwords[0] == '':
                    pass
        else:
            if command == '':
                pass
        self.logUpdate("Command", command, '')
        pass
    
    def receive_func(self, name, func_id):
        if func_id == 1:
            self.logUpdate(name, 'random text')
        elif func_id == 2:
            self.logUpdate(name, f"function_{func_id}")
    
    def addCell(self, num):
        self.colNum[num] += 1
        self.main_signal[num].append(mainToSignal())
        
        nBtn=cellTable()
        cell=cellCol(self.colNum[num]-1, num)
        nBtn.setItem(0,0, cell)
        bbtn = underTable(self.colNum[num]-1, num)
        bbtn.signals.data.connect(self.logUpdate)
        bbtn.signals.beep.connect(self.receive_func)
        self.main_signal[num][-1].request.connect(bbtn.receiveR)
        self.main_signal[num][-1].command.connect(bbtn.commandR)
        self.main_signal[num][-1].data.connect(bbtn.receiveD)
        nBtn.setCellWidget(1,0, bbtn)
        self.buttons[num].append(nBtn)
        self.tables[num].addWidget(nBtn)
        self.logUpdate("Add",str(num))
    
    def save(self):
        wholeData = {
            "table_data":{
                "table_num": self.table_num,
                "colNum": self.colNum
                },
            "cell_data":[],
            "log_data":self.logScr.text()
        }
        for Y in range(self.table_num):
            yLis = []
            for X in range(self.colNum[Y]):
                yLis.append(self.buttons[Y][X].item(1, 0).returnData())
            wholeData["cell_data"].append(yLis)
        sav = open("./data/{code}_"+time.strftime("%Y%m%d_%H%M%S"),"w")
        sav.write(str(wholeData))
        sav.close()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    app.exec_()