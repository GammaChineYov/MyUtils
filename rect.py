class Rect:
    def __init__(self, center=(0, 0), width=1, height=1):
        self._center_x, self._center_y = center
        self._width = width
        self._height = height
        self._update_boundaries()

    def _update_boundaries(self):
        half_width = self._width / 2
        half_height = self._height / 2
        self._xmin = self._center_x - half_width
        self._xmax = self._center_x + half_width
        self._ymin = self._center_y - half_height
        self._ymax = self._center_y + half_height

    @property
    def center_x(self):
        return self._center_x

    @center_x.setter
    def center_x(self, value):
        self._center_x = value
        self._update_boundaries()

    @property
    def center_y(self):
        return self._center_y

    @center_y.setter
    def center_y(self, value):
        self._center_y = value
        self._update_boundaries()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if value < 0:
            raise ValueError("Width must be non-negative.")
        self._width = value
        self._update_boundaries()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if value < 0:
            raise ValueError("Height must be non-negative.")
        self._height = value
        self._update_boundaries()

    @property
    def xmin(self):
        return self._xmin

    @xmin.setter
    def xmin(self, value):
        if value >= self.xmax:
            raise ValueError("xmin must be less than xmax.")
        self._width = self.xmax - value
        self._center_x = (self.xmin + self.xmax) / 2
        self._update_boundaries()

    @property
    def xmax(self):
        return self._xmax

    @xmax.setter
    def xmax(self, value):
        if value <= self.xmin:
            raise ValueError("xmax must be greater than xmin.")
        self._width = value - self.xmin
        self._center_x = (self.xmin + self.xmax) / 2
        self._update_boundaries()

    @property
    def ymin(self):
        return self._ymin

    @ymin.setter
    def ymin(self, value):
        if value >= self.ymax:
            raise ValueError("ymin must be less than ymax.")
        self._height = self.ymax - value
        self._center_y = (self.ymin + self.ymax) / 2
        self._update_boundaries()

    @property
    def ymax(self):
        return self._ymax

    @ymax.setter
    def ymax(self, value):
        if value <= self.ymin:
            raise ValueError("ymax must be greater than ymin.")
        self._height = value - self.ymin
        self._center_y = (self.ymin + self.ymax) / 2
        self._update_boundaries()

    @property
    def min_coord(self):
        return (self.xmin, self.ymin)

    @min_coord.setter
    def min_coord(self, value):
        xmin, ymin = value
        if xmin >= self.xmax or ymin >= self.ymax:
            raise ValueError("Min coord must be within the bounds of the rectangle.")
        self.xmin = xmin
        self.ymin = ymin
        self._update_boundaries()

    @property
    def max_coord(self):
        return (self.xmax, self.ymax)

    @max_coord.setter
    def max_coord(self, value):
        xmax, ymax = value
        if xmax <= self.xmin or ymax <= self.ymin:
            raise ValueError("Max coord must be within the bounds of the rectangle.")
        self.xmax = xmax
        self.ymax = ymax
        self._update_boundaries()

    @property
    def center(self):
        return (self._center_x, self._center_y)

    @center.setter
    def center(self, value):
        self._center_x, self._center_y = value
        self._update_boundaries()

    def is_horizontally_intersecting(self, other_rect, gap_tolerance=0):
        return not (self.xmax + gap_tolerance < other_rect.xmin or self.xmin - gap_tolerance > other_rect.xmax)

    def is_vertically_intersecting(self, other_rect, gap_tolerance=0):
        return not (self.ymax + gap_tolerance < other_rect.ymin or self.ymin - gap_tolerance > other_rect.ymax)

    def combine_with(self, other_rect):
        xmin = min(self.xmin, other_rect.xmin)
        xmax = max(self.xmax, other_rect.xmax)
        ymin = min(self.ymin, other_rect.ymin)
        ymax = max(self.ymax, other_rect.ymax)
        center_x = (xmin + xmax) / 2
        center_y = (ymin + ymax) / 2
        width = xmax - xmin
        height = ymax - ymin
        self._center_x = center_x
        self._center_y = center_y
        self._width = width
        self._height = height
        self._update_boundaries()
