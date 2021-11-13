from which_pyqt import PYQT_VER

if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
    from PyQt4.QtCore import QLineF, QPointF, QObject
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time

# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25


#
# This is the class you have to complete.
#


class ConvexHullSolver(QObject):

    # Class constructor
    def __init__(self):
        super().__init__()
        self.pause = False

    # Some helper methods that make calls to the GUI, allowing us to send updates
    # to be displayed.

    def showTangent(self, line, color):
        self.view.addLines(line, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self, line, color):
        self.showTangent(line, color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self, polygon):
        self.view.clearLines(polygon)

    def showText(self, text):
        self.view.displayStatusText(text)

    # This is the method that gets called by the GUI and actually executes
    # the finding of the hull
    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert (type(points) == list and type(points[0]) == QPointF)

        t1 = time.time()
        points.sort(key=lambda x: x.x())  # O(nlogn)
        t2 = time.time()

        t3 = time.time()
        polygon = self.get_polygon(points)  # O(nlogn)
        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon, RED)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4 - t3))

    # takes the points in the convex hull
    # returns the lines in the convex hull
    def get_polygon(self, points):  # O(nlogn)
        hull = self.dc_convex_hull_solver(points)  # O(nlogn)
        lines = []
        i = 0
        while i < hull.length():  # O(n)
            p1 = hull.getPoint(i % hull.length())
            p2 = hull.getPoint((i + 1) % hull.length())
            line = QLineF(p1, p2)
            lines.append(line)
            i = i + 1
        return lines

    # takes a list of points
    # returns convex hull
    def dc_convex_hull_solver(self, points):  # 2T(n/2)+O(n) = O(nlogn)
        if len(points) == 1:
            return Hull(points)

        mid = len(points) // 2
        L, R = points[:mid], points[mid:]

        points_left = self.dc_convex_hull_solver(L)
        points_right = self.dc_convex_hull_solver(R)
        return self.combine(points_left, points_right)

    # takes two points
    # returns slope
    def find_slope(self, p, q):
        return (q.y() - p.y()) / (q.x() - p.x())

    # takes left and right hull
    # returns indices of upper tangent
    def find_upper_tangent(self, L, R):  # O(n)
        p, q = L.getRightmost(), R.getLeftmost()
        temp = Tangent(L.getPoint(p), R.getPoint(q))
        done = 0
        while not done:  # O(n)
            done = 1
            r = p - 1
            while self.find_slope(L.getPoint(r), R.getPoint(q)) < self.find_slope(temp.p, temp.q):
                temp = Tangent(L.getPoint(r), R.getPoint(q))
                p = r
                r = p - 1
                done = 0
            r = q + 1
            while self.find_slope(L.getPoint(p), R.getPoint(r)) > self.find_slope(temp.p, temp.q):
                temp = Tangent(L.getPoint(p), R.getPoint(r))
                q = r
                r = q + 1
                done = 0
        return p, q

    # takes left and right hull
    # returns indices of lower tangent
    def find_lower_tangent(self, L, R):  # O(n)
        p, q = L.getRightmost(), R.getLeftmost()
        temp = Tangent(L.getPoint(p), R.getPoint(q))
        done = 0
        while not done:  # O(n)
            done = 1
            r = p + 1
            while self.find_slope(L.getPoint(r), R.getPoint(q)) > self.find_slope(temp.p, temp.q):
                temp = Tangent(L.getPoint(r), R.getPoint(q))
                p = r
                r = p + 1
                done = 0
            r = q - 1
            while self.find_slope(L.getPoint(p), R.getPoint(r)) < self.find_slope(temp.p, temp.q):
                temp = Tangent(L.getPoint(p), R.getPoint(r))
                q = r
                r = q - 1
                done = 0
        return p, q

    def combine(self, L, R):  # O(n)
        # find indices of tangents
        x, y = self.find_upper_tangent(L, R)  # O(n)
        v, w = self.find_lower_tangent(L, R)  # O(n)

        # get list of points in subhull starting at upper tangent and moving clockwise
        points = R.getPoints(y, w) + L.getPoints(v, x)  # O(n)
        return Hull(points)


class Hull:
    # points is an array of QPointF's
    def __init__(self, points):
        super().__init__()
        self.points = points

    # takes a start and stop index
    # returns a list of points between start and stop indices
    def getPoints(self, start, stop):  # O(n)
        arr = [self.points[start % len(self.points)]]
        i = (start + 1) % len(self.points)
        while i != (stop + 1) % len(self.points):
            arr.append(self.points[i % len(self.points)])
            i = (i + 1) % len(self.points)
        return arr

    # returns a point at specified index
    def getPoint(self, i):
        i = i % len(self.points)
        return self.points[i]

    # returns leftmost point
    def getLeftmost(self):
        lm = min(self.points, key=lambda x: x.x())
        return self.points.index(lm)

    # returns rightmost point
    def getRightmost(self):
        rm = max(self.points, key=lambda x: x.x())
        return self.points.index(rm)

    # returns number of points in hull
    def length(self):
        return len(self.points)


class Tangent:
    # contains two points
    def __init__(self, p, q):
        super().__init__()
        self.p = p
        self.q = q
