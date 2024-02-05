"""BLE Sensor data retrieval

The script will configure the native BLE sensor in central configuration and scan for
the sensor ending with given SENSOR_ID. Once a new sensor is found then initiates the
connection, set the command characteristics values and enable notification service.
All the binary data packet will be parsed and sensor payload objects will be stored
locally and save into a csv file on the  ctrl+c exit signal.

Install Bleak before running the script by

.. code:: bash

    pip install bleak


Usage:

.. code:: bash

    python sensor.py


"""

import sys
import asyncio
import csv
import dataclasses
import logging
import signal
import struct
from datetime import datetime
from functools import reduce
import threading

from bleak import BleakClient
from bleak import _logger as logger
from bleak import discover
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread
from PyQt6.QtCore import QObject, pyqtSignal

from .models import Acceleration
from annotation import AnnotateAccelerometerData

SENSOR_ID = "223430000278"
WRITE_CHARACTERISTIC_UUID = "34800001-7185-4d5d-b431-630e7050e8f0"
NOTIFY_CHARACTERISTIC_UUID = "34800002-7185-4d5d-b431-630e7050e8f0"
DATA_POINTS = []


class DataView:
    def __init__(self, array, bytes_per_element=1):
        """
        bytes_per_element is the size of each element in bytes.
        By default, we assume the array is one byte per element.
        """
        self.array = array
        self.bytes_per_element = 1

    def __get_binary(self, start_index, byte_count, signed=False):
        integers = [self.array[start_index + x] for x in range(byte_count)]
        bytes = [
            integer.to_bytes(self.bytes_per_element, byteorder="little", signed=signed)
            for integer in integers
        ]
        return reduce(lambda a, b: a + b, bytes)

    def get_uint_16(self, start_index):
        bytes_to_read = 2
        return int.from_bytes(
            self.__get_binary(start_index, bytes_to_read), byteorder="little"
        )

    def get_uint_8(self, start_index):
        bytes_to_read = 1
        return int.from_bytes(
            self.__get_binary(start_index, bytes_to_read), byteorder="little"
        )

    def get_uint_32(self, start_index):
        bytes_to_read = 4
        binary = self.__get_binary(start_index, bytes_to_read)
        return struct.unpack("<I", binary)[0]  # <f for little endian

    def get_float_32(self, start_index):
        bytes_to_read = 4
        binary = self.__get_binary(start_index, bytes_to_read)
        return struct.unpack("<f", binary)[0]  # <f for little endian

    def get_int_32(self, start_index):
        bytes_to_read = 4
        binary = self.__get_binary(start_index, bytes_to_read)
        return struct.unpack("<i", binary)[0]  # <f for little endian

    def get_int_arr(self):
        byte_length = len(self.array)
        result = []
        start_index = 6
        bytes_to_read = 4
        number_of_readings = 16
        for index in [
            start_index + bytes_to_read * i for i in range(number_of_readings)
        ]:
            result.append(self.get_int_32(index))
        return result


# @dataclasses.dataclass
# class Acceleration:
#     timestamp: int
#     timestamp_local: str
#     ax: float
#     ay: float
#     az: float
#     fall_state: str

#     def as_csv_field(self):
#         return [self.timestamp, self.timestamp_local, self.ax, self.ay, self.az, self.fall_state]


def save_as_csv():
    with open(f"sensor_data_{datetime.now()}.csv", "w", newline="") as file:
        writer = csv.writer(file)
        head = ["timestamp", "timestamp_local", "ax", "ay", "az", "fall_state"]
        writer.writerow(head)

        for field in DATA_POINTS:
            writer.writerow(field.as_csv_field())


async def run_queue_consumer(queue: asyncio.Queue):
    while True:
        data = await queue.get()
        if data is None:
            save_as_csv()
            logger.info(
                "Got message from client about disconnection. Exiting consumer loop..."
            )
            break
        else:
            # print(data)
            DATA_POINTS.append(data)


