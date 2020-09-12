import socketserver
import subprocess


def getIp():
    rawIp = subprocess.check_output("hostname -I", shell=True).decode("utf-8")
    return rawIp.split()[0]


class MyUDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print("{} wrote:".format(self.client_address[0]))
        print(data)
        socket.sendto(data.upper(), self.client_address)


if __name__ == "__main__":
    ip = getIp()
    print("Server IP:" + ip)

    HOST, PORT = ip, 2727
    with socketserver.UDPServer((HOST, PORT), MyUDPHandler) as server:
        server.serve_forever()
