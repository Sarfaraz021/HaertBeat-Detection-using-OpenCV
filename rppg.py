# rppg.py

from collections import namedtuple
from datetime import datetime

import numpy as np
from PyQt5.QtCore import pyqtSignal, QObject
import mediapipe as mp
import cv2

from camera import Camera
from detector import ROIDetector

RppgResults = namedtuple("RppgResults", ["rawimg",
                                         "roimask",
                                         "landmarks",
                                         "signal",
                                         ])

class RPPG(QObject):

    rppg_updated = pyqtSignal(RppgResults)

    def __init__(self, parent=None, video=1):
        """rPPG model processing incoming frames and emitting calculation
        outputs.

        The signal RPPG.updated provides a named tuple RppgResults containing
          - rawimg: the raw frame from camera
          - roimask: binary mask filled inside the region of interest
          - landmarks: multiface_landmarks object returned by FaceMesh
          - signal: reference to a list containing the signal
        """
        super().__init__(parent=parent)

        self._cam = Camera(video=video, parent=parent)
        self._cam.frame_received.connect(self.on_frame_received)

        self.detector = ROIDetector()
        self.signal = []

    def on_frame_received(self, frame):
        """Process new frame - find face mesh and extract pulse signal.
        """
        rawimg = frame.copy()
        roimask, results = self.detector.process(frame)

        r, g, b, a = cv2.mean(rawimg, mask=roimask)
        self.signal.append(g)

        self.rppg_updated.emit(RppgResults(rawimg=rawimg,
                                           roimask=roimask,
                                           landmarks=results,
                                           signal=self.signal))

    def start(self):
        """Launch the camera thread.
        """
        self._cam.start()

    def stop(self):
        """Stop the camera thread and clean up the detector.
        """
        self._cam.stop()
        self.detector.close()
