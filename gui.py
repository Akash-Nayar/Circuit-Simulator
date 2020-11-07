from tkinter import *


voltage = 15.0
resistance = 10.0
capacitance = 10.0
flip = False


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
    def __init__(self, parent, default, flip_default, x, y):
        self.top = Toplevel(parent)
        self.voltage_label = Label(top, text="Voltage")
        self.voltage_label.pack()

        entry = StringVar()
        entry.set(default)
        self.voltage_box = Entry(top, textvariable=entry)
        self.reg = top.register(validate_voltage)
        self.voltage_box.config(validate="key", validatecommand=(self.reg, "%P"))
        self.voltage_box.pack()
        self.flip = IntVar(value=int(flip_default))
        self.flip_check = Checkbutton(top, text="Flip label", variable=self.flip)
        self.flip_check.pack()

        self.submit_button = Button(top, text="Submit", command=self.send)
        self.submit_button.pack()
        self.top.update()
        w, h = self.top.winfo_width(), self.top.winfo_height()
        self.top.geometry(f"+{x + 20}+{y - int(h / 2)}")

    def send(self):
        global voltage, flip
        voltage = float(self.voltage_box.get())
        flip = bool(self.flip.get())
        self.top.destroy()


class CapacitorDialog:
    def __init__(self, parent, default, flip_default, x, y):
        self.top = Toplevel(parent)
        self.capacitance_label = Label(top, text="Capacitance")
        self.capacitance_label.pack()

        entry = StringVar()
        entry.set(default)
        self.capacitance_box = Entry(top, textvariable=entry)
        self.reg = top.register(validate_resistance)
        self.capacitance_box.config(validate="key", validatecommand=(self.reg, "%P"))
        self.capacitance_box.pack()
        self.flip = IntVar(value=int(flip_default))
        self.flip_check = Checkbutton(top, text="Flip label", variable=self.flip)
        self.flip_check.pack()
        self.submit_button = Button(top, text="Submit", command=self.send)
        self.submit_button.pack()
        self.top.update()
        w, h = self.top.winfo_width(), self.top.winfo_height()
        self.top.geometry(f"+{x + 20}+{y - int(h / 2)}")

    def send(self):
        global capacitance, flip
        capacitance = float(self.capacitance_box.get())
        flip = bool(self.flip.get())
        self.top.destroy()


class ResistorDialog:
    def __init__(self, parent, default, flip_default, x, y):
        self.top = Toplevel(parent)
        self.resistance_label = Label(top, text="Resistance")
        self.resistance_label.pack()
        entry = StringVar()
        entry.set(default)
        self.resistance_box = Entry(top, textvariable=entry)
        self.reg = top.register(validate_resistance)
        self.resistance_box.config(validate="key", validatecommand=(self.reg, "%P"))
        self.resistance_box.pack()
        self.flip = IntVar(value=int(flip_default))
        self.flip_check = Checkbutton(top, text="Flip label", variable=self.flip)
        self.flip_check.pack()

        self.submit_button = Button(top, text="Submit", command=self.send)
        self.submit_button.pack()
        self.top.update()
        w, h = self.top.winfo_width(), self.top.winfo_height()
        self.top.geometry(f"+{x + 20}+{y - int(h / 2)}")

    def send(self):
        global resistance, flip
        resistance = float(self.resistance_box.get())
        flip = bool(self.flip.get())
        self.top.destroy()
