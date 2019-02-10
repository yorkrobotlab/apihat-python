# import the necessary packages
import logging,time,cv2,os
from picamera.array import PiRGBArray
from picamera import PiCamera

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
rawCapture = PiRGBArray(camera)

# allow the camera to warmup
time.sleep(0.1)

# grab an image from the camera
def captureImage():
    camera.capture(rawCapture, format="bgr")
    image = rawCapture.array
    return image

if __name__ == "__main__":
 logger = logging.getLogger()
 logger.setLevel(logging.INFO)
 filename = "/ramdisk/image.jpg"
 time.sleep(0.1)
 logging.info("Taking a still and saving to " + filename)
 image = captureImage()
 cv2.imwrite(filename,image)
 os._exit(1)
