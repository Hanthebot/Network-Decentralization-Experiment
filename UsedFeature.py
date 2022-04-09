import pyperclip

def p(a):
    print(a.replace("\n\n", "\n"))

def ink(l):
    l = l.split("\n")
    while True:
        for L in l:
            input()
            pyperclip.copy(L)