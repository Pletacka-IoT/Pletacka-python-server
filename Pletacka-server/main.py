import socketserver
import subprocess
import mysql.connector
import re
import time
import threading


class MyUDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        # separate number from message
        sensor_number = str(self.request[0].strip())
        sensor_number = int(re.search(r'\d+', sensor_number)[0])

        from_ip = self.client_address[0]

        # check that sensor is in on sensors
        if sensor_number in onSensors.keys():
            reset_cutdown(sensor_number)
        else:
            # check that sensor is in database
            if sensor_number in all_sensors_status.keys():
                # add sensor in on sensors
                print("Add - {}".format(sensor_number))
                reset_cutdown(sensor_number)
            else:
                # not existting sensor
                print("ERROR - adding unexisting sensor -> {}".format(sensor_number))


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
            all_sensors_status[sensor_number] = status[0][0]
            if status[0][0] != "OFF":
                onSensors[sensor_number] = 10
        else:
            all_sensors_status[sensor_number] = -1

    return onSensors


def reset_cutdown(number):
    onSensors[number] = 10


def cutdown_old():
    for sensor in onSensors:
        if onSensors[sensor] > 2:
            onSensors[sensor] = onSensors[sensor] - 1
        elif onSensors[sensor] == -1:
            x = ""
        else:
            onSensors[sensor] = -1
            print("Remove - {}".format(sensor))

    print(onSensors)
    cutdowner = threading.Timer(3, cutdown_old).start()


if __name__ == "__main__":
    ip = get_ip()
    print("Server IP:" + ip)
    print("Read from DB: ", end='')

    pdb = mysql.connector.connect(
        host="localhost",
        user="pletacka",
        password="ladasmolik",
        database="pletacka-ex"
    )

    all_sensors_status = {}

    onSensors = get_on_sensors()

    cutdown_old()

    HOST, PORT = ip, 2727
    with socketserver.UDPServer((HOST, PORT), MyUDPHandler) as server:
        server.serve_forever()

# //To do
# - kontrola existence senzoru
# - odesilani do databaze
# - autostartup malina
# - prejmenovat databaze
