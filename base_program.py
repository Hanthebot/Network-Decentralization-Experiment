from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDesktopWidget, QPushButton, QScrollArea, QMainWindow, QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
from datetime import datetime
import os, time, random, sys, json, random

from util import mkIfNone, fo2, splitQS, joinQS
from classes import dataFormat, mainToSignal, underTable, cellTable, cellCol, addBtnClass

mkIfNone("./data")

gray = "808080"
code = sys.argv[1].replace(".txt", "") if len(sys.argv) > 1 else "default"
default_data = {
        "colNum" : [3, 4, 5, 6],
        "colNumSpe" : [False, False, False, False],
        "permission":{"self-request": 3, "received": 3, "request": 3, "upload": 0, "download": 3},
        "sync":{
            "data_provider": [0, 0, 0, 0],
            "sync": [0, 0, False, False]
        },
        "labels":["Admin", "Manager", "Node", "User"]
    }

if os.path.exists("./data/" + code + ".txt"):
    print("File already existing. Loading...")
    with open("./data/" + code + ".txt", "r", encoding = "utf-8") as fil:
        total_data = json.load(fil)
    loading_data = total_data["table_data"]
    if set(loading_data["permission"].keys()) != set(default_data["permission"].keys()):
        for k in default_data["permission"].keys():
            if k not in loading_data["permission"].keys():
                loading_data["permission"][k] = len(loading_data["labels"]) - 1
    log_dt = total_data.get("log_data", [])
    input_dt = total_data.get("input_data", [])
    loading_data["sync"] = total_data["table_data"].get("sync", default_data["sync"])
    loading_data["colNumSpe"] = total_data["table_data"].get("colNumSpe", default_data["colNumSpe"])
    
else:
    if len(sys.argv) > 1:
        print("No file found. Continuing on default...")
    else:
        print("No argument. Continuing on default...")
    loading_data = default_data
    log_dt = []
    input_dt = []

