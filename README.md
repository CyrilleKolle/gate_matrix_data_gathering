# BLE Sensor data retrieval

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

