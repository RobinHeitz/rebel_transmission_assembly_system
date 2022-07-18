from re import X


class MyClass:

    def __init__(self) -> None:
        self._x = None

    
    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        print("SETTER CALLED")
        self._x = value

    
    