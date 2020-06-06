from detection import Point

class Line:

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.m = self.getGradient()
        self.b = self.getIntercept()

    def getGradient(self):
        m = (self.p1.y - self.p2.y)/ (self.p1.x - self.p2.x)
        return m

    def getIntercept(self):
        # y = mx + b
        # b = y - mx
        b = self.p1.y - self.m*self.p1.x
        return b