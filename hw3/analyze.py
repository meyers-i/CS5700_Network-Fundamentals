import sys
if len(sys.argv) < 3:
    print("Error: Missing data arguments")
    exit()
filename = sys.argv[1]
tcpfilename = sys.argv[2]
dataFile = "data.csv"
if len(sys.argv) == 4:
    dataFile = sys.argv[3]
packet_drops = 0
packetSent = {}
throughputPerSecond = []
throughputPerPacket = []
throughputCount = 1
currentThroughput = 0
latenciesPerPacket = []
currentLatencies = []
latenciesPerSecond = []
seq = {}
totalSize = 0
totalTime = 0
with open(filename) as f:
    lines = f.readlines()
    for line in lines:
        values = line.split()
        packetType = values[4]
        if packetType == "cbr":
            continue
        eventType = values[0]
        time = float(values[1])
        source = values[2]
        destination = values[3]
        packetSize = float(values[5])
        packetId = values[-1]
        sequenceNumber = values[-2]
        if eventType == "d":
            packet_drops +=1
            continue
        if packetType == "tcp":
            if eventType == "+":
                packetSent[(sequenceNumber, source)] = time
        elif packetType == "ack":
            if eventType == "r" and packetSent.get((sequenceNumber, destination)) != None:
                #packet ack arrived at source completing trip
                startTime = packetSent[(sequenceNumber, destination)]
                endTime = time
                totalTime = endTime - startTime
                latenciesPerPacket.append(totalTime)
                throughputPerPacket.append(packetSize/totalTime)
                if time > throughputCount:
                    throughputCount += 1
                    throughputPerSecond.append(currentThroughput)
                    currentThroughput = 0
                    if len(currentLatencies) != 0:
                        latenciesPerSecond.append(sum(currentLatencies)/len(currentLatencies))
                    currentLatencies = []
                else:
                    currentThroughput += packetSize
                    currentLatencies.append(totalTime)
        if eventType == "-":
            if seq.get(sequenceNumber, True):
                totalSize += packetSize
                seq[sequenceNumber] = False
    totalTime = float(lines[len(lines)-1].split()[1])  - float(lines[0].split()[1]) 
if len(latenciesPerPacket) == 0:
    print("No packets were sent")
    exit()
# print("Packet Dropped:", packet_drops)
# print("Throughput over time :", throughputPerSecond)
# print("Throughput per packet:", throughputPerPacket)
# print("Average Bandwidth:", totalSize / totalTime)

# print("End to End Latency Average:", sum(latenciesPerPacket)/len(latenciesPerPacket))
# print("Latencies per second:", latenciesPerSecond)
# print("Latencies per packet:", latenciesPerPacket)
def stringify(l):
    return [str(x) for x in l]
f = open(dataFile,"w+")
f.write("Packets Dropped,{}\n".format(packet_drops))
f.write("Throughput over time,{}\n".format(",".join(stringify(throughputPerSecond))))
f.write("Throughput per packet,{}\n".format(",".join(stringify(throughputPerPacket))))
f.write("Average Bandwith,{}\n".format(totalSize / totalTime))
f.write("End to End Latency Average,{}\n".format(sum(latenciesPerPacket)/len(latenciesPerPacket)))
f.write("Latencies per second,{}\n".format(",".join(stringify(latenciesPerSecond))))
f.write("Latencies per packet,{}\n".format(",".join(stringify(latenciesPerPacket))))

#print("Sequence Numbers:", seq.keys())
window = []
with open(tcpfilename) as tcpf:
    lines = tcpf.readlines()
    for line in lines:
        values = line.split()
        time = float(values[1])
        cwnd = float(values[17])
        window.append([time, cwnd])
f.write("Window over time\n")
for i in window:
    f.write("{},{}\n".format(i[0], i[1]))
# print("Window over time:", window)
f.close()