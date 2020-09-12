import socketserver
import subprocess
import mysql.connector
import re
import time


def get_ip():
    rawIp = subprocess.check_output("hostname -I", shell=True).decode("utf-8")
    return rawIp.split()[0]


def get_on_sensors():
    onSensors = {}
    db = pdb.cursor()
    db.execute("SELECT * FROM sensors")
    all_sensors = db.fetchall()
    for one_sensor in all_sensors:
        sensor_number = one_sensor[0]
        sql = "SELECT state FROM A" + str(sensor_number) + " ORDER BY id DESC LIMIT 1"
        db.execute(sql)

        status = db.fetchall()
        if status:
            all_status[sensor_number] = status[0][0]
            if status[0][0] != "OFF":
                onSensors[sensor_number] = 5
        else:
            all_status[sensor_number] = -1

    return onSensors


def add_on_sensor(number):
    onSensors[number] = 5
    db = pdb.cursor()
    db.execute("SELECT * FROM sensors")
    result = db.fetchall()


class MyUDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        sensor_number = str(self.request[0].strip())
        sensor_number = int(re.search("[0-9][0-9]", sensor_number)[0])
        from_ip = self.client_address[0]
        # socket = self.request[1]
        # print("{} wrote:".format(from_ip))
        # print(sensor_number)
        if sensor_number in onSensors.keys():
            # in keys
            print()
        else:
            # not in keys
            print("Add - {}".format(sensor_number))
            add_on_sensor(sensor_number)
        print(onSensors)


if __name__ == "__main__":
    ip = get_ip()
    print("Server IP:" + ip)

    pdb = mysql.connector.connect(
        host="localhost",
        user="pletacka",
        password="ladasmolik",
        database="pletacka-ex"
    )

    all_status = {}

    onSensors = get_on_sensors()

    print(onSensors)

    time.sleep(2)

    HOST, PORT = ip, 2727
    with socketserver.UDPServer((HOST, PORT), MyUDPHandler) as server:
        server.serve_forever()
