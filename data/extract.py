import glob, json, sys, os

direc = "."
if len(sys.argv) > 1:
    if os.path.exists(sys.argv[1] + "/"):
        direc = sys.argv[1]
lis = glob.glob(direc+"/*.txt")
g = {}
for l in lis:
    with open(l, 'r') as fil:
        total_data = json.load(fil)
    loading_data = total_data['table_data']
    log_dt = total_data.get('log_data', [])
    g[l] = []
    for log in log_dt:
        if len(log[2].split(" ")) > 2:
            if log[2].split(" ")[1] == "took":
                print(l, log[2].split(" ")[2].replace("s",""))
                g[l].append(log[2].split(" ")[2].replace("s",""))
    print("")

for l in lis:
    for G in g[l]:
        print(G)
    print("")