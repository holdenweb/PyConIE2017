"""Simple switch debouncer"""
from machine import Timer, Pin

class Switch:
    "Represents a switch attached to a pin."
    def __init__(self, pin_no, name):
        self._state = 0
        self.value = 0
        self.pin = Pin(pin_no)
        self.name = name

    def output(self):
        "Return name of switch if closed, dot if open."
        return self.name if self.value else "."

class Debouncer:
    """Handles logic for repeated sampling of all switches with debounced transition detection.
    
    A regular tick schedules the examination of all registered switches, recording a value
    if the last twelve samples agree (which the code assumes mean bouncing has stopped)."""
    def __init__(self):
        self.switches = []
        self.timer = Timer(-1)
        self.timer.init(period=6, mode=Timer.PERIODIC, callback=self.tick)

    def register(self, switch):
        "Add a switch to the bank."
        self.switches.append(switch)
        switch.pin.init(mode=Pin.IN, pull=Pin.PULL_UP)
        return switch

    def tick(self, _):
        "Examine input states and note debounced states."
        for switch in self.switches:
            bit = switch.pin.value()
            switch._state = ((switch._state << 1) | bit) & 0xfff
            # Latch state if last 12 samples were equal
            if switch._state == 0x000:   # switch pressed
                switch.value = True
            elif switch._state == 0xfff: # switch released
                switch.value = False

def switches():
    "Report names of pressed switches."
    return "".join(x.output() for x in (R, W, B, Y))

# Create a bank of four debounced switches
d = Debouncer()
Y = d.register(Switch(0, "Y")) # D3
R = d.register(Switch(14, "R")) # D5
W = d.register(Switch(12, "W")) # D6
B = d.register(Switch(13, "B")) # D7

# Background task loops reporting changes in any switches' state
state = switches()

while True:
    new_state = switches()
    if new_state != state:
        state = new_state
        print(state)
