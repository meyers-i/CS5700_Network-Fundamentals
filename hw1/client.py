import socket
import sys
neu_id = sys.argv[-1]
hostname = sys.argv[-2]
port = 27993
if sys.argv[1] == "-p":
    port = int(sys.argv[2])

def solveProblem(num1, oper, num2):
    if oper == "+":
        return str(int(num1) + int(num2))
    if oper == "-":
        return str(int(num1) - int(num2))
    if oper == "*":
        return str(int(num1) * int(num2))
    if oper == "/":
        return str(int(int(num1) / int(num2)))
    raise Exception("unknown operation")

def solve():
    while True:
        data = s.recv(1024)
        data = data.decode()
        if "STATUS" in data:
            data = data.split()
            ans = solveProblem(data[-3], data[-2], data[-1])
            msg = "cs5700fall2018 {}\n".format(ans)
            s.send(str.encode(msg))
        elif "BYE" in data:
            return data.split()[-2]
        else:
            raise Exception("Unknown Message")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((hostname, port))
s.send(str.encode("cs5700fall2018 HELLO {}\n".format(neu_id)))
flag = solve()
print(flag)
