

## config.json Variables 

### VideoTracker

FOV             : Field of View for video input device
CASC_PATH       : Local path to cascade xml
SAVED_FRAMES    : Backlog frames for estimation
SCALE_FACTOR    : Scale factor used for opencv detection
MIN_NEIGHBORS   : Minimum neighbor requirement for cv2 scan
MIN_SIZE        : Minimum face size for 
LOSS_CAP        : Number of lost frames to continue estimation until giving up

### Aimer

ANGLE_FILE      : Buffer file for angle communication
XOFFSET         : Degree offset for X axis
YOFFSET         : Degree offset for Y axis
XSCALE          : Scale factor for X axis; used for tuning
YSCLAE          : Scale factor for Y axis; used for tuning

### LogQueue

CL              : Confidence level for linear correlation
TOLERANCE       : Tolerance for outliers [Percent tolerance, Pixel tolerance]