from dataclasses import dataclass


GEAR_SCALE = 7424*50/360

class RESPONSE_ERROR_CODES:
    ERR_CODE_TEMP = 0
    ERR_CODE_ESTOP = 1
    ERR_CODE_MNE = 2
    ERR_CODE_COM = 3
    ERR_CODE_LAG = 4
    ERR_CODE_ENC = 5
    ERR_CODE_DRV = 6
    ERR_CODE_OC = 7

RESPONSE_ERROR_CODES_DICT = {
    RESPONSE_ERROR_CODES.ERR_CODE_TEMP : ("TEMP","Temperatur des Motorcontrollers/ des Motors zu hoch",),
    RESPONSE_ERROR_CODES.ERR_CODE_ESTOP : ("ESTOP", "Keine 24V am Controller anliegend (Notstop)", ),
    RESPONSE_ERROR_CODES.ERR_CODE_MNE : ("MNE","Motor nicht aktiviert",), 
    RESPONSE_ERROR_CODES.ERR_CODE_COM : ("COM", "Kommunikationsausfall",),
    RESPONSE_ERROR_CODES.ERR_CODE_LAG : ("LAG", "Schleppfehler",),
    RESPONSE_ERROR_CODES.ERR_CODE_ENC : ("ENC","Encoder Fehler (Motor oder Abtriebsencoder)", ),
    RESPONSE_ERROR_CODES.ERR_CODE_DRV : ("DRV","Treiberfehler", ),
    RESPONSE_ERROR_CODES.ERR_CODE_OC : ("OC", "Überstrom"),
}



############
# EXCEPTIONS
############

class Exception_PCAN_Connection_Failed(BaseException):
    def __init__(self, error_status):            
        message = f"Connection to PCAN USB Adapter failed. Is the adapter plugged in? Error Code = {error_status}"
        super().__init__(message)

class Exception_Controller_No_CAN_ID(BaseException):
    ...


class Exception_Movement_Command_Reply_Error(BaseException):
    def __init__(self, error_codes):
        message = f"Movement CMD Reply has at least one error code: {error_codes}"
        super().__init__(message)
        self.error_codes = error_codes



#########
# CLASSES
#########

@dataclass
class MessageMovementCommandReply:
    """Reply message from movement commands.
    Params:
    - current (mA) : float
    - position (°): float
    - tics: int
    - millis: float
    """
    current: float
    position: float
    tics: int
    millis: int

    def __lt__(self, other):
        return self.position < other.position

    def __gt__(self, other):
        return self.position > other.position
    def __call__(self):
        """Returns the attributes of the instance: current, position, millis"""
        return self.current, self.position, self.tics, self.millis
    
@dataclass
class MessageEnvironmentStatus:
    """
    Environmental message, sent acyclical 1-2 times per sec.
    Params:
    - voltage (V): float
    - temp_motor (°C): float
    - temp_board (°C): float
    - millis: float
    """

    voltage:float 
    temp_motor:float 
    temp_board:float 
    millis: float

    def __init__(self, _voltage, _temp_motor, _temp_board, _millis) -> None:
        self.voltage = _voltage / 1000
        self.temp_motor = _temp_motor / 100 if _temp_motor != -1 else 0
        self.temp_board = _temp_board / 100
        self.millis = _millis

    def __call__(self):
        """Returns the attributes of the instance: voltage, temp_motor and temp_board."""
        return self.voltage, self.temp_motor, self.temp_board, self.millis

