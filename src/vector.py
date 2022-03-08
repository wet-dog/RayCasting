import math


class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        """Return the vector of two vectors added together."""
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """Return the vector of one vector subtracted from another."""
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        """
        If two vectors are multiplied together return their dot product.
        Otherwise return a vector multiplied by a scalar value.
        """
        if type(self) == type(other):
            return self.dot(other)
        elif isinstance(other, (int, float)):
            return Vector(self.x*other, self.y*other)

    def __rmul__(self, other):
        """
        Perform __mul__ if the format is x * Vector to get the same
        behaviour as Vector * x.
        """
        return self.__mul__(other)

    def __div__(self, other):
        """Return a vector divided by a scalar value."""
        if isinstance(other, (int, float)):
            return Vector(self.x/other, self.y/other)

    def dot(self, other):
        """Return the dot product of two vectors."""
        return self.x*other.x + self.y*other.y

    def mag(self):
        """Return the magnitude of a vector."""
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        """Normalize a vector."""
        mag = self.mag()
        normalized_x = self.x / mag
        normalized_y = self.y / mag
        self.x = normalized_x
        self.y = normalized_y

    def coords(self):
        """Return the x and y components of the vector as a tuple pair."""
        return self.x, self.y

    def round(self):
        """
        Return a new vector with the x and y components of the original vector
        rounded to the nearest integer.
        """
        return Vector(int(self.x), int(self.y))

    @classmethod
    def from_angle(cls, angle):
        """Create a vector given an angle."""
        return cls(math.cos(angle), math.sin(angle))
