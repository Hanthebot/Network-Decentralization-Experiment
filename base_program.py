from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDesktopWidget, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea, QMainWindow, QShortcut
from PyQt5.QtGui import QFont, QColor, QBrush, QKeySequence
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PIL import Image, ImageOps
from datetime import datetime
import os, time, traceback, random, sys, glob, json, random, string
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

gray = '808080'
code = sys.argv[1].replace(".txt","") if len(sys.argv) > 1 else "default"
default_data = {
        "colNum" : [3, 4, 5, 6],
        "permission":{"self-request": 3, "receiveD": 3, "request": 3, "upload": 0, "download": 0},
        "data_provider":[0,0,0,0],
        "labels":["Admin","Manager","Node","User"]
    }

if os.path.exists("./data/"+code+".txt"):
    print("File already existing. Loading...")
    with open("./data/"+code+".txt", 'r') as fil:
        total_data = json.load(fil)
    loading_data = total_data['table_data']
    if set(loading_data['permission'].keys()) != set(default_data['permission'].keys()):
        for k in default_data['permission'].keys():
            if k not in loading_data['permission'].keys():
                loading_data['permission'][k] = len(loading_data['labels']) - 1
    log_dt = total_data['log_data']
    
else:
    if len(sys.argv) > 1:
        print("No file found. Continuing on default...")
    else:
        print("No argument. Continuing on default...")
    loading_data = default_data
    log_dt = []

i = 0
while len(loading_data['labels']) < len(loading_data['colNum']):
    loading_data['labels'].append(f'{i}Emp')
    i += 1

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
    return "{0:.6f}".format(a).ljust(len("{0:.6f}".format(a)))\

def splitQS(a): #split quotes and space
    l=[]
    new = True
    quote = False
    for A in a:
        if new:
            l.append("")
            new = False
        if A == ' ' and quote != True:
            new = True
        elif A == '\"':
            quote = not quote
        else:
            l[-1] += A
    return l

def rand6(length=6):
    chars = string.digits
    random =  ''.join(random.choice(chars) for _ in range(length))

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
        self.born = time.time()
        self.last_update = time.time()
        self.labels = labels
        self.permission = permission
        for func in ["self-request", "receiveD", "request", "upload", "download"]:
            if func not in self.permission.keys():
                self.permission[func] = len(self.labels) - 1
        self.name = self.nameMaker(self.x, self.y)
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
    
    def nameMaker(self, x, y):
        return f"{self.labels[y]}_{x}"
    
    def btn1_clicked(self): #return age
        ret = dataFormat(self.name, self.btn1_clicked.__name__)
        age = time.time()-self.born
        ret.log = f"Age: {fo2(age)}s"
        ret.meta['born'] = self.born
        ret.meta['age'] = age
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
        pass
        
    def receiveD(self, inp_ret): #receive data
        ret = dataFormat(self.name, self.receiveD.__name__)
        if self.y <= self.permission[self.receiveD.__name__]:
            if self.name == inp_ret.meta['to']:
                file_name = inp_ret.meta['file_name']
                self.data[file_name] = inp_ret.meta['data']
                ret.log = f"{self.name} received {file_name} from {inp_ret.meta['from']}"
                ret.time = time.time()
                self.signals.data.emit(ret)
                self.signals.end.emit(inp_ret.meta['code'])
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
        ret = dataFormat(self.name, self.commandR.__name__+"/"+command)
        if command == 'upload':        
            if self.y <= self.permission[command]:
                file_name = inp_ret.meta['file_name']
                with open(file_name, "rb") as f:
                    self.data[file_name] = f.read()
                ret.log = f"{file_name} uploaded successfully"
                ret.time = time.time()
                self.signals.data.emit(ret)
                self.signals.end.emit(inp_ret.meta['code'])
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
                    ret.time = time.time()
                    self.signals.data.emit(ret)
                    self.signals.end.emit(inp_ret.meta['code'])
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
                    ret.log = f"{file_name} downloaded as {save_as} successfully"
                    ret.time = time.time()
                    self.signals.data.emit(ret)
                    self.signals.end.emit(inp_ret.meta['code'])
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

