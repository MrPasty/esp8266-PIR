# Basic PIR - listens for the ON command and then starts monitoring for movement
#             when detected updates a mqtt topic which can be used for automation
#             When turned off does not look for movement
#
# Usage:      Designed to be only active at night - this should toggle the ON/OFF
#             device should remain in deep sleep till needed - working on this
#
#
# Pins:       ground of esp to ground of PIR, VU from ESP to VIN on PIR, D1 on
#             ESP to Data on PIR.  5V
#


import esp, machine, ConnectWiFi, time
from machine import Pin
from umqtt.simple import MQTTClient

# Input pin D1 on ESP
INPUTPIN = 5

# Connect to Wifi
ConnectWiFi.connect()

# configure RTC.ALARM0 to be able to wake the device
rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

# check if the device woke from a deep sleep
if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print('woke from a deep sleep')

#Define pins for PIR - D1 on ESP
pin = machine.Pin(INPUTPIN, machine.Pin.IN, machine.Pin.PULL_UP)


# Set up MQTT
SERVER = "xx.xx.xx.xx"
PORT = 1883
CLIENT_ID = "PIR1_SENSOR"
SUBTOPIC = "PIR1_cmd"
PUBTOPIC = "PIR1_state"
PUBTOPIC2 = "PIR1_sleep"
USER = "****"
PASSWORD = "****"
state = "off"
motiondetected = 0


def sub_cb(topic, msg):
    global state, motiondetected, updatestate
    print((topic, msg))
    command = msg.decode('ASCII') # convert bytestring back to string
    channel = topic.decode('ASCII') # convert bytestring back to string
    
    # CHECK FOR TOPIC AND HANDLE ACCORDINGLY
    if channel == "PIR1_cmd":
        if command == "on":
            state = "on"
            print("Turned on")
        if command == "off":
            state = "off"
            print("Turned off")
            motiondetected = 0

    if channel == "PIR1_state":
        if command == "on":
            motiondetected = 1
        if command == "off":
            motiondetected = 0


def main(server=SERVER, port=PORT, pwd=PASSWORD, user=USER):
    c = MQTTClient(CLIENT_ID, server, port, user, pwd)
    # Subscribed messages will be delivered to this callback
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(SUBTOPIC) # where we check if the script should run or not
    c.subscribe(PUBTOPIC) # where we see if motion is active or not
    c.publish(PUBTOPIC,b"off") # Set default status of motion to deactivated
    print("Connected to %s, subscribed to %s and %s topic" % (server, SUBTOPIC, PUBTOPIC))

    try:
        while 1:
            global state, motiondetected, updatestate
            c.wait_msg()
            while state == "on":
                if pin.value() == 1 and motiondetected == 0:
                    print("Motion Detected")
                    c.publish(PUBTOPIC,b"on")
                    motiondetected = 1
                c.check_msg()

                if pin.value() == 0 and motiondetected == 1:
                    print("Resetting sensor state")
                    c.publish(PUBTOPIC,b"off")
                    motiondetected = 0

            # put the device to sleep
            # Set wake alarm for 30 mins
            print("Going to sleep")
            c.publish(PUBTOPIC2, b"sleeping")
            time.sleep(2)
            rtc.alarm(rtc.ALARM0, 1800000)
            machine.deepsleep()



    finally:
        c.disconnect()


if __name__ == "__main__":
    main()

