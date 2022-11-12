#!/usr/bin/python3
from datetime import datetime
import time
from PIL import Image, ImageDraw, ImageFont
import adafruit_pcd8544
import board
import busio
import digitalio


class Display:
    'A wrapper class for displaying text to the LCD display. Messages can also be sent to the terminal for development'

    def __init__(self, fontfile, bias=1, contrast=80, console=True):
        # Define LCD input GPIOs
        self.__spi = busio.SPI(board.SCK, MOSI=board.MOSI)
        self.__dc = digitalio.DigitalInOut(board.D23)
        self.__cs = digitalio.DigitalInOut(board.CE0)
        self.__rst = digitalio.DigitalInOut(board.D24)
        self.__display = adafruit_pcd8544.PCD8544(self.__spi, self.__dc, self.__cs, self.__rst)

        # Define display parameters
        self.__display.bias = bias
        self.__display.contrast = contrast
        self.__font = ImageFont.truetype(fontfile, 8)
        self.__nchars = 18  # 18 characters max per line
        self.__console = console
        
        # Turn on the backlight:
        self.__backlight = digitalio.DigitalInOut(board.D22)
        self.__backlight.switch_to_output()
        self.__backlight.value = True

    # Display text to the LCD
    def text(self, text, center=False):
        # enable line-wrapping for long text with unspecified breaks
        if "\n" not in text:
            stext = []
            start, end, l = 0, self.__nchars, 0
            while l <= len(text):
                stext.append(text[start, end])
                start += self.__nchars
                end += self.__nchars
                l += self.__nchars
        else:
            stext = text.split("\n")

        image = Image.new('1', (self.__display.width, self.__display.height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((1, 1, self.__display.width - 1, self.__display.height - 1), outline=255, fill=0)

        if self.__console:
            print("+------------------+")
        for i, line in enumerate(stext):
            if center:  # the text will be centered
                missingChars = self.__nchars - len(line)
                lpad = missingChars // 2
                rpad = missingChars // 2 + missingChars % 2
                line = " " * lpad + line + " " * rpad
                
            else:  # the text will be centered
                missingChars = self.__nchars - len(line)
                rpad = missingChars
                line = line + " " * rpad

            draw.text((5, 5 + i * 10), line, font=self.__font, fill=255)
            if self.__console:
                print("|" + line + "|")
        if self.__console:
            print("+------------------+")

        self.__display.image(image)
        self.__display.show()

    # Display a TRX detection to the LCD
    def detection(self, rfid, t, antenna):
        Y, m, d, H, M, S = time.localtime(t)[0:6]
        self.text(f"LATEST RFID ON\n{Y}-{m}-{d} {H}:{M}:{S}\nA{antenna}: {rfid[:14]}\n{rfid[14:]}")

    # Clear the display
    def clear(self):
        image = Image.new('1', (self.__display.width, self.__display.height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((1, 1, self.__display.width - 1, self.__display.height - 1), outline=255, fill=0)
        self.__display.image(image)
        self.__display.show()