class MyApp(QMainWindow):
    def __init__(self,setup_data, log_dt):
        super().__init__()
        self.Q=QWidget()
        self.colNum = setup_data['colNum']
        self.table_num = len(setup_data['colNum'])
        self.permission = setup_data['permission']
        self.data_provider = setup_data['data_provider']
        self.labels = loading_data['labels']
        self.logList = log_dt
        self.setCentralWidget(self.Q)
        self.initUI()
        
    def initUI(self):
        self.ol = ""
        self.result = ""
        self.ti = ""
        self.task_signal = {}
        self.QQ = QHBoxLayout()
        self.A = QVBoxLayout()
        self.Sc = QVBoxLayout()
        self.btnA = QVBoxLayout()
        self.btnB = QVBoxLayout()
        self.btnWhole = QHBoxLayout()
        self.time = QLabel("",self)
        self.tables = []
        self.buttons = []
        self.main_signal = [[mainToSignal() for j in range(self.colNum[i])] for i in range(self.table_num)]
        for g in range(self.table_num):
            btns=QHBoxLayout()
            undButtons = []
            for num in range(self.colNum[g]):
                nBtn = cellTable()
                cell = cellCol(num, g)
                nBtn.setItem(0,0, cell)
                bbtn = underTable(num, g, self.permission, self.labels)
                bbtn.signals.data.connect(self.dataInterpret)
                bbtn.signals.request.connect(self.requestConnect)
                bbtn.signals.returnData.connect(self.returnedData)
                self.main_signal[g][num].command.connect(bbtn.commandR) #uploading
                self.main_signal[g][num].data.connect(bbtn.receiveD) #for sending out data
                self.main_signal[g][num].returnData.connect(bbtn.returnData) #for save
                nBtn.setCellWidget(1,0, bbtn)
                btns.addWidget(nBtn)
                undButtons.append(nBtn)
            self.buttons.append(undButtons)
            self.tables.append(btns)
        
        self.wholeData = {
            "table_data":{
                "colNum": self.colNum,
                "permission":self.permission,
                "data_provider":self.data_provider,
                "labels":self.labels
                },
            "cell_data":[[[] for x in range(self.colNum[g])] for g in range(self.table_num)],
            "log_data":self.logList
        }
        
        for btns in self.tables:
            self.A.addLayout(btns)
        
        self.addBtnLis = [addBtnClass(g) for g in range(self.table_num)]
        for addbtn in self.addBtnLis:
            addbtn.addSignal.add.connect(self.addCell)
            self.btnB.addWidget(addbtn)
        
        self.commandText = QLineEdit(self)
        self.commandText.returnPressed.connect(self.entered)
        self.A.addWidget(self.commandText)
        
        self.scrollWidth = 250
        self.Btn = QPushButton("refresh", self)
        self.Btn.clicked.connect(self.box)
        self.Btn.setMaximumWidth(self.scrollWidth)
        self.BtnS = QPushButton("save", self)
        self.BtnS.clicked.connect(self.save)
        self.BtnS.setMaximumWidth(self.scrollWidth)
        shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        shortcut.activated.connect(self.save)
        self.scrollArea = QScrollArea()
        #self.scrollArea.setMaximumWidth(self.scrollWidth)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.verticalScrollBar().rangeChanged.connect(self.moveToEnd)
        self.logScr = QLabel(self)
        self.logScr.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.logScr.setWordWrap(True)
        self.scrollArea.setWidget(self.logScr)
        self.Sc.addWidget(self.scrollArea)
        self.Sc.addWidget(self.Btn)
        self.Sc.addWidget(self.BtnS)
        
        self.QQ.addLayout(self.A)
        self.QQ.addLayout(self.btnB)
        self.QQ.addLayout(self.Sc)
        
        self.statusBar().addPermanentWidget(self.time,0)
        self.Q.setLayout(self.QQ)
        self.setGeometry(300,300,1000,500)
        self.setWindowTitle(f"Network Simulation -{code}")
        self.center()
        self.show()
        for lg in self.logList:
            self.logUpdate(lg[1], lg[2], color=gray, t=lg[0], new=False)
    
    def paintEvent(self, QPaintEvent):
        self.time.setText(self.ti)
        if self.ol!=self.result:
            lns=[l.split(" ") for l in self.result.split("\n")]
            for Y in range(self.table_num):
                for X in range(self.colNum[Y]):
                    self.buttons[Y][X].item(0, 0).setText(lns[Y][X])

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def box(self):
        t = time.time()
        self.ti = "time spent: "+fo2(time.time()-t)+"s"
        self.result="\n".join([" ".join([self.labels[Y][0] for X in range(self.colNum[Y])]) for Y in range(self.table_num)])
        self.logUpdate("System", "Data updated", gray)
    
    def moveToEnd(self):
        self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().maximum())
        
    def logUpdate(self, name, string, color='', t=datetime.now().strftime('%H:%M:%S.%f')[:-4], new = True):
        logText = self.logScr.text()
        logText += "<br>"
        if len(color) == 6:
            logText += "<span style=\"color:#"+color+"\">"
            logText += f"[{t}] {name}: {string}"
            logText +="</span>"
        else:
            logText += f"[{t}] {name}: {string}"
        addText = f"[{t}] {name}: {string}"
        if new:
            print(addText)
            self.logList.append([datetime.now().strftime('%H:%M:%S.%f')[:-4], name, string])
        self.logScr.setText(logText)
    
    def entered(self):
        text = self.commandText.text()
        self.commandText.clear()
        self.prompt(text)
    
    def prompt(self, command):
        self.logUpdate("System", command, '')
        cwords = splitQS(command)
        command = cwords[0].lower()
        if len(cwords) > 1:
            if self.aName(cwords[1]): #have a target node
                target = self.nameSplitter(cwords[1])
                if command == 'upload':
                    ret = dataFormat("System", self.prompt.__name__+"/"+command)
                    ret.meta['command'] = command
                    ret.meta['file_name'] = cwords[2]
                    ret.meta['code'] = rand6() if len(cwords) <= 3 else cwords[3]
                    self.task_signal[ret.meta['code']] = False
                    ret.time = time.time()
                    self.main_signal[target[0]][target[1]].command.emit(ret) #upload file
                
                elif command == 'request':
                    ret = dataFormat("System", self.prompt.__name__+"/"+command)
                    ret.meta['command'] = command
                    file_name = cwords[3]
                    ret.meta['file_name'] = file_name
                    ret.meta['code'] = rand6() if len(cwords) <= 4 else cwords[4]
                    self.task_signal[ret.meta['code']] = False
                    requester = self.nameSplitter(cwords[2])
                    ret.meta['from'] = self.nameMaker(requester[0], requester[1])
                    ret.meta['to'] = self.nameMaker(target[0], target[1])
                    ret.log = ret.meta['from']+" request "+file_name+" to "+ret.meta['to']
                    ret.time = time.time()
                    self.main_signal[target[0]][target[1]].command.emit(ret)
                
                elif command == 'download':
                    ret = dataFormat("System", self.prompt.__name__+"/"+command)
                    ret.meta['command'] = command
                    file_name = cwords[2]
                    save_as = cwords[3]
                    ret.meta['file_name'] = file_name
                    ret.meta['save_as'] = save_as
                    ret.meta['code'] =  rand6() if len(cwords) <= 4 else cwords[4]
                    self.task_signal[ret.meta['code']] = False
                    ret.meta['from'] = "System"
                    ret.meta['to'] = self.nameMaker(target[0], target[1])
                    ret.log = ret.meta['from']+" download "+file_name+" to "+ret.meta['to']
                    ret.time = time.time()
                    self.main_signal[target[0]][target[1]].command.emit(ret)
                
                elif command == 'up_and_down':
                    file_name = cwords[3]
                    ran_code = rand6()
                    self.prompt(f"upload {cwords[1]} {file_name} {ran_code}")
                    i=0
                    while i < 100:
                        if self.task_signal[ran_code]:
                            break
                        time.sleep(0.02)
                    if self.task_signal[ran_code]:
                        ran_code2 = rand6()
                        self.prompt(f"request {cwords[1]} {cwords[2]} {file_name} {ran_code2}")
                        i=0
                        while i < 100:
                            if self.task_signal[ran_code2]:
                                break
                            time.sleep(0.02)
                        if not self.task_signal[ran_code2]:
                            self.logUpdate("System", "Failed requesting", '')
                    else:
                        self.logUpdate("System", "Failed uploading", '')
                    
                else:
                    self.logUpdate("System", "No command found", '')
            else:
                if cwords[0].lower() == 'setname':
                    global code
                    code = cwords[1]
                    self.setWindowTitle(f"Network Simulation -{code}")
                    self.logUpdate("System", f"structure code -> {code}", gray)
                
                elif cwords[0].lower() == 'macroadd':
                    target_layer = self.returnNum(cwords[1])
                    quant = int(cwords[2])
                    for i in range(quant):
                        self.cellAdd(target_layer, False)
                    self.logUpdate("System", "Log cleared", gray)
                
                elif cwords[0].lower() == 'requestR':
                    target_layer = self.returnNum(cwords[1])
                    requester = self.nameSplitter(cwords[2])
                    file_name = cwords[3]
                    requestTo = random.randrange(len(self.main_signal[target_layer]))
                    self.prompt(f"request {self.labels[target_layer]}_{requestTo} {nameMaker(requester[0], requester[1])} {file_name}")
                    self.logUpdate(f"System", "To {self.labels[target_layer]}_{requestTo}", gray)
                
                elif cwords[0].lower() == 'requestRR':
                    target_layer = self.returnNum(cwords[1])
                    request_layer = self.returnNum(cwords[2])
                    file_name = cwords[3]
                    requestTo = random.randrange(len(self.main_signal[target_layer]))
                    requestFrom = random.randrange(len(self.main_signal[request_layer]))
                    self.prompt(f"request {self.labels[target_layer]}_{requestTo} {self.labels[request_layer]}_{requestFrom} {file_name}")
                    self.logUpdate(f"System", "To {self.labels[target_layer]}_{requestTo} from {self.labels[request_layer]}#{requestFrom}", gray)
        else:
            if command.lower() == 'clearlog':
                self.logList = []
                self.logScr.setText("")
                self.logUpdate("System", "Log cleared", gray)
            else:
                self.logUpdate("System", "No command found", '')
        pass
    
    def addCell(self, num, visible=True):
        self.colNum[num] += 1
        self.main_signal[num].append(mainToSignal())
        if visible:
            nBtn = cellTable()
            cell = cellCol(self.colNum[num]-1, num)
            nBtn.setItem(0,0, cell)
        bbtn = underTable(self.colNum[num]-1, num)
        bbtn.signals.data.connect(self.dataInterpret)
        bbtn.signals.end.connect(self.taskOrganize)
        self.main_signal[num][-1].command.connect(bbtn.commandR)
        self.main_signal[num][-1].data.connect(bbtn.receiveD)
        self.main_signal[num][-1].returnData.connect(bbtn.returnData)
        if visible:
            nBtn.setCellWidget(1,0, bbtn)
            self.buttons[num].append(nBtn)
            self.tables[num].addWidget(nBtn)
        self.wholeData['cell_data'][num].append([])
        if visible:
            self.logUpdate("Added",self.labels[num])
    
    def returnedData(self, coord, returnedData):
        y,x = coord
        self.wholeData["cell_data"][y][x] = list(returnedData.keys()) #for now
    
    def dataInterpret(self, inp_data):
        self.logUpdate(inp_data.name, inp_data.log, gray)
        if inp_data.function in ['commandR/request']:
            inp_data.name = "System"
            inp_data.function = self.dataInterpret.__name__
            target = self.nameSplitter(inp_data.meta['to'])
            inp_data.log = f"Sent {inp_data.meta['file_name']} to {inp_data.meta['to']}"
            inp_data.time = time.time()
            self.main_signal[target[0]][target[1]].data.emit(inp_data)
        if inp_data.function in ['commandR/upload','commandR/request']:
            self.logUpdate(inp_data.name, f"{inp_data.function} took {(time.time()-inp_data.time)}s", gray)
    
    def taskOrganize(self, ran_code):
        self.task_signal[ran_code] = True
        
    def save(self):
        self.wholeData["log_data"] = self.logList
        for Y in range(self.table_num):
            yLis = []
            for X in range(self.colNum[Y]):
                self.main_signal[Y][X].returnData.emit("")
        with open(f"./data/{code}_"+time.strftime("%Y%m%d_%H%M%S")+".txt","w") as sav:
            sav.write(str(self.wholeData).replace("'","\""))
        with open(f"./data/{code}.txt","w") as sav:
            sav.write(str(self.wholeData).replace("'","\""))
        self.logUpdate("Saved",time.strftime("%Y-%m-%d-%H:%M:%S"))
    
    def requestConnect(self, inp_data):
        y,x = self.nameSplitter(inp_data.name)
        requestTo = random.randrange(len(self.main_signal[self.data_provider[y]]))
        self.prompt(f"request {self.labels[self.data_provider[y]]}#{requestTo} {inp_data.name} {inp_data.meta['file_name']}")
        self.logUpdate(inp_data.name, inp_data.log, gray)

    def returnNum(self, a):
        for x in self.labels:
            if a.lower() in [x.lower(), x[0].lower()]:
                return self.labels.index(x)
        else:
            return len(self.labels)+1

    def nameSplitter(self, name):
        if "#" in name:
            clas, id_num = name.split("#")
            clas = self.returnNum(clas)
            id_num = int(id_num)
        elif "_" in name:
            clas, id_num = name.split("_")
            clas = self.returnNum(clas)
            id_num = int(id_num)
        else:
            clas, id_num (-1, -1)
        
        return (clas, id_num)
    
    def nameMaker(self, x,y):
        return f"{self.labels[y]}_{x}"
    
    def aName(self, name):
        if "#" in name or "_" in name:
            return True
        return False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp(loading_data, log_dt)
    app.exec_()