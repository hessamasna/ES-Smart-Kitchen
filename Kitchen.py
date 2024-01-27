import RPi.GPIO as GPIO
from time import time, sleep
from pushover import Pushover
import serial


ser = serial.Serial('/dev/rfcomm0')
ser.isOpen()

po = Pushover("aamiva5quebo1dqxjyteg9eva3nfva")
po.user("ubfkda8re4pyrf3htg4cxdxu1cjz1b")
msg = po.msg("")
msg.set("title", "Kitchen alert!!!")

ser.write(b'Hello kitchen. \r\n')

# Set GPIO mode
GPIO.setmode(GPIO.BCM)

# Set GPIO pins
WATER_SENSOR_PIN = 17  # water sensor GPIO
PIR_SENSOR_PIN = 18    # PIR motion sensor GPIO
MQ_SENSOR_DO_PIN = 22  # Fire sensor GPIO
TOUCH_SENSOR_PIN = 26  # Touch sensor GPIO
LED_PIN = 16 #LED

# Set up GPIO pins
GPIO.setup(WATER_SENSOR_PIN, GPIO.IN)
GPIO.setup(PIR_SENSOR_PIN, GPIO.IN)
GPIO.setup(MQ_SENSOR_DO_PIN, GPIO.IN)
GPIO.setup(TOUCH_SENSOR_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)

def waitForResponse(): 
    status = 'offline'
    while status != 'check':
        ser.write(b'you should check kitchen first to active sensores again !!! \r\n ( type "check" to active sensores again) \r\n')
        print(f"status is {status}!, wait to check and ative sensors again")
        status = ser.readline().decode("utf-8").strip()
    print('sensores are online now!!')
    ser.write(b'sensores are online now!! \r\n')
    


def read_water_sensor():
    return GPIO.input(WATER_SENSOR_PIN)

def read_pir_sensor():
    return GPIO.input(PIR_SENSOR_PIN)
    
def read_mq_sensor():
    return GPIO.input(MQ_SENSOR_DO_PIN)

def read_touch_sensor():
    return GPIO.input(TOUCH_SENSOR_PIN)


def timer(duration):
    start_time = time()
    GPIO.output(LED_PIN, GPIO.HIGH)
    
    print(f"Turn on light for 10 seconds")
    
    while True:
        elapsed_time = time() - start_time
        print(f"Elapsed Time: {elapsed_time:.0f} seconds")

        if elapsed_time >= duration:
            break
        
        sleep(1)
        
    GPIO.output(LED_PIN, GPIO.LOW)
    print(f"Turn off light")

if __name__ == "__main__":
    try:
        pir_triggered_time = None

        while True:
            water_status = read_water_sensor()
            pir_status = read_pir_sensor()
            mq_digital_value = read_mq_sensor()
            touch_status = read_touch_sensor()
            
            if touch_status == GPIO.HIGH:
                if water_status == GPIO.LOW:
                    print("send message to market")
                    msg = po.msg("hi market, we are out of water!!!")
                    po.send(msg)
            
            if water_status == GPIO.HIGH:
                print("Water detected!")
            else:
                print("No water detected.")
                #msg = po.msg("No water detected. check water")
                #po.send(msg)
#                 ser.write(b'No water detected. check water. \r\n')
#                 waitForResponse()

            if pir_status == GPIO.HIGH:
                print("Motion detected.")
                ser.write(b'Motion detected. \r\n')
                msg = po.msg("Motion detected.")
                po.send(msg)
                # Turn on light for 10 seconds
                timer(10)
                waitForResponse()
            else:
                print("No motion detected.")
            
            #madon
            if mq_digital_value != GPIO.HIGH:
                print("Fire or gas detected!")
                ser.write(b'Fire or gas detected! check kitchen. \r\n')
                msg = po.msg("Fire or gas detected! check kitchen")
                po.send(msg)
                waitForResponse()
            else:
                print("No fire or gas detected.")
                
            sleep(1)

    except KeyboardInterrupt:
        GPIO.cleanup()


