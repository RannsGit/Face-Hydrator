"""
Kyle Tennison
October 25, 2022

Log/Queue for recent frames. Allows estimation for future points and 
outlier analysis."""


import scipy.stats as stat
import numpy as np
from tools import *

class LogQueue:

    def __init__(self, max_size, log=None, name="unnamed", min_size=5) -> None:

        self.CL, self.TOLERANCE = jsonGet(
            "CL", "TOLERANCE"
        )

        self.max_size: int = max_size
        self.min_size: int = min_size
        self._log: list = log if log else []
        self.name = name
        self.justPurged = False

    def end(self):
        """Get end of the queue"""

        return self._log[-1]

    def _push(self, value):
        """Push a value to the beginning of queue"""

        # Push at index 0
        self._log.append(value)

    def cycle(self, value):
        """Cycle new value in and old value out"""

        # Cycle complete when list is full
        if len(self.get_log()) == self.max_size:
            self._push(value)
            self._log.pop(0)
            
        # Don't remove ending member if not full yet
        elif len(self.get_log()) < self.max_size:
            self._push(value)

    @staticmethod
    def derive(_array):
        """Find slope between points. Assumes interval = 1"""

        # Protect real array
        array = _array.copy()

        derived = []
        for i in range(len(array) - 1):
            lower = array[i]
            upper = array[i+1]
            slope = upper-lower
            derived.append(slope)
        return derived


    def isLinearCorrelation(self, _array: list):
        """Tests if there is significant linear correlation"""

        # Check for all equal values
        if all([i == _array[0] for i in _array]): return False

        # Protect real array
        array = np.asarray(_array.copy())

        # Only look at last 5 frames
        if len(array) > 5:
            array = array[-5:]


        r, p = stat.pearsonr(
            [i for i in range(len(array))],
            array
        )

        debug(f"Linear correlation p-value {p}", "blue")

        return p < 1 - self.CL
 
    @staticmethod
    def regress(_array: list):

        # Protect real array
        array = _array.copy()

        r = stat.linregress(
            [i for i in range(len(array))],
            array
        )

        debug(f"y = {round(r.slope,3)}x + {round(r.intercept, 3)}")

        return lambda x: r.slope * x + r.intercept

    def get_log(self):
        """Returns list form of Log"""
        return self._log.copy()

    def _valid_length(self):

        if self.justPurged:
            if len(self._log) == 1:
                self._log = [self._log[0]] * self.min_size
            if len(self._log) > 1:
                self.justPurged = False
        


        if len(self._log) < self.min_size:
            debug(
                f"Log must be at least "
                f"{round(self.min_size * self.max_size, 2)}% full, not "
                f"{round(len(self._log) / self.max_size, 2) * 100}%")
            return False

        if len(self._log) > self.max_size:
            debug(
                f"Log exceeds max length {self.max_size}. Shortening.",
                "red"
            )
            self._log = self._log[-self.max_size:]
            return True

        return True

    
    def get_next_values(self, n=3):
        """Estimate proceeding values
        Parameters:
            n (int): Number of values to estimate
        Return:
            (list): Estimated values, [+1, +2, +3]"""

        # Validate length
        if not self._valid_length(): return [0] * n

        # Protect real log
        log = self.get_log()

        # Declare estimation list
        estimated = []

        # Derive velocity
        debug("Testing derived regression", 'blue')
        velocities = self.derive(log)
        debug(f"Derived velocity: {velocities}")
        
        # Check for linear correlation on velocity
        canRegressVelocity = self.isLinearCorrelation(velocities)

        # ---- IF GOOD FIT FOR VELOCITY ----

        # DO NOT REGRESS DERIVATIVE
        if False:


        # if canRegressVelocity:
            debug("Regressing Velocity", "green")
            # Regress derivative to project velocities
            projectedVelocities = []
            f = self.regress(velocities)
            length = len(velocities)
            for i in range(n):
                projectedVelocities.append(
                    f( length + i )
                )
            velocities.extend(projectedVelocities)  # Add to list of velocities

            # Get y-intercept on displacement curve
            dispY = log[0]
            
            # Integrate velocities w manual riemann sum
            for i in range(len(velocities)):
                estimated.append(
                    int(dispY + velocities[i] + \
                        sum(velocities[:i]))
                    )
            
            # Slice list to only include last n
            estimated = estimated[-n:]

        # ---- END VELOCITY REGRESS ----
        
        # Check for other pattern
        else:
            debug(f"Cannot regress velocities", "red")
            debug("Testing displacement regression", 'blue')

            # Test displacement for linear correlation (const velocity scenario)
            canRegressDisplacement = self.isLinearCorrelation(log)

            # ---- IF GOOD FIT FOR DISPLACEMENT ----
            if canRegressDisplacement:
                debug("Regressing Displacement", "green")
                f = self.regress(log)
                length = len(log)
                for i in range(n):
                    estimated.append(
                        int( f(length + i) )
                    )

            else:
                debug("No Correlation", "yellow")
                for i in range(n):
                    estimated.append(
                        int( np.mean(log) )
                    )

        return estimated
                

    def purge(self):
        """Purge all members from log"""
        self._log = []
        self.justPurged = True
    
    def isOutlier(self, value):
        """Determines if a value is an outlier that should be ignored"""

        log = self.get_log()  # Save space


        if not self._valid_length(): return False

       
        # # Check for regression
        # if self.isLinearCorrelation(log):

        #     debug("Regression = TRUE", 'green')
        #     debug(self)
            
        #     # Create function of best fit
        #     f = self.regress(log)
        #     x = len(log)

        #     # Create validation interval
        #     err = stat.tstd(log) * self.TOLERANCE[1] +self.TOLERANCE[0]
        #     vi = (f(x) - err, f(x) + err)

        #     debug(
        #         f"{self.name}: Regression interval:\t{vi}", "green")


        # else:
            
        #     debug("Regression = FALSE")
       
        #     # Create confidence interval
        #     ci = stat.t.interval(
        #         confidence=self.CL, 
        #         df=len(log) - 1,
        #         loc=np.mean(log),
        #         scale=stat.sem(log))

        #     # Create validation interval
        #     err = stat.tstd(log) * self.TOLERANCE[1] +self.TOLERANCE[0]
        #     vi = (ci[0] - err, ci[1] + err)

        #     debug(f"{self.name}: Mean interval:\t{vi}")

        projected = self.get_next_values(n=1)[0]
        err = projected * self.TOLERANCE[1] + self.TOLERANCE[0]
        vi = (
            projected - err, projected + err
        )

        # Validate

        if vi[0] <= value <= vi[1]:
            return False  # Not an outlier 
        else:
            return True  # Is an outlier

    def __str__(self) -> str:
       return  "{"f"{', '.join([str(round(i, 3)) for i in self.get_log()])}""}"

if __name__ == "__main__":

    import random

    l = LogQueue(8, 
    [10 - (random.random() - 0.5) for i in range(10)])
    l.cycle(2)
    print("estimated: ", l.get_next_values())
    print("exsisting: ", l)