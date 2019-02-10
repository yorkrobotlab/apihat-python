#!/usr/bin/python
# YRL028 - APIHAT - Python 3 API Version 0.1
#
# Functions for the Adafruit PiOLED [SSD1306_128_32] display
#
# James Hilder, York Robotics Laboratory, Feb 2019

import time, logging, subprocess, Adafruit_SSD1306, os
import settings as s, utils

from PIL import Image, ImageDraw, ImageFont

OLED_BUS = s.OLED_BUS  # The display is attached to bus 8, which translates to bus i2c_8

disp = Adafruit_SSD1306.SSD1306_128_32(rst=None,i2c_bus=OLED_BUS)

# Load default font.
mono_small = ImageFont.truetype('font/mono.ttf',8)
small_font = ImageFont.truetype('font/pixelmix.ttf', 8)
small_font_bold = ImageFont.truetype('font/pixelmix_bold.ttf', 8)
medium_font = ImageFont.truetype('font/hexaberry_font.ttf',16)
large_font = ImageFont.truetype('font/hexaberry_font.ttf',24)
# Good resource for fonts to try: http://www.dafont.com/bitmap.php

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = 128
height = 32
draw_image = Image.new('1', (width, height))

# Initialize library.
def init_display():
    disp.begin()
    # Clear display.
    disp.clear()
    disp.display()

# Send the image to the display.  image is a PIL image, 128x32 pixels.
def display_image(image):
  if(s.DISPLAY_ROTATED): image = image.transpose(Image.ROTATE_180)
  try:
    disp.image(image)
    disp.display()
  except IOError:
    logging.warning("IO Error writing to OLED display")

# Display a warning with specified text
def warning(text):
    draw_image = Image.open("images/warning.pbm")
    draw = ImageDraw.Draw(draw_image)
    draw.text((40,16),text,font=mono_small,fill=255)
    display_image(draw_image)

# Load and display an image
def display_image_file(image_filename):
  image = Image.open(image_filename)
  display_image(image)

def one_line_text(text):
    draw = ImageDraw.Draw(draw_image)
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    draw.text((0,4),text,font=large_font,fill=255)
    display_image(draw_image)

def one_line_text_wrapped(text):
    draw = ImageDraw.Draw(draw_image)
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    lt = len(text)
    if(lt<9): draw.text((0,4),text,font=large_font,fill=255)
    elif(lt<28):
        if(lt>14):
            draw.text((0,0),text[0:14],font=medium_font,fill=255)
            draw.text((0,16),text[14:lt],font=medium_font,fill=255)
        else:
            draw.text((0,8),text,font=medium_font,fill=255)
    else:
        draw.text((0,0),text[0:16],font=mono_small,fill=255)
        end_pos = 32
        if(lt<33): end_pos=lt
        draw.text((0,8),text[16:end_pos],font=mono_small,fill=255)
        if(lt>32):
            end_pos = 48
            if(lt<49): end_pos=lt
            draw.text((0,16),text[32:end_pos],font=mono_small,fill=255)
            if(lt>48):
                end_pos=64
                if(lt<64): end_pos=lt
                draw.text((0,24),text[48:end_pos],font=mono_small,fill=255)
    display_image(draw_image)


# Display two lines of text; max 14 characters per line
def two_line_text(line1_text,line2_text):
    draw = ImageDraw.Draw(draw_image)
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    draw.text((0,0),line1_text,font=medium_font,fill=255)
    draw.text((0,16),line2_text,font=medium_font,fill=255)
    display_image(draw_image)

# Display two lines of text; if either line is longer than 14 characters will shrink font + wrap for that line (32 characters max per line)
def two_line_text_wrapped(line1_text,line2_text):
    draw = ImageDraw.Draw(draw_image)
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    if(len(line1_text)<15):
        draw.text((0,0),line1_text,font=medium_font,fill=255)
    else:
        if(len(line1_text)<17):draw.text((0,0),line1_text,font=mono_small,fill=255)
        else:
            draw.text((0,0),line1_text[0:16],font=mono_small,fill=255)
            draw.text((0,8),line1_text[16:len(line1_text)],font=mono_small,fill=255)
    if(len(line2_text)<15):
        draw.text((0,16),line2_text,font=medium_font,fill=255)
    else:
        if(len(line2_text)<17):draw.text((0,16),line2_text,font=mono_small,fill=255)
        else:
            draw.text((0,16),line2_text[0:16],font=mono_small,fill=255)
            draw.text((0,24),line2_text[16:len(line2_text)],font=mono_small,fill=255)
    display_image(draw_image)

def display_string(d_str):
   draw = ImageDraw.Draw(draw_image)
   split_text=[d_str[i:i+16] for i in range(0, len(d_str), 16)]
   draw.rectangle((0,0,width,height), outline=0, fill=0)
   y_pos = 0
   for line in split_text:
      if y_pos<32:
          draw.text((0,y_pos),line,font=mono_small,fill=255)
      y_pos+=8
   display_image(draw_image)

#Display current system stats (IP, cpu load, temperatures, memory usage)
def display_stats():
    draw = ImageDraw.Draw(draw_image)
    x = 0
    padding = -1
    top = padding
    bottom = height-padding
    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    draw.text((x, top),  ("IP: %s" % utils.get_ip()),  font=small_font, fill=255)
    draw.text((x, top+8),  ("Load: %2.1f%%  MHz: %d" % (utils.get_cpu_load(), utils.get_arm_clockspeed())),  font=small_font, fill=255)
    draw.text((x, top+16),  ("CPU: %2.1fC  GPU:%2.1fC" % (utils.get_cpu_temp(),utils.get_gpu_temp())),  font=small_font, fill=255)
    mem = utils.get_mem_usage()
    draw.text((x, top+24),  ("Mem: %d/%dMB %2.2f%%" % (mem[0],mem[1],mem[2])),  font=small_font, fill=255)
    display_image(draw_image)

#Command line test [will run when display.py is run directly]
if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logging.info("YRL027 Display Test")
    init_display()
    display_image_file("images/yrl-white.pbm")
    time.sleep(0.6)
    display_image_file("images/yrl028-black.pbm")
    time.sleep(0.1)
    display_image_file("images/yrl028-white.pbm")
    time.sleep(0.2)
    display_image_file("images/apihat-black.pbm")
    time.sleep(0.1)
    display_image_file("images/apihat-white.pbm")
    time.sleep(0.8)
    #display_stats()
    two_line_text_wrapped("IP Address:",utils.get_ip())
    os._exit(1)
