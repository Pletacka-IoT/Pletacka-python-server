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
            if onSensors[sensor_number] == -1:
                # print("\nAdd again")
                sensor_add_state(sensor_number, "ON")
                all_sensors_status[sensor_number] = "ON"
            reset_cutdown(sensor_number)



        else:
            # check that sensor is in database
            if sensor_number in all_sensors_status.keys():
                # add sensor in on sensors
                # print("\nAdd")
                sensor_add_state(sensor_number, "ON")
                all_sensors_status[sensor_number] = "ON"
                reset_cutdown(sensor_number)
            else:
                # not existting sensor
                print("\nERROR - adding unexisting sensor -> {} -> {}".format(sensor_number, get_tiime()))


def get_tiime():
    return time.strftime("%H:%M:%S", time.gmtime())


def get_ip():
    rawIp = subprocess.check_output("hostname -I", shell=True).decode("utf-8")
    return rawIp.split()[0]


def get_on_sensors():
    onSensors = {}
    pdb = mysql.connector.connect(**config)
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
                # print("\nRemove")
                onSensors[sensor_number] = max_watchdog
        else:
            all_sensors_status[sensor_number] = -1

    pdb.disconnect()
    return onSensors


def reset_cutdown(sensor_number):
    onSensors[sensor_number] = max_watchdog


def cutdown_old():
    for sensor in onSensors:
        if onSensors[sensor] > 2:
            onSensors[sensor] = onSensors[sensor] - 1
        elif onSensors[sensor] == -1:
            x = ""
        else:
            # Turn off
            onSensors[sensor] = -1
            sensor_add_state(sensor, "OFF")
    # print(onSensors)
    print("\r{} -> {}".format(onSensors, get_tiime()), end="")
    cutdowner = threading.Timer(speed_watchdog_s, cutdown_old).start()


# add
def sensor_add_state(sensor_number, state):
    if all_sensors_status[sensor_number] != state:
        pdb = mysql.connector.connect(**config)
        db = pdb.cursor()
        sql = "INSERT INTO `A" + str(sensor_number) + "` (`state`) VALUE ('" + str(state) + "')"
        db.execute(sql)
        pdb.commit()
        all_sensors_status[sensor_number] = state
        print("\n   {} - {} -> {}".format(state.capitalize(), sensor_number, get_tiime()))
        pdb.disconnect()
    else:
        print(
            "\nRemove -> Nothing to change - {} -> {}".format(sensor_number, get_tiime()))


if __name__ == "__main__":
    ip = get_ip()
    print("Server IP:" + ip)
    print("Read from DB: ", end='')

    config = {
        'user': 'pletacka',
        'password': 'ladasmolik',
        'host': 'localhost',
        'port': '3306',
        'database': 'Pletacka-IoT',
        'raise_on_warnings': True, }

    # pdb = mysql.connector.connect(**config)



    # pdb = mysql.connector.connect(
    #     host="localhost",
    #     user="pletacka",
    #     password="ladasmolik",
    #     database="Pletacka-IoT"
    # )
    max_watchdog = 6
    speed_watchdog_s = 4

    all_sensors_status = {}

    onSensors = get_on_sensors()

    cutdown_old()

    HOST, PORT = ip, 2727
    with socketserver.UDPServer((HOST, PORT), MyUDPHandler) as server:
        server.serve_forever()
