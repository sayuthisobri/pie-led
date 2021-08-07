import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from datetime import datetime, timedelta

import subprocess

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# Beaglebone Black pin configuration:
# RST = 'P9_12'
# Note the following are only used with SPI:
# DC = 'P9_15'
# SPI_PORT = 1
# SPI_DEVICE = 0

# 128x32 display with hardware I2C:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Note you can change the I2C address by passing an i2c_address parameter like:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)

# Alternatively you can specify an explicit I2C bus number, for example
# with the 128x32 display you would use:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_bus=2)

# 128x32 display with hardware SPI:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# 128x64 display with hardware SPI:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# Alternatively you can specify a software SPI implementation by providing
# digital GPIO pin numbers for all the required display pins.  For example
# on a Raspberry Pi with the 128x32 display you might use:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, dc=DC, sclk=18, din=25, cs=22)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
# font = ImageFont.load_default()
font = ImageFont.truetype("UbuntuMono-Regular.ttf", 14)
headerFont = ImageFont.truetype("UbuntuMono-Regular.ttf", 20)


def execCmd(cmd):
    return subprocess.check_output(cmd, shell=True).decode()


lastFetchIp = None
localIp = execCmd("hostname -I | cut -d\' \' -f1")
lastIp = localIp

showTime = True

def getIp():
    global lastFetchIp, lastIp, showTime
    cmd = "curl --no-progress-meter ifconfig.me"
    if (lastFetchIp is None or (datetime.now() - lastFetchIp) > timedelta(minutes=3)):
        lastIp = execCmd(cmd)
        lastFetchIp = datetime.now()
    return lastIp if showTime else localIp;


def getHeader():
    global showTime
    text = "msms.work"
    if(showTime):
        text = datetime.now().strftime("%I:%M %p")
    showTime = not showTime
    return text

showTemp = False

while True:

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    # cmd = "hostname -I | cut -d\' \' -f1"
    IP = getIp()
    if showTemp:
        cmd = "sensors|grep °C|awk '{printf \"CPU Temp: %s\", $2}'"
    else:
        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
    showTemp = not showTemp
    CPU = execCmd(cmd)
    cmd = "free -m | awk 'NR==2{printf \"Mem: %sMB %.1f%%\", $3,$3*100/$2 }'"
    MemUsage = execCmd(cmd)
    cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
    Disk = execCmd(cmd)

    # Write two lines of text.
    line_height = font.getsize("I")[1]
    header = getHeader()
    w1, h1 = headerFont.getsize(header)
    c_top = top - 3
    draw.text(((128-w1)/2, c_top), header,  font=headerFont, fill=255)
    c_top += h1 + 2
    draw.line((0, c_top, 128, c_top), fill=255)
    draw.text((x, c_top), IP,  font=font, fill=255)
    c_top += line_height
    draw.text((x, c_top), CPU, font=font, fill=255)
    c_top += line_height
    draw.text((x, c_top), MemUsage,  font=font, fill=255)
    c_top += line_height
    draw.text((x, c_top), Disk,  font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(3)
