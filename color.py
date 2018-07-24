def get_hex(num):
    h = hex(num)[2:]
    return h if len(h) == 2 else h * 2


def bound_color(num):
    return max(min(int(round(num)), 255), 0)


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

        try:
            assert len(self._value) == 3
            assert all(map(lambda e: 0 <= e <= 255, self._value))
            assert 0 <= self._alpha <= 1
        except AssertionError as e:
            print(self._value, value, alpha)
            raise e

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
    def hsl(self):
        return Color.rgb_to_hsl(self._value)

    @property
    def alpha(self):
        return self._alpha

    @property
    def is_light(self):
        r, g, b = self._value
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance > 0.5

    @property
    def alternative(self):
        if self.is_light:
            return Color([0, 0, 0])
        else:
            return Color([255, 255, 255])

    def to_json(self):
        return [*self._value, self._alpha]

    def add_alpha(self, alpha):
        return Color(self._value, alpha)

    def add_light(self, m=1.1, a=0.1):
        h, s, l = self.hsl
        l = max(min(l * m + a, 1), 0)
        value = Color.hsl_to_rgb((h, s, l))
        return Color(value, self._alpha)

    @classmethod
    def rgb_to_hsl(cls, rgb):
        r, g, b = rgb
        r /= 255
        g /= 255
        b /= 255
        cmax_i, cmax = max(zip(range(3), (r, g, b)), key=lambda x: x[1])
        cmin_i, cmin = min(zip(range(3), (r, g, b)), key=lambda x: x[1])
        delta = cmax - cmin
        # hue
        if delta == 0:
            h = 0
        elif cmax == r:
            h = ((g - b) / delta % 6) * 60
        elif cmax == g:
            h = ((b - r) / delta + 2) * 60
        else:
            h = ((r - g) / delta + 4) * 60
        # luminance
        l = (cmax + cmin) / 2
        # saturation
        if delta == 0:
            s = 0
        else:
            s = delta / (1 - abs(2 * l - 1))
        return h, s, l

    @classmethod
    def hsl_to_rgb(cls, hsl):
        h, s, l = hsl
        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = l - c / 2

        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        r, g, b = bound_color((r + m) * 255), bound_color((g + m) * 255), bound_color((b + m) * 255)
        return r, g, b

    @classmethod
    def rgb_to_hex(cls, color: iter):
        return '#' + ''.join(map(get_hex, color))

    @classmethod
    def hex_to_rgb(cls, value: str):
        if value.startswith('#'):
            value = value[1:]
        if len(value) == 6:
            value = [int(value[i:i + 2], 16) for i in range(0, 6, 2)]
        elif len(value) == 3:
            value = [int(value[i:i + 1] * 2, 16) for i in range(0, 3, 1)]
        elif len(value) == 8:
            return Color.hex_to_rgb(value[:-2])
        else:
            raise ValueError(f"bad hex color {value}")
        return value


def main():
    rgb = (43, 56, 89)
    print(rgb)
    hsl = Color.rgb_to_hsl(rgb)
    print(hsl)
    rgb = Color.hsl_to_rgb(hsl)
    print(rgb)


if __name__ == '__main__':
    main()
