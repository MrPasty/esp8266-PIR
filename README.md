# esp8266-PIR
PIR Sensor for ESP8266

Language:
micropython

Overview:
This code will connect to a MQTT server and listen to see if the sensor should be active, if it is the PIR sensor is enabled and triggers when motion detected.  If the sensor is not set to enabled it enters deep sleep for 30 minutes before restarting and checking again.

Purpose:
Designed to be used in conjunction with Home Assistant (HA), I have a automation which turns on the sensor at midnight and off again at 5am, if motion is detected it publishes 'on' to an mqtt topic which an HA automation is listening for and turns on a light for a period of time and then turns it off again.  I use this to turn on a lamp in the night should anyone go downstairs to the kitchen etc so no need to fumble around in the dark for a light switch.

Details of how to connect the PIR sensor are in the main.py

Feel free to modify and improve as this is my first attempt at micropython and I am not a coder.
