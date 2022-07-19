
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


if __name__ == "__main__":

    print(RESPONSE_ERROR_CODES_DICT.get(RESPONSE_ERROR_CODES.ERR_CODE_COM))