class MyApp(QMainWindow):
    def __init__(self, setup_data, log_dt, input_dt):
        super().__init__()
        global code
        self.Q = QWidget()
        self.colNum = setup_data["colNum"]
        self.colNumSpe = setup_data["colNumSpe"]
        self.table_num = len(setup_data["colNum"])
        self.permission = setup_data["permission"]
        self.syncData = setup_data["sync"]
        self.labels = loading_data["labels"]
        self.logList = log_dt
        self.inputList = input_dt
        self.usage = {
            "upload": ["upload file to cell", "upload [target] [file name] [code = random]"],
            "request": ["send file request to cell", "request [target] [requester] [file name] [code = random]"],
            "download": ["download file from cell", "download [target] [file_name] [save directory] [code = random]"],
            "up_and_down": ["upload and request file, return time", "up_and_down [target] [requester] [file_name]"],
            "requestr": ["request to random cell in target layer", "requestr [target layer name] [requester]"],
            "file": ["check files (same as f button)", "file [target]"],
            "setname": ["set name for structure", "setname [name]"],
            "usage": ["return usage", "usage [command/all]"],
            "macroadd": ["add certain number of cells", "macroadd [layer name] [quantity]"],
            "requestrr": ["request from random cell in requesting layer to random cell in target layer", "requestrr [target layer name] [requesting layer name]"],
            "requestrrx": ["request from random cell in requesting layer to random cell in target layer", "requestrr [target layer name] [requesting layer name]"],
            "uploadr": ["request from random cell in requesting layer to random cell in target layer", "uploadr [target layer name] [file name] [code = random]"],
            "uploadrx": ["request from random cell in requesting layer to random cell in target layer", "uploadr [target layer name] [file name] [code = random]"],
            "uploadrrx": ["request from random cell in requesting layer to random cell in target layer", "uploadr [target layer name] [file name] [code = random]"],
            "up_and_downrr": ["upload and request file, return time", "up_and_downrr [requester layer] [file_name]"],
            "up_and_downrrx": ["upload and request file, return time", "up_and_downrr [requester layer] [file_name]"],
            "repeat": ["repeat a command x times after t seconds", "repeat [x] [command] [t = 0]"],
            "delay": ["repeat a command x times after t seconds", "repeat [x] [command] [t = 0]"],
            "quantity": ["repeat a command x times after t seconds", "repeat [x] [command] [t = 0]"],
            "clearlog": ["clears log", "clearlog"],
            "help": ["returns list of functions", "help"],
            "label": ["return label", "label"],
            "a": ["returns cell age in seconds", "press button 'A'"],
            "f": ["returns list of files stored in the cell", "press button 'F'"],
            "save": ["save data", "press save button or Ctrl+S"]
        }
        self.functions_count = {u:0 for u in self.usage}
        self.events = {
            "received": {},
            "request": {},
            "upload": {},
            "download": {},
            "returnsync": {},
            "acceptsync": {},
            "acceptpublish": {},
            "btn1_clicked": {},
            "btn2_clicked": {},
            "publisher": {}
        }
        self.ol = ""
        self.result = ""
        self.birth = time.time()
        self.wholeData = {
            "table_data": {
                "colNum": self.colNum,
                "colNumSpe": self.colNumSpe,
                "permission": self.permission,
                "sync": self.syncData,
                "labels": self.labels
                },
            "cell_data": [[[] for X in range(self.colNum[Y])] for Y in range(self.table_num)],
            "log_data": self.logList,
            "input_data": self.inputList,
            "func_data": self.functions_count
        }
        self.lastI = 0
        self.setCentralWidget(self.Q)
        self.initUI()
        
    def initUI(self):
        self.ti = ""
        self.QQ = QHBoxLayout()
        self.A = QVBoxLayout()
        self.Sc = QVBoxLayout()
        self.btnA = QVBoxLayout()
        self.btnB = QVBoxLayout()
        self.btnWhole = QHBoxLayout()
        self.time = QLabel("", self)
        self.tables = [QHBoxLayout() for num in range(self.table_num)]
        self.buttons = [[] for num in range(self.table_num)]
        self.main_signal = [[mainToSignal() for X in range(self.colNum[Y])] for Y in range(self.table_num)]
        for Y in range(self.table_num):
            if not self.colNumSpe[Y]:
                for X in range(self.colNum[Y]):
                    self.addCell(Y, visible = True, setting = True, x = X)
            elif type(self.colNumSpe[Y]) == list:
                xi = 0
                for Z in self.colNumSpe[Y]:
                    for X in range(abs(Z)):
                        self.addCell(Y, visible = (Z >= 0), setting = True, x = xi)
                        xi += 1
        
        for btns in self.tables:
            self.A.addLayout(btns)
        
        self.addBtnLis = [addBtnClass(Y) for Y in range(self.table_num)]
        for addbtn in self.addBtnLis:
            addbtn.addSignal.add.connect(self.addCell)
            self.btnB.addWidget(addbtn)
        
        self.commandText = QLineEdit(self)
        self.commandText.returnPressed.connect(self.entered)
        self.A.addWidget(self.commandText)
        QShortcut(Qt.Key_Up, self, self.last_command)
        QShortcut(Qt.Key_Down, self, self.then_command)
        QShortcut(QKeySequence("Escape"), self, activated = self.esc)
        
        self.scrollWidth = 250
        self.Btn = QPushButton("refresh", self)
        self.Btn.clicked.connect(self.box)
        self.Btn.setMaximumWidth(self.scrollWidth)
        self.BtnS = QPushButton("save", self)
        self.BtnS.clicked.connect(self.save)
        self.BtnS.setMaximumWidth(self.scrollWidth)
        QShortcut(QKeySequence("Ctrl+S"), self, activated = self.save)
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
        
        self.statusBar().addWidget(self.time, 0)
        for Y in range(self.table_num):
            for X in range(self.colNum[Y]):
                self.main_signal[Y][X].active.emit(True)
        self.Q.setLayout(self.QQ)
        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle(f"Network Simulation -{code}")
        self.center()
        self.show()
        for lg in self.logList:
            self.logUpdate(lg[1], lg[2], color = gray, t = lg[0], new = False)
    
    def paintEvent(self, _):
        pass

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def box(self):
        #reset
        self.time.setText("Time spent: " + fo2(time.time() - self.birth) + "s")
        self.logUpdate("System", "Data updated", gray)
    
    def moveToEnd(self):
        self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().maximum())
        
    def logUpdate(self, name, string, color = "", t = None, new = True):
        t = datetime.now().strftime("%H:%M:%S.%f")[:-4] if t == None else t
        logText = self.logScr.text()
        logText += "<br>"
        if len(color) == 6:
            logText += "<span style = \"color:#" + color + "\">"
            logText += f"[{t}] {name}: {string}"
            logText += "</span>"
        else:
            logText += f"[{t}] {name}: {string}"
        addText = f"[{t}] {name}: {string}"
        if new:
            print(addText)
            self.logList.append([t, name, string.replace("\"", "'")])
        self.logScr.setText(logText)
    
    def entered(self):
        text = self.commandText.text()
        self.commandText.clear()
        self.lastI = 0
        if text != "":
            self.prompt(text)
    
    def prompt(self, commandF):
        cwords = splitQS(commandF.replace("'", "\""))
        cwordsO = cwords
        command = cwords[0].lower()
        tStart = 0
        tDash = "-t" in cwords
        quiet = "-q" in cwords
        while cwords[-1] in ["-t", "-q"]:
            if cwords[-1] == "-t":
                tStart = time.time()
                #self.events[command][cwords[-2]] = ["arrival", "compare", t, cwords[-2]] #reserve code
            cwords = cwords[:-1]
        if quiet:
            self.logUpdate("Prompt", commandF, gray)
        else:    
            self.inputList.append([datetime.now().strftime("%H:%M:%S.%f")[:-4], commandF])
            self.logUpdate("Prompt", commandF, "")
        if command not in self.usage.keys():
            self.logUpdate("System", "No command found", "")
            return False
        else:
            self.functions_count[command] += 1
        if len(cwords) > 1:
            if self.aName(cwords[1]): #have a target node
                target = self.nameSplitter(cwords[1])
                if command == "upload":
                    ret = dataFormat("System", command)
                    ret.meta["command"] = command
                    ret.meta["file_name"] = cwords[2]
                    ret.meta["code"] = self.returnCode(command) if len(cwords) <= 3 else cwords[3]
                    if tDash:
                        self.events["publisher"][ret.meta["code"]] = ["arrival", "compare", tStart, ret.meta["code"]]
                    ret.time = time.time()
                    self.main_signal[target[0]][target[1]].command.emit(ret) #upload file
                
                elif command == "request":
                    ret = dataFormat("System", command)
                    ret.meta["command"] = command
                    file_name = cwords[3]
                    ret.meta["file_name"] = file_name
                    ret.meta["code"] = self.returnCode(command) if len(cwords) <= 4 else cwords[4]
                    requester = self.nameSplitter(cwords[2])
                    ret.meta["from"] = self.nameMaker(requester[0], requester[1])
                    ret.meta["to"] = self.nameMaker(target[0], target[1])
                    ret.log = ret.meta["from"] + " request " + file_name + " to " + ret.meta["to"]
                    if tDash:
                        self.events["publisher"][ret.meta["code"]] = ["arrival", "compare", tStart, ret.meta["code"]]
                    ret.time = time.time()
                    self.main_signal[target[0]][target[1]].command.emit(ret)
                
                elif command == "download":
                    ret = dataFormat("System", command)
                    ret.meta["command"] = command
                    file_name = cwords[2]
                    save_as = cwords[3]
                    ret.meta["file_name"] = file_name
                    ret.meta["save_as"] = save_as
                    ret.meta["code"] = self.returnCode(command)
                    ret.meta["from"] = "System"
                    ret.meta["to"] = self.nameMaker(target[0], target[1])
                    ret.log = ret.meta["from"] + " download " + file_name + " to " + ret.meta["to"]
                    ret.time = time.time()
                    self.main_signal[target[0]][target[1]].command.emit(ret)
                
                elif command == "up_and_down":
                    file_name = cwords[3]
                    rcode = self.returnCode(command) if len(cwords) <= 4 else cwords[4]
                    ran_code = rcode + "U"
                    ran_code2 = rcode + "D"
                    self.events["publisher"][ran_code] = ["arrival", "prompt", f"request {cwords[1]} {cwords[2]} {file_name} {ran_code2} -q"]
                    if tDash:
                        self.events["received"][ran_code2] = ["arrival", "compare", tStart, self.returnCode(command)]
                    if self.permission["upload"] >= self.nameSplitter(cwords[1])[0]:
                        self.prompt(f"upload {cwords[1]} {file_name} {ran_code} -q")
                    else:
                        target_layer = self.permission["upload"]
                        requestTo = random.randrange(self.colNum[target_layer])
                        self.prompt(f"upload {self.nameMaker(target_layer, requestTo)} {file_name} {ran_code} -q")
                
                elif command == "requestr":
                    requester = self.nameSplitter(cwords[1])
                    target_layer = self.syncData["data_provider"][requester[0]]
                    file_name = cwords[2]
                    requestTo = random.randrange(self.colNum[target_layer])
                    self.prompt(f"request {self.nameMaker(target_layer, requestTo)} {self.nameMaker(requester[0], requester[1])} {joinQS(cwordsO[2:])} -q")
                
                elif command == "file":
                    target = self.nameSplitter(cwords[1])
                    ret = dataFormat("System", command)
                    ret.meta["command"] = command
                    ret.meta["code"] = self.returnCode(command)
                    ret.log = f"check files of {cwords[1]}"
                    ret.time = time.time()
                    self.main_signal[target[0]][target[1]].command.emit(ret)
                    
                else:
                    self.logUpdate("System", "Invalid syntax: try usage", "")
            else:
                if command == "setname":
                    code = cwords[1]
                    self.setWindowTitle(f"Network Simulation -{code}")
                    self.logUpdate("System", f"structure code -> {code}", gray)
                    
                if command == "usage":
                    phrase = cwords[1].lower()
                    if phrase in self.usage.keys():
                        self.logUpdate("System", f"{phrase}: " + " \\ ".join(self.usage[phrase]), "")
                    elif phrase == "all":
                        for u in self.usage.keys():
                            self.logUpdate("System", f"{u}: " + " \\ ".join(self.usage[u]), "")
                    else:
                        self.logUpdate("System", "Invalid syntax: try usage", "")
                
                elif command == "macroadd":
                    target_layer = self.returnNum(cwords[1])
                    quant = int(cwords[2])
                    ran_code = self.returnCode(command) if len(cwords) <= 3 else cwords[3]
                    if tDash:
                        self.events["publisher"][ran_code] = ["list", "compare", tStart, quant, ran_code, 0]
                    for _ in range(quant):
                        self.addCell(target_layer, visible = False, codeName = ran_code)
                    self.logUpdate("System", f"{quant} {self.labels[target_layer]}s added", gray)
                
                elif command == "requestrr":
                    request_layer = self.returnNum(cwords[1])
                    target_layer = self.syncData["data_provider"][request_layer]
                    file_name = cwords[2]
                    requestTo = random.randrange(self.colNum[target_layer])
                    requestFrom = random.randrange(self.colNum[request_layer])
                    self.prompt(f"request {self.nameMaker(target_layer, requestTo)} {self.nameMaker(request_layer, requestFrom)} {joinQS(cwordsO[2:])} -q")
                
                elif command == "requestrrx":
                    request_layer = self.returnNum(cwords[1])
                    target_layer = self.syncData["data_provider"][request_layer]
                    file_name = cwords[2]
                    ran_code = self.returnCode(command) if len(cwords) <= 3 else cwords[3]
                    tiX = 10
                    if tDash:
                        self.events["received"][ran_code] = ["list", "compare", tStart, tiX, ran_code, 0]
                    for i in range(tiX):
                        requestTo = random.randrange(self.colNum[target_layer])
                        requestFrom = random.randrange(self.colNum[request_layer])
                        self.prompt(f"request {self.nameMaker(target_layer, requestTo)} {self.nameMaker(request_layer, requestFrom)} {file_name} {ran_code} -q")
                
                elif command == "up_and_downrr":
                    request_layer = self.returnNum(cwords[1])
                    target_layer = self.syncData["data_provider"][request_layer]
                    file_name = cwords[2]
                    requestTo = random.randrange(self.colNum[target_layer])
                    requestFrom = random.randrange(self.colNum[request_layer])
                    self.prompt(f"up_and_down {self.nameMaker(target_layer, requestTo)} {self.nameMaker(request_layer, requestFrom)} {joinQS(cwordsO[2:])} -q")
                
                elif command == "up_and_downrrx":
                    request_layer = self.returnNum(cwords[1])
                    target_layer = self.syncData["data_provider"][request_layer]
                    file_name = cwords[2]
                    ran_code = self.returnCode(command) if len(cwords) <= 3 else cwords[3]
                    tiX = 10
                    if tDash:
                        self.events["received"][ran_code + "D"] = ["list", "compare", tStart, tiX, ran_code, 0]
                    for i in range(tiX):
                        requestTo = random.randrange(self.colNum[target_layer])
                        requestFrom = random.randrange(self.colNum[request_layer])
                        self.prompt(f"up_and_down {self.nameMaker(target_layer, requestTo)} {self.nameMaker(request_layer, requestFrom)} {file_name} {ran_code} -q")
                
                elif command == "uploadrrx":
                    target_layer = self.returnNum(cwords[1])
                    file_name = cwords[2]
                    ran_code = self.returnCode(command) if len(cwords) <= 3 else cwords[3]
                    tiX = 10
                    c = sum([self.colNum[syn] for syn in range(len(self.colNum)) if self.syncData["sync"][syn] == target_layer and type(self.syncData["sync"][syn]) == int])
                    if tDash:
                        self.events["publisher"][ran_code] = ["list", "compare", tStart, tiX*c, ran_code, 0]
                    for i in range(tiX):
                        requestTo = random.randrange(self.colNum[target_layer])
                        self.prompt(f"upload {self.nameMaker(target_layer, requestTo)} {file_name} {ran_code} -q")
                
                elif command == "uploadr":
                    target_layer = self.returnNum(cwords[1])
                    file_name = cwords[2]
                    requestTo = random.randrange(self.colNum[target_layer])
                    self.prompt(f"upload {self.nameMaker(target_layer, requestTo)} {joinQS(cwordsO[2:])} -q")
                
                elif command == "uploadrx":
                    target_layer = self.returnNum(cwords[1])
                    file_name = cwords[2]
                    rcode = self.returnCode(command) if len(cwords) <= 3 else cwords[3]
                    ran_code = rcode + "U"
                    ran_code2 = rcode + "M"
                    requestTo = random.randrange(self.colNum[target_layer])
                    if tDash:
                        self.events["publisher"][ran_code2] = ["list", "compare", tStart, 100, ran_code2, 0]
                    self.events["upload"][ran_code] = ["arrival", "prompt", f"macroadd {self.labels[len(self.colNum) - 1]} 100 {ran_code2} -t"]
                    self.prompt(f"upload {self.nameMaker(target_layer, requestTo)} {file_name} {ran_code} -q")
                
                elif command == "quantity":
                    target_layer = self.returnNum(cwords[1])
                    if type(self.colNumSpe[target_layer]) == list:
                        hidden_num = (self.colNum[target_layer] - sum(self.colNumSpe[target_layer])) / 2
                        self.logUpdate("System", f"{cwords[1]}: {self.colNum[target_layer]}, {int(hidden_num)} hidden", gray)
                    else:
                        self.logUpdate("System", f"{cwords[1]}: {self.colNum[target_layer]}", gray)
                
                elif command == "repeat":
                    x = int(cwords[1])
                    repeated_command = joinQS(cwordsO[2:-1])
                    for r in range(x - 1):
                        self.logUpdate("System", str(r + 1), gray)
                        self.prompt(repeated_command)
                        print("\n")
                        time.sleep(float(cwords[-1]))
                    self.logUpdate("System", str(x), gray)
                    self.prompt(repeated_command)
                
                elif command == "delay":
                    x = float(cwords[1])
                    time.sleep(x)
                    self.logUpdate("System", "", gray)
                    repeated_command = joinQS(cwordsO[2:])
                    self.prompt(repeated_command)
                    
        else:
            if command == "clearlog":
                self.logList = []
                self.logScr.setText("")
                self.logUpdate("System", "Log cleared", gray)
            
            elif command == "help":
                self.logUpdate("System", ", ".join(self.usage.keys()), gray)
                
            elif command == "label":
                self.logUpdate("System", ", ".join(self.labels), gray)
            else:
                self.logUpdate("System", "Invalid syntax: try usage", "")
    
    def addCell(self, Y, visible = True, setting = False, x = 0, codeName = False):
        if not setting:
            self.colNum[Y] += 1
            x = self.colNum[Y] - 1
            self.main_signal[Y].append(mainToSignal())
            if visible:
                if not self.colNumSpe[Y]:
                    self.colNumSpe[Y] = [x + 1]
                elif self.colNumSpe[Y][-1] > 0:
                    self.colNumSpe[Y][-1] += 1
                else:
                    self.colNumSpe[Y].append(1)
            else:
                if not self.colNumSpe[Y]:
                    self.colNumSpe[Y] = [x, -1]
                elif self.colNumSpe[Y][-1] < 0:
                    self.colNumSpe[Y][-1] -= 1
                else:
                    self.colNumSpe[Y].append(-1)
        
        nBtn = cellTable()
        cell = cellCol(x, Y)
        nBtn.setItem(0, 0, cell)
        if codeName:
            bbtn = underTable(x, Y, permission = self.permission, labels = self.labels, code_num = codeName)
        else:
            bbtn = underTable(x, Y, permission = self.permission, labels = self.labels)
        bbtn.signals.data.connect(self.dataInterpret)
        bbtn.signals.end.connect(self.taskOrganize)
        bbtn.signals.returnData.connect(self.returnedData)
        bbtn.signals.publish.connect(self.publisher)
        bbtn.signals.sync.connect(self.syncer)
        self.main_signal[Y][x].command.connect(bbtn.commandR)
        self.main_signal[Y][x].returnData.connect(bbtn.returnData)
        self.main_signal[Y][x].active.connect(bbtn.activate)
        
        nBtn.item(0, 0).setText(self.labels[Y][0])
        nBtn.setCellWidget(1, 0, bbtn)
        if not visible:
            nBtn.hide()
        self.buttons[Y].append(nBtn)
        self.tables[Y].addWidget(nBtn)
        if not setting:
            self.wholeData["cell_data"][Y].append([])
            self.main_signal[Y][x].active.emit(True)
            if visible:
                self.logUpdate("Added", self.nameMaker(Y, x))
                
    def returnedData(self, coord, returnedData):
        y, x = coord
        self.wholeData["cell_data"][y][x] = list(returnedData.keys()) #for now
    
    def dataInterpret(self, inp_ret):
        if inp_ret.function not in ["returnsync", "acceptpublish", "acceptsync", "publish", "publisher"]:
            self.logUpdate(inp_ret.name, inp_ret.log, gray)
        if inp_ret.function == "request":
            inp_ret.name = "System"
            inp_ret.function = self.dataInterpret.__name__
            target = self.nameSplitter(inp_ret.meta["to"])
            inp_ret.meta["command"] = "received"
            inp_ret.log = f"Sent {inp_ret.meta['file_name']} to {inp_ret.meta['to']}"
            inp_ret.time = time.time()
            self.main_signal[target[0]][target[1]].command.emit(inp_ret)
        elif inp_ret.function == "returnsync":
            inp_ret.name = "System"
            inp_ret.function = self.dataInterpret.__name__
            target = self.nameSplitter(inp_ret.meta["to"])
            inp_ret.meta["command"] = "acceptsync"
            inp_ret.log = f"Sent sync data to {inp_ret.meta['to']}"
            inp_ret.time = time.time()
            self.main_signal[target[0]][target[1]].command.emit(inp_ret)
        if inp_ret.function in self.events.keys():
            if inp_ret.meta.get("code", "") in self.events[inp_ret.function].keys():
                event = self.events[inp_ret.function][inp_ret.meta["code"]]
                if event[0].lower() == "arrival":
                    if event[1].lower() == "prompt":
                        self.prompt(event[2])
                    elif event[1].lower() == "compare":
                        self.logUpdate("System", f"{event[3]} took {inp_ret.time - event[2]}s", "")
                    del self.events[inp_ret.function][inp_ret.meta["code"]]
                elif event[0].lower() == "list":
                    self.events[inp_ret.function][inp_ret.meta["code"]][5] += 1
                    if event[3] <= self.events[inp_ret.function][inp_ret.meta["code"]][5]:
                        if event[1].lower() == "prompt":
                            self.prompt(event[2])
                        elif event[1].lower() == "compare":
                            self.logUpdate("System", f"{event[4]} took {inp_ret.time - event[2]}s", "")
                        del self.events[inp_ret.function][inp_ret.meta["code"]]
    
    def taskOrganize(self, ran_code):
        tim = datetime.now().strftime("%H:%M:%S.%f")[:-4]
        self.time.setText(f"[{tim}] {ran_code}")
        
    def save(self):
        self.wholeData["log_data"] = self.logList
        for Y in range(self.table_num):
            for X in range(self.colNum[Y]):
                self.main_signal[Y][X].returnData.emit("")
        with open(f"./data/{code}_" + time.strftime("%Y%m%d_%H%M%S") + ".txt", "w", encoding = "utf-8") as sav:
            sav.write(json.dumps(self.wholeData, indent = 4))
        self.logUpdate("Saved", time.strftime("%Y-%m-%d-%H:%M:%S"))
    
    def requestConnect(self, inp_ret):
        y, _ = self.nameSplitter(inp_ret.name)
        requestTo = random.randrange(len(self.main_signal[self.syncData["data_provider"][y]]))
        self.prompt(f"request {self.labels[self.syncData['data_provider'][y]]}#{requestTo} {inp_ret.name} {inp_ret.meta['file_name']}")
        self.logUpdate(inp_ret.name, inp_ret.log, gray)

    def returnNum(self, a):
        for x in self.labels:
            if a.lower() == x.lower() or a.lower() == x[0].lower():
                return self.labels.index(x)
        return len(self.labels) + 1

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
            clas, id_num = (-1, -1)
        
        return (clas, id_num)
    
    def nameMaker(self, y, x):
        return f"{self.labels[y]}_{x}"
    
    def aName(self, name):
        try:
            return self.nameSplitter(name) != (-1, -1)
        except:
            return False
    
    def returnCode(self, command):
        if command in self.usage.keys():
            return f"{command}#{self.functions_count[command]}"
        else:
            return "None#0"
    
    def last_command(self):
        if len(self.inputList) >= abs(self.lastI + 1):
            self.lastI += 1
            self.commandText.setText(self.inputList[-self.lastI][1])
    
    def then_command(self):
        if len(self.inputList) > abs(self.lastI - 1):
            self.lastI -= 1
            self.commandText.setText(self.inputList[-self.lastI][1])
    
    def publisher(self, inp_ret):
        Y, x = self.nameSplitter(inp_ret.name)
        target_layers = [syn for syn in range(len(self.colNum)) if self.syncData["sync"][syn] == Y and type(self.syncData["sync"][syn]) == int]
        for tY in target_layers:
            for tX in range(self.colNum[tY]):
                if not (tX == x and tY == Y):
                    last_update = self.buttons[tY][tX].cellWidget(1, 0).last_update
                    changes = [change for change in inp_ret.meta["edit_list"] if change[0] > last_update]
                    if len(changes) > 0:
                        ret = dataFormat("System", self.publisher.__name__)
                        ret.meta["command"] = "acceptpublish"
                        ret.meta["to"] = self.nameMaker(tY, tX)
                        ret.meta["data"] = {}
                        ret.meta["code"] = inp_ret.meta["code"]
                        ret.meta["last_update"] = inp_ret.meta["last_update"]
                        changed_files = [change[1] for change in changes]
                        setted_changes = list(set(changed_files))
                        ret.meta["edit_list"] = changes
                        for setted in setted_changes:
                            if setted in inp_ret.meta["data"].keys():
                                ret.meta["data"][setted] = inp_ret.meta["data"][setted]
                            elif setted in inp_ret.meta["keys"]:
                                ret.meta["data"][setted] = self.buttons[Y][x].cellWidget(1, 0).data[setted]
                        ret.log = "Published sent to" + ret.meta["to"]
                        ret.time = time.time()
                        self.main_signal[tY][tX].command.emit(ret)
        if inp_ret.meta["code"]:
            report = dataFormat("System", self.publisher.__name__)
            report.meta["code"] = inp_ret.meta["code"]
            report.log = "Publishing completed"
            report.time = time.time()
            self.dataInterpret(report)
    
    def syncer(self, inp_ret):
        Y, x = self.nameSplitter(inp_ret.name)
        if type(self.syncData["sync"][Y]) == int:
            target_layer = self.syncData["sync"][Y]
            requestTo = random.randrange(self.colNum[target_layer])
            ret = dataFormat("System", self.syncer.__name__)
            ret.meta["command"] = "returnsync"
            ret.meta["from"] = inp_ret.name
            ret.meta["to"] = self.nameMaker(target_layer, requestTo)
            ret.meta["code"] = inp_ret.meta["code"]
            ret.log = ret.meta["from"] + " request sync to " + ret.meta["to"]
            ret.time = time.time()
            self.main_signal[target_layer][requestTo].command.emit(ret)
        else:
            ret = dataFormat("System", self.syncer.__name__)
            ret.meta["command"] = "acceptsync"
            ret.meta["from"] = "System"
            ret.meta["to"] = inp_ret.name
            ret.meta["data"] = {}
            ret.meta["last_update"] = 0
            ret.meta["code"] = inp_ret.meta["code"]
            ret.log = "Blank sync"
            ret.time = time.time()
            self.main_signal[Y][x].command.emit(ret)
        
    def esc(self):
        sys.exit()
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MyApp(loading_data, log_dt, input_dt)
    app.exec_()