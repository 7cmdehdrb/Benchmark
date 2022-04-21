import threading
import time
import datetime
import wmi


idx = 0


class Data(object):
    def __init__(self, idx, sensor):
        self.idx = idx
        self.identifier = str(sensor.Identifier)
        self.name = str(sensor.Name)
        self.sensor_type = str(sensor.SensorType)
        self.value = int(sensor.Value)
        # self.val_max = float(sensor.Max)
        # self.val_min = float(sensor.Min)


class CPU(Data):
    def __init__(self, idx, sensor, tag):
        super().__init__(idx, sensor)
        self.tag = tag

    def find(self, tag):
        if self.tag == tag:
            return True

        return False


def isSameData(cpu1, cpu2):
    if cpu1.idx != cpu2.idx:
        return False

    if cpu1.name != cpu2.name:
        return False

    if cpu1.sensor_type != cpu2.sensor_type:
        return False

    if cpu1.value != cpu2.value:
        return False

    return True


def getData(w):
    global idx

    result = []

    infos = w.Sensor()

    for sensor in infos:

        if (
            sensor.SensorType == "Clock"
            or sensor.SensorType == "Load"
            or sensor.SensorType == "Temperature"
        ):

            try:
                data = Data(sensor=sensor, idx=idx)
                if data.name.startswith("CPU"):
                    if "Total" in str(data.name) or "#" in str(data.name):
                        # CPU Total or CPU Core #n
                        data = CPU(sensor=sensor, tag=data.name.split(" ")[-1], idx=idx)

                        if len(result) == 0:
                            result.append(data)

                        else:
                            temp = True
                            for i in result:
                                if isSameData(i, data) is True:
                                    temp = False
                                    break

                            if temp is True:
                                result.append(data)
                                # print(sensor)

            except AttributeError as ae:
                print(ae)
                print("Attribute Error")
                continue
            except Exception as ex:
                print(ex)
                print("ERROR!!!")

    return result


def writeCSV(file, data, idx):
    with open(file, "a") as csvfile:
        for d in data:
            text = ""
            text += str(idx)
            text += ","
            text += d.name
            text += ","
            text += d.tag
            text += ","
            text += d.sensor_type
            text += ","
            text += str(d.value)
            text += "\n"
            csvfile.write(text)


if __name__ == "__main__":

    w = wmi.WMI(namespace="root\OpenHardwareMonitor")

    file_name = (
        str(datetime.datetime.now()).replace(":", "-").replace(" ", "-").split(".")[0]
        + ".csv"
    )

    print(file_name)

    while True:
        data = getData(w)
        writeCSV(file=file_name, data=data, idx=idx)
        print("Logging... %d" % idx)

        idx += 1
