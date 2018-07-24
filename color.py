class Color:
    def __init__(self, value, alpha=1.0):
        if isinstance(value, Color):
            self._value = value._value
        elif isinstance(value, str):
            self._value = Color.hex_to_rgb(value)
        else:
            self._value = list(value)
        self._value = list(map(int, self._value))
        self._alpha = alpha

        assert len(self._value) == 3
        assert all(map(lambda e: 0 <= e <= 255, self._value))
        assert 0 <= self._alpha <= 1

    def __add__(self, alpha: float):
        assert isinstance(alpha, float)
        assert 0 <= self._alpha <= 1
        return Color(self._value, alpha)

    def __str__(self):
        return str(self.to_json())

    def __repr__(self):
        return str(self.to_json())

    @property
    def hex(self):
        return Color.rgb_to_hex(self._value)

    @property
    def rgb(self):
        return self._value

    @property
    def alpha(self):
        return self._alpha

    @property
    def light(self):
        r, g, b = self._value
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance > 0.5

    @property
    def alternative(self):
        if self.light:
            return Color([0, 0, 0])
        else:
            return Color([255, 255, 255])

    def to_json(self):
        return [*self._value, self._alpha]

    def add_alpha(self, alpha):
        return Color(self._value, alpha)

    def add_light(self, m=1.1, a=20):
        value = list(map(lambda x: min(255, int(x * m + a)), self._value))
        return Color(value, self._alpha)

    @classmethod
    def rgb_to_hex(cls, color: iter):
        return '#' + ''.join(map(lambda c: hex(c)[2:], color))

    @classmethod
    def hex_to_rgb(cls, value: str):
        if value.startswith('#'):
            value = value[1:]
        if len(value) == 6:
            value = [int(value[i:i + 2], 16) for i in range(0, 6, 2)]
        elif len(value) == 3:
            value = [int(value[i:i + 1] * 2, 16) for i in range(0, 3, 1)]
        else:
            raise ValueError
        return value
