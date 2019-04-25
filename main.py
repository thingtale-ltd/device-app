# import the necessary packages
from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import json
import numpy as np
import time
import cv2
import os
import time

import tts
import wifi_config
 
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--display", action="store_true", help="Whether or not frames should be displayed")
ap.add_argument("-b", "--box", action="store_true", help="Display bounding boxes around QRCodes")
ap.add_argument("--histogram", action="store_true", help="Display the luminance histogram")

args = vars(ap.parse_args())

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(usePiCamera=True, resolution=(240, 240)).start()

start_time = time.time()

#loop over the frames from the video stream
frame_ctr = 0
while True:
    frame = vs.read()

    # wait for video buffer
    if frame is None:
        time.sleep(0)
        continue

    frame_grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # find the barcodes in the frame and decode each of the barcodes
    barcodes = pyzbar.decode(frame_grayscale)

    # loop over the detected barcodes
    barcode_data_list = []
    for barcode in barcodes:
        # the barcode data is a bytes object so if we want to draw it
        # on our output image we need to convert it to a string first
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type

        if barcodeType != "QRCODE":
            continue
        else:
            if args["box"]:
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.rectangle(frame_grayscale, (x, y), (x + w, y + h), 127, 2)

            barcode_json = json.loads(barcodeData)
            barcode_data_list.append(barcode_json)

    if args["display"]:
        if args["histogram"]:
            nbins = 128
            hist_height, hist_width =  40, 120
            bin_width = int(float(hist_width) / float(nbins) * 2)

            #Create an empty image for the histogram
            hist_img = np.zeros((hist_height, hist_width))

            #Create array for the bins
            bins = np.arange(nbins, dtype=np.uint16).reshape(nbins, 1)

            hist = cv2.calcHist([frame_grayscale], [0], None, [nbins], [0, 256])

            #Loop through each bin and plot the rectangle in white
            pts = np.column_stack((bins, hist))
            for x, y in enumerate(hist):
                cv2.rectangle(hist_img, (x*bin_width, y/hist_height), (x*bin_width + bin_width-1, hist_height), (255), -1)

            #invert histogram (negative colors)
            hist_img = 255 - hist_img

            #insert historgram
            h, w = frame_grayscale.shape
            frame_grayscale[h-hist_height:frame_grayscale.shape[0], w-hist_width:frame_grayscale.shape[1]] = hist_img

        cv2.imshow("video color", frame)
        cv2.imshow("video grayscale", frame_grayscale)
        cv2.waitKey(1)

    for barcode_json in barcode_data_list:
        if barcode_json["type"] == "word":
            #play_cmd = "aplay /home/pi/qrcode/pizerow/sounds/{0}.wav".format(barcode_json["sound"])
            #os.system(play_cmd)

            sound = barcode_json["sound"]
            tts.play("{}; for {}".format(sound[0].upper(), sound.capitalize()))

        elif barcode_json["type"] == "wifi-config":
            wifi_config.update(barcode_json)

    frame_ctr += 1
    bench_freq = frame_ctr / (time.time() - start_time)
    print("avg FPS: {0:.3f}".format(bench_freq))

# close the output CSV file do a bit of cleanup
print("[INFO] cleaning up...")
cv2.destroyAllWindows()
vs.stop()
