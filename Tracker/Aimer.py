from tools import debug

class Aimer:
    """Aim at point from coordinate on screen."""

    ANGLEFILE = "../Arduino/status.txt"

    XOFFSET = 0
    YOFFSET = 90
    
    def __init__(self, name, fov, clen) -> None:

        # Setup Camera Parameters
        self.name = name
        self.fov = fov 
        self.clen = clen

        # Save valid last angles
        self.lastX = 0
        self.lastY = 0

        # Display parameters
        print(
            "-"*15, "\n"
            "Aimer init\n"
            f"  - Name: {name}\n"
            f"  - Field of View: {fov}\n"
            f"  - clen: {clen}\n",
            "-"*15, "\n",
            sep=''
        )

    def get_angle(self, point) -> float:
        """Get of angle to point from center of camera."""
        f = self.fov
        p = point 
        l = self.clen 

        t = -(l * f - 2 * p * f) / (2 * l)

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
        
        with open(self.ANGLEFILE, 'w') as file:
            file.write(f"{x},{y}")
        debug(f"Aimed with position {x}, {y}.")


if __name__ == "__main__":
    aimer = Aimer('', 0, 0)
    aimer.aim(20, 0)