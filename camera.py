# import the necessary packages
import logging,time,cv2,os
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera

# initialize the camera and grab a reference to the raw camera capture
#camera = PiCamera()

filename = "/ramdisk/image.png"
frame_delay = 0.7
NO_FILTER = 0
CANNY = 1
HOUGH_LINES = 2
HOUGH_CIRCLES = 3
ORB_KEYPOINTS = 4
BLOBS = 5
filter_mode = BLOBS

# This function is a hack as there is a bug in openCV 4.0.0 with drawKeypoints
def draw_keypoints(image,kp):
    for kpoint in kp:
      x, y = kpoint.pt
      cv2.circle(image, (int(x), int(y)), 2, color=(0,255,0))
    return image

with PiCamera() as camera:
    orb=cv2.ORB_create()
    blobs=cv2.SimpleBlobDetector_create()

    camera.resolution = (608,400)
    rawCapture = PiRGBArray(camera)
    time.sleep(1)
    now=time.time()
    for foo in camera.capture_continuous(rawCapture, format="bgr"):
        image=rawCapture.array
        if(filter_mode == CANNY): image=cv2.Canny(image,100,200)
        elif(filter_mode == HOUGH_LINES):
          gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
          gray_image = cv2.medianBlur(gray_image,5)
          edges = cv2.Canny(gray_image,50,150,apertureSize=3)
          lines = cv2.HoughLines(edges,1,np.pi/180,200)
          if lines is not None:
              for rho,theta in lines[0]:
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(a))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(a))
                cv2.line(image,(x1,y1),(x2,y2),(0,0,255),2)
        elif(filter_mode == HOUGH_CIRCLES):
          gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
          gray_image = cv2.medianBlur(gray_image,5)
          circles = cv2.HoughCircles(gray_image,cv2.HOUGH_GRADIENT,1,50,param1=50,param2=30,minRadius=0,maxRadius=0)
          circles = np.uint16(np.around(circles))
          if circles is not None:
              for i in circles[0,:]:
                  # draw the outer circle
                  cv2.circle(image,(i[0],i[1]),i[2],(0,255,0),2)
                  # draw the center of the circle
                  cv2.circle(image,(i[0],i[1]),2,(0,0,255),3)
        elif(filter_mode == ORB_KEYPOINTS):
          gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
          gray_image = cv2.medianBlur(gray_image,5)
          kp=orb.detect(gray_image,None)
          kp,des = orb.compute(gray_image, kp)
          draw_keypoints(image,kp)
        elif(filter_mode == BLOBS):
          gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
          gray_image = cv2.medianBlur(gray_image,5)
          kp=blobs.detect(gray_image)
          draw_keypoints(image, kp)
        cv2.imwrite(filename,image)
        if(time.time()-now > frame_delay): print("Frame dropped")
        while(time.time()-now < frame_delay): time.sleep(0.01)
        now=time.time()
        rawCapture.truncate()
        rawCapture.seek(0)


#
# rawCapture = PiRGBArray(camera)
#
# # allow the camera to warmup
# time.sleep(0.1)
#
# # grab an image from the camera
# def captureImage():
#     camera.capture_continuous(rawCapture, format="bgr")
#     image = rawCapture.array
#     return image
#
# if __name__ == "__main__":
#  logger = logging.getLogger()
#  logger.setLevel(logging.INFO)
#  filename = "/ramdisk/image.png"
#  time.sleep(0.1)
#  while True:
#      now=time.time()
#      while(time.time() - now < 0.5): time.sleep(0.01)
#      logging.info("Taking a still and saving to " + filename)
#      image = captureImage()
#      cv2.imwrite(filename,image)
#  os._exit(1)
