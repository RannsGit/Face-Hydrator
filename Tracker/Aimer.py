"""
Kyle Tennison
October 24, 2022

Aimer. Updates positions in ANGLEFILE to reflect the desired servo angles.
Called from VideoTracker."""


from tools import *

class Aimer:
    """Aim at point from coordinate on screen."""

    ANGLE_FILE = jsonGet("ANGLE_FILE")
    XOFFSET = 90     # X axis offset
    YOFFSET = 90    # Y axis offset

    ANGLE_FILE, XOFFSET, YOFFSET, XSCALE, YSCALE = jsonGet(
        "ANGLE_FILE", "XOFFSET", "YOFFSET", "XSCALE", "YSCALE"
    )
    
    def __init__(self, fov:int, xLen:int, yLen:int) -> None:
        """Setup aimer:
        Parameters:
            fov (int)   - Camera FOV
            xLen (int) - x-length of image (pixels)
            yLen (int) - y-length of image (pixels)
            """

        # Setup Camera Parameters
        self.fov = fov 
        self.xLen = xLen
        self.yLen = yLen

        # Save valid last angles
        self.lastX = 0
        self.lastY = 0

        # Display parameters
        print(
            "-"*15, "\n"
            "Aimer init\n"
            f"  - Field of View: {fov}\n"
            f"  - xLen: {xLen}\n",
            f"  - yLen: {yLen}\n",
            "-"*15, "\n",
            sep=''
        )

    def get_angle(self, point, axis) -> float:
        """Get of angle to point from center of camera.
        Parameters:
            point: Coordinate of point on axis
            axis:  axis ID of choice"""
        f = self.fov
        p = point 
        l = self.xLen if axis == 0xA else self.yLen

        t = (-(l * f - 2 * p * f) / (2 * l)) * \
            self.XSCALE if axis == 0xA else self.YSCALE

        return round(t, 2)

    def aim(self, x, y):
        """Update aimer file to newest position"""
        assert all([isinstance(i, (int, float)) for i in (x,y)]), \
            "Cannot aim non-numeric type"

        # Convert to integer if necessary
        if isinstance(x, float):
            x = round(x)
        if isinstance(y, float):
            y = round(y)

        # Apply offsets
        x = x + self.XOFFSET
        y = y + self.YOFFSET

        # Force range
        if not 0 <= x <= 180:
            print("x out of range:", x)
            x = self.lastX
        else:
            self.lastX = x
        if not 0 <= y <= 180:
            print("y out of range:", y)
            y = self.lastY
        else:
            self.lastY = y
        
        with open(self.ANGLE_FILE, 'w') as file:
            file.write(f"{x},{y}")
        debug(f"Aimed with position {x}, {y}.")


if __name__ == "__main__":
    aimer = Aimer('', 0, 0)
    aimer.aim(20, 0)