async def run_ble_client(end_of_serial: str, queue: asyncio.Queue, data_received_signal: pyqtSignal):
    # Check the device is available
    devices = await discover()
    found = False
    address = None
    for d in devices:
        print("device:", d)
        if d.name and d.name.endswith(end_of_serial):
            print("device found")
            address = d.address
            found = True
            break

    # This event is set if device disconnects or ctrl+c is pressed
    disconnected_event = asyncio.Event()

    def raise_graceful_exit(*args):
        disconnected_event.set()

    def disconnect_callback(client):
        logger.info("Disconnected callback called!")
        disconnected_event.set()

    async def notification_handler(sender, data):
        """Simple notification handler which prints the data received."""
        d = DataView(data)
        # Dig data from the binary
        msg = "Data: ts: {}, ax: {}, ay: {}, az: {}".format(
            d.get_uint_32(2), d.get_float_32(6), d.get_float_32(10), d.get_float_32(14)
        )
        print(msg)

        acc_data = Acceleration(
            timestamp=d.get_uint_32(2),
            timestamp_local=(str(datetime.now())),
            ax=d.get_float_32(6),
            ay=d.get_float_32(10),
            az=d.get_float_32(14),
            fall_state=annotation.fall_state,
        )
        data_received_signal.emit(acc_data)
        # queue message for later consumption
        await queue.put(acc_data)

    if found:
        async with BleakClient(
                address, disconnected_callback=disconnect_callback
        ) as client:

            loop = asyncio.get_event_loop()
            # Add signal handler for ctrl+c
            signal.signal(signal.SIGINT, raise_graceful_exit)
            signal.signal(signal.SIGTERM, raise_graceful_exit)

            # Start notifications and subscribe to acceleration @ 13Hz
            logger.info("Enabling notifications")
            await client.start_notify(NOTIFY_CHARACTERISTIC_UUID, notification_handler)
            logger.info("Subscribing datastream")
            # 1 means Commands.SUBSCRIBE
            # 99 is just a random number for the client_id
            # Meas/ECG/125
            # /Meas/Acc/13
            await client.write_gatt_char(
                WRITE_CHARACTERISTIC_UUID,
                bytearray([1, 99]) + bytearray("/Meas/Acc/13", "utf-8"),
                response=True,
            )

            # Run until disconnect event is set
            await disconnected_event.wait()
            logger.info(
                "Disconnect set by ctrl+c or real disconnect event. Check Status:"
            )

            # Check the connection status to infer if the device disconnected or crtl+c was pressed
            status = client.is_connected
            logger.info("Connected: {}".format(status))

            # If status is connected, unsubscribe and stop notifications
            if status:
                logger.info("Unsubscribe")
                await client.write_gatt_char(
                    WRITE_CHARACTERISTIC_UUID, bytearray([2, 99]), response=True
                )
                logger.info("Stop notifications")
                await client.stop_notify(NOTIFY_CHARACTERISTIC_UUID)

            # Signal consumer to exit
            await queue.put(None)

            await asyncio.sleep(1.0)

    else:
        # Signal consumer to exit
        await queue.put(None)
        print("Sensor  ******" + end_of_serial, "not found!")


async def main(end_of_serial: str, data_received_signal: pyqtSignal):
    queue = asyncio.Queue()
    client_task = run_ble_client(end_of_serial, queue, data_received_signal)
    consumer_task = run_queue_consumer(queue)
    await asyncio.gather(client_task, consumer_task)
    logger.info("Main method done!")


# def run_asyncio_loop(end_of_serial: str):
#     asyncio.run(main(end_of_serial=end_of_serial))
class ThreadManager(QObject):
    data_received = pyqtSignal(Acceleration)

    def __init__(self):
        super().__init__()
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self.run_asyncio_loop)
        self.thread.start()

    def run_asyncio_loop(self):
        asyncio.run(main(SENSOR_ID, self.data_received))

    def stop(self):
        self.thread.quit()
        self.thread.wait()

    def __del__(self):
        self.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    thread_instance = ThreadManager()
    annotation = AnnotateAccelerometerData()
    # thread_instance.data_received.connect(annotation.on_data_received)

    annotation.show()
    logging.basicConfig(level=logging.INFO)
    # asyncio.run(main(SENSOR_ID, thread_instance.data_received))

    app.exec()

    # threading.Thread(target=run_asyncio_loop, args=(SENSOR_ID,), daemon=True).start()
    # sys.exit(app.exec())

"""
Application Flow


Receive data stream at all times
  Keep track of the last 10 seconds of data at all times
  
Once a button is pressed (fall / no fall)
  Save data to new file, mark whether it was a fall or not

"""
