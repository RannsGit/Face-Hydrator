import cv2 
import numpy as np
from LogQueue import LogQueue
from Aimer import Aimer
from tools import *

class VideoTracker:

    def __init__(self, cascade_path: str, camera_fov: str, camera_index: int=0) -> None:

        # Get Constants form JSON
        self.SAVED_FRAMES, self.SCALE_FACTOR, self.MIN_NEIGHBORS, self.MIN_SIZE,\
        self.LOSS_CAP = jsonGet("SAVED_FRAMES", "SCALE_FACTOR", 
                                "MIN_NEIGHBORS", "MIN_SIZE", "LOSS_CAP")

       # Setup Classifier
        self.cascade = cv2.CascadeClassifier(cascade_path)

        # Setup Log Queue
        self.xlog = LogQueue(self.SAVED_FRAMES, name='x-axis')
        self.ylog = LogQueue(self.SAVED_FRAMES, name='y-axis')
        self.recStore = LogQueue(1, [Rectangle()])

        # Setup video
        self.video = cv2.VideoCapture(camera_index)
        videoShape = self.get_image().shape

        # Setup Aimer
        self.aimer = Aimer(fov=camera_fov, xLen=videoShape[1],
                           yLen=videoShape[0])

        # Store last predicted triangle
        self.predicted = Rectangle()

        # Track frames where face is lost
        self.lossCount = 0

        # Display parameters
        print(
            "-"*15, "\n"
            "VideoTracker init\n"
            f"  - Cascade Path: {cascade_path}\n"
            f"  - Camera Index: {camera_index}\n"
            f"  - Video Height: {videoShape[0]}\n"
            f"  - Video Width: {videoShape[1]}\n",
            "-"*15, "\n",
            sep=''
        )


    def get_image(self) -> np.ndarray:
        """Get image from video capture device"""
        # Read from video source
        ret, frame = self.video.read()

        # Check for bad frame
        if not ret:
            if DEBUG: debug("VideoTracker.get_image(): Bad Return Code", "red")
            return None

        # Return flipped frame
        return cv2.flip(frame, 1)


    def loop(self) -> None:
        """Loop to get frame and process"""

        debug("-" * 15)  # Denote new loop
        
        
        # -- Process Image --

        # Get frame
        image = self.get_image()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Get faces
        faces = self.get_faces(gray)

        # Track face closest to previous position
        o = self.recStore.end()
        b = Rectangle()
        lowest = 10e6
        for (x, y, w, h) in faces:
            dist = np.sqrt(
                (o.y - y)**2 + (o.x-x)**2
            )
            if dist < lowest:
                lowest = dist 
                b.set(x, y, w, h)


        # -- Validate Face -- 

        valid = True
        noFaces = False

        # Ignore frames without faces
        if b.x == b.y == 0:
            valid = False 
            noFaces = True

        # Sort out too small values
        if b.w * b.h < self.MIN_SIZE ** 2 and not noFaces:
            debug("VideoTracker.loop(): Invalid face: Too Small", "red")
            valid = False 


        # Check for outliers
        elif not noFaces:
            outliers = self.xlog.isOutlier(b.x), self.ylog.isOutlier(b.y)
            if any(outliers):
                msg = "x" if outliers[0] else '' + \
                    " and y" if all(outliers) else '' + \
                    "Y" if outliers[1] else ''
                debug(f"VideoTracker.loop(): Invalid face: {msg} outlier(s)", "red")
                valid = False

                # Track anyways if all is lost
                if self.lossCount >= self.LOSS_CAP:
                   self.xlog.cycle(b.x)
                   self.ylog.cycle(b.y) 
            else:
                self.xlog.cycle(b.x)
                self.ylog.cycle(b.y)

        debug(self.xlog)
        debug(f"VideoTracker.loop(): Face position: ({b.x}, {b.y})")
        # Store good rectangle
        if valid:
            self.recStore.cycle(b)
            self.lossCount = 0

        # Display validity
        if not valid:
            debug("invalid face", "red")
            self.lossCount += 1

        # -- Predict Future Rectangles -- 

        PREDICT_COUNT = 1
        
        recPredict = [] 
        lr = self.recStore.end()  # Reference last good rectangle for size
        xPredict = self.xlog.get_next_values(n=PREDICT_COUNT)
        yPredict = self.ylog.get_next_values(n=PREDICT_COUNT)
        for i in range(PREDICT_COUNT):
            recPredict.append(
                Rectangle(
                    lr.w,
                    lr.h,
                    xPredict[i],
                    yPredict[i]
                )
            )

        # Give up when cap reached
        if not valid and self.lossCount >= self.LOSS_CAP:
            debug("Loss Cap", "red")

            # Destroy all values
            self.xlog.purge()
            self.ylog.purge()

            # Add back last prediction only
            self.xlog.cycle(recPredict[0].x)
            self.ylog.cycle(recPredict[0].y)

        else: # under cap
            # Use prediction if invalid
            if not valid:
                self.xlog.cycle(recPredict[0].x)
                self.ylog.cycle(recPredict[0].y)


        # -- Draw Rectangles --

        if not valid:
            # Draw predictions
            predictColor = (235, 158, 52)
            for i in range(PREDICT_COUNT):
                r = recPredict[i] 
                weight = PREDICT_COUNT - i
                try:
                    cv2.rectangle(image, (r.x, r.y), 
                    (r.x+r.w, r.y+r.h), predictColor, weight)
                except cv2.error as e:
                    debug(f"Experienced {type(e).__name__} on rect draw.")

        # Not Tracking
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2)

        # Currently Tracking
        gcolor = (0, 255, 0) if valid else (255, 0, 0)
        cv2.rectangle(image, (b.x, b.y), (b.x+b.w, b.y+b.h), gcolor, 2)

        # -- Draw crosshair lines --
        s = recPredict[0]

        u = b if valid else s  # Denote best available face with u

        # Vertical
        cv2.line(
            image, 
            (int(u.x + 0.5*u.w), image.shape[0]), 
            (int(u.x + 0.5*u.w), 0), 
            (255, 0, 0), 
            2)

        # Horizontal
        cv2.line(
            image,
            (0, int(u.y + 0.5*u.h)),
            (image.shape[1], int(u.y + 0.5*u.h)),
            (255, 0, 0),
            2
        )

        # -- Get & Display Target Angle -- 

        xTarget = self.aimer.get_angle(u.x, XAXIS)
        yTarget = self.aimer.get_angle(u.y, YAXIS)
        cv2.putText(
            image,
            text=f"xTarget angle: {xTarget}",
            org=(10, 40),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(0, 0, 255),
            thickness=2
        )
        cv2.putText(
            image,
            text=f"yTarget angle: {yTarget}",
            org=(10, 40),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(0, 0, 255),
            thickness=2
        )
        cv2.putText(
            image,
            text=f"Loss Count: {self.lossCount}",
            org=(10, 120),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(0, 0, 255),
            thickness=2
        )
        
        # -- Send angle to aimer --
        self.aimer.aim(0, xTarget)


        # Display the resulting frame
        cv2.imshow('Video', image)

    def get_faces(self, image):
        """Detect faces from image"""

        return self.cascade.detectMultiScale(
            image,
            scaleFactor=self.SCALE_FACTOR,
            minNeighbors=self.MIN_NEIGHBORS, 
            minSize=(self.MIN_SIZE, self.MIN_SIZE),
            flags=cv2.CASCADE_SCALE_IMAGE
        )


    def run(self):
        while True:
            # Escape Sequence
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # Call loop
            self.loop()