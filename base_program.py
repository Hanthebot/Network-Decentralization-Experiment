from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDesktopWidget, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea, QMainWindow, QShortcut
from PyQt5.QtGui import QFont, QColor, QBrush, QKeySequence
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PIL import Image, ImageOps
from datetime import datetime
import os, time, traceback, random, sys, glob, json, random, string
import numpy as np

from util import *
from classes import *

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
        self.usage = {
            "upload":["upload file to cell", "upload [target] [file name] [code = random]"],
            "request":["send file request to cell", "request [target] [requester] [file name] [code = random]"],
            "download":["download file from cell","download [target] [file_name] [save directory] [code = random]"],
            "up_and_down":["upload and request file, return time","up_and_down [target] [requester] [file_name]"],
            "setname":["set name for structure","setname [name]"],
            "usage":["return usage","usage [command/all]"],
            "macroadd":["add certain number of cells","macroadd [layer name] [quantity]"],
            "requestr":["request to random cell in target layer","requestr [target layer name] [requester]"],
            "requestrr":["request from random cell in requesting layer to random cell in target layer","requestr [target layer name] [requesting layer name]"],
            "clearlog":["clears log", "clearlog"],
            "clearlog":["clears log", "help"],
            "a":["returns cell age in seconds", "press button 'A'"],
            "f":["returns list of files stored in the cell", "press button 'F'",],
            "save":["save data","press save button or Ctrl+S"]
        }
        self.functions_count = {u:0 for u in self.usage}
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
            "log_data":self.logList,
            "func_data":self.functions_count
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
            self.logList.append([datetime.now().strftime('%H:%M:%S.%f')[:-4], name, string.replace("\"","'")])
        self.logScr.setText(logText)
    
    def entered(self):
        text = self.commandText.text()
        self.commandText.clear()
        self.prompt(text)
    
    def prompt(self, command):
        self.logUpdate("System", command, '')
        cwords = splitQS(command)
        command = cwords[0].lower()
        if command not in self.usage.keys():
            self.logUpdate("System", "No command found", '')
            return False
        else:
            self.functions_count[command] += 1
        if len(cwords) > 1:
            if self.aName(cwords[1]): #have a target node
                target = self.nameSplitter(cwords[1])
                if command == 'upload':
                    ret = dataFormat("System", self.prompt.__name__+"/"+command)
                    ret.meta['command'] = command
                    ret.meta['file_name'] = cwords[2]
                    ret.meta['code'] = self.returnCode(command) if len(cwords) <= 3 else cwords[3]
                    self.task_signal[ret.meta['code']] = False
                    ret.time = time.time()
                    self.main_signal[target[0]][target[1]].command.emit(ret) #upload file
                
                elif command == 'request':
                    ret = dataFormat("System", self.prompt.__name__+"/"+command)
                    ret.meta['command'] = command
                    file_name = cwords[3]
                    ret.meta['file_name'] = file_name
                    ret.meta['code'] = self.returnCode(command) if len(cwords) <= 4 else cwords[4]
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
                    ret.meta['code'] = self.returnCode(command)
                    self.task_signal[ret.meta['code']] = False
                    ret.meta['from'] = "System"
                    ret.meta['to'] = self.nameMaker(target[0], target[1])
                    ret.log = ret.meta['from']+" download "+file_name+" to "+ret.meta['to']
                    ret.time = time.time()
                    self.main_signal[target[0]][target[1]].command.emit(ret)
                
                elif command == 'up_and_down':
                    t = time.time()
                    file_name = cwords[3]
                    ran_code = self.returnCode(command)+"_U"
                    self.prompt(f"upload {cwords[1]} {file_name} {ran_code}")
                    i=0
                    while i < 100:
                        if self.task_signal[ran_code]:
                            break
                        time.sleep(0.02)
                    if self.task_signal[ran_code]:
                        ran_code2 = self.returnCode(command)+"_D"
                        self.prompt(f"request {cwords[1]} {cwords[2]} {file_name} {ran_code2}")
                        i=0
                        while i < 100:
                            if self.task_signal[ran_code2]:
                                break
                            time.sleep(0.02)
                        if self.task_signal[ran_code2]:
                            self.logUpdate("System", f"up_and_down {file_name} finished {time.time()-t}s", '')
                        else:
                            self.logUpdate("System", "Failed requesting", '')
                    else:
                        self.logUpdate("System", "Failed uploading", '')
                    
                else:
                    self.logUpdate("System", "Invalid syntax: try usage", '')
            else:
                if command == 'setname':
                    global code
                    code = cwords[1]
                    self.setWindowTitle(f"Network Simulation -{code}")
                    self.logUpdate("System", f"structure code -> {code}", gray)
                    
                if command == 'usage':
                    phrase = cwords[1].lower()
                    if phrase in self.usage.keys():
                        self.logUpdate("System", f"{phrase}: "+'\n'.join(self.usage[phrase]), '')
                    elif phrase == "all":
                        for u in self.usage.keys():
                            self.logUpdate("System", f"{u}: "+'\n'.join(self.usage[u]), '')
                    else:
                        self.logUpdate("System", "Invalid syntax: try usage", '')
                
                elif command == 'macroadd':
                    target_layer = self.returnNum(cwords[1])
                    quant = int(cwords[2])
                    for i in range(quant):
                        self.cellAdd(target_layer, False)
                    self.logUpdate("System", "Log cleared", gray)
                
                elif command == 'requestr':
                    target_layer = self.returnNum(cwords[1])
                    requester = self.nameSplitter(cwords[2])
                    file_name = cwords[3]
                    requestTo = random.randrange(len(self.main_signal[target_layer]))
                    self.prompt(f"request {self.labels[target_layer]}_{requestTo} {nameMaker(requester[0], requester[1])} {file_name}")
                    self.logUpdate(f"System", "To {self.labels[target_layer]}_{requestTo}", gray)
                
                elif command == 'requestrr':
                    target_layer = self.returnNum(cwords[1])
                    request_layer = self.returnNum(cwords[2])
                    file_name = cwords[3]
                    requestTo = random.randrange(len(self.main_signal[target_layer]))
                    requestFrom = random.randrange(len(self.main_signal[request_layer]))
                    self.prompt(f"request {self.labels[target_layer]}_{requestTo} {self.labels[request_layer]}_{requestFrom} {file_name}")
                    self.logUpdate(f"System", "To {self.labels[target_layer]}_{requestTo} from {self.labels[request_layer]}#{requestFrom}", gray)
        else:
            if command == 'clearlog':
                self.logList = []
                self.logScr.setText("")
                self.logUpdate("System", "Log cleared", gray)
            elif command == 'help':
                self.logUpdate("System", ", ".join(self.usage.keys()), gray)
            else:
                    self.logUpdate("System", "Invalid syntax: try usage", '')
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
            inp_data.meta['code'] =  rand6()
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
            sav.write(json.dumps(self.wholeData))
        with open(f"./data/{code}.txt","w") as sav:
            sav.write(json.dumps(self.wholeData))
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
    
    def nameMaker(self, y, x):
        return f"{self.labels[y]}_{x}"
    
    def aName(self, name):
        if "#" in name or "_" in name:
            return True
        return False
    
    def returnCode(self, command, plus):
        if command in self.usage.keys():
            if plus:
                return f"{command}#{self.functions_count[command]+1}"
            else:
                return f"{command}#{self.functions_count[command]}"
        else:
            return "no such command"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp(loading_data, log_dt)
    app.exec_()