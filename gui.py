from tkinter import *


voltage = 0
resistance = 0


def validate_float(flt, positive=False):

    if not positive:
        try:
            if flt[0] == "-":
                flt = flt[1:]
        except IndexError:
            pass
    if flt == "":
        return True
    try:
        float(flt)
        return True
    except ValueError:
        return False


def validate_voltage(flt):
    return validate_float(flt)


def validate_resistance(flt):
    return validate_float(flt, positive=True)


class BatteryDialog:
    def __init__(self, parent, default):
        top = self.top = Toplevel(parent)
        self.voltage_label = Label(top, text="Voltage")
        self.voltage_label.pack()

        entry = StringVar()
        entry.set(default)
        self.voltage_box = Entry(top, textvariable=entry)
        self.reg = top.register(validate_voltage)
        self.voltage_box.config(validate="key", validatecommand=(self.reg, "%P"))
        self.voltage_box.pack()

        self.submit_button = Button(top, text="Submit", command=self.send)
        self.submit_button.pack()

    def send(self):
        global voltage
        voltage = float(self.voltage_box.get())
        self.top.destroy()


class ResistorDialog:
    def __init__(self, parent, default):
        top = self.top = Toplevel(parent)
        self.resistance_label = Label(top, text="Resistance")
        self.resistance_label.pack()
        entry = StringVar()
        entry.set(default)
        self.resistance_box = Entry(top, textvariable=entry)
        self.reg = top.register(validate_resistance)
        self.resistance_box.config(validate="key", validatecommand=(self.reg, "%P"))
        self.resistance_box.pack()

        self.submit_button = Button(top, text="Submit", command=self.send)
        self.submit_button.pack()

    def send(self):
        global resistance
        resistance = float(self.resistance_box.get())
        self.top.destroy()
