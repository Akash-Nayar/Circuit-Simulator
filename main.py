import gui
import math
from tkinter import *
from tkinter.font import Font
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageTk, ImageOps
from scipy import interpolate
import numpy as np


# Colors
color1 = "#F7F7F8"
color2 = "#E2E2E1"
color1 = "#AAAAAA"
color2 = "#BBBBBB"


root = Tk()
root.title("Circuit Simulator")
root.resizable(False, False)



style = ttk.Style(root)

root.tk.eval("""
    set base_theme_dir awthemes-9.5.0/

    package ifneeded awthemes 9.5.0 \
        [list source [file join $base_theme_dir awthemes.tcl]]
    package ifneeded colorutils 4.8 \
        [list source [file join $base_theme_dir colorutils.tcl]]
    package ifneeded awdark 7.9 \
        [list source [file join $base_theme_dir awdark.tcl]]
    # ... (you can add the other themes from the package if you want
    """)
root.tk.call("package", "require", 'awdark')
root.tk.call("package", "require", 'awdark')
root.tk.call("package", "require", 'awlight')
print(style.theme_names())
style_str = 'awdark'
if style_str == 'awdark':
    dark_mode = True
else:
    dark_mode = False
style.theme_use(style_str)

root.configure(bg=style.lookup('TFrame', 'background'))
style.theme_use('awlight')
display_width = 1280
display_height = 720

circuit_width = 50
circuit_height = 30

cell_size = 20
canvas_width = circuit_width * cell_size
canvas_height = circuit_height * cell_size


bg_color = color2
bg_widget_color = color1

tab_control = ttk.Notebook(root)

creator = ttk.Frame(tab_control)
observer = ttk.Frame(tab_control)
"""
resistor_canvas = Canvas(observer)
resistor_scrollbar = ttk.Scrollbar(observer, orient="horizontal", command=resistor_canvas.xview)
resistor_frame = ttk.Frame(resistor_canvas)
resistor_frame.bind(
    "<Configure>",
    lambda e: resistor_canvas.configure(
        scrollregion=resistor_canvas.bbox("all")
    )
)
resistor_canvas.create_window((0, 0), window=resistor_frame, anchor="nw")
resistor_canvas.configure(yscrollcommand=resistor_scrollbar.set)

for i in range(50):
    ttk.Label(resistor_frame, text="Sample scrolling label").grid(row=0, column=i)
resistor_canvas.grid(row=0, column=0)
resistor_scrollbar.grid(row=1, column=0)
"""
padding = (10, 10)
tab_control.add(creator, text ='Creator')
tab_control.add(observer, text ='Observer')
tab_control.grid(row=0, column=0)
circuit_view_frame = ttk.LabelFrame(creator, text='Circuit Board')
circuit_view_frame.grid(row=0, column=0, sticky="n",
                  padx=padding[0], pady=padding[1])
circuit_view = Canvas(circuit_view_frame, width=canvas_width, height=canvas_height,
                      highlightthickness=1, background='gray10' if dark_mode else None, highlightbackground="black")

options_view = ttk.Frame(creator)
root.option_add("*Font", "Calibri")

# the root window was already created, so we
# have to update it ourselves


circuit_view.grid(row=0, column=0, sticky="n",
                  padx=padding[0], pady=padding[1])
options_view.grid(row=0, column=1, sticky="n",
                  padx=(0, padding[0]))


circuit = [[0] * circuit_width for _ in range(circuit_height)]
circuit_objects = [[0] * circuit_width for _ in range(circuit_height)]
circuit_objects_list = []

capacitors = []

draw_labels = True


def print_path(p):
    text = ""
    for i in range(len(circuit)):
        row = "\n"
        for j in range(len(circuit[0])):
            if (i, j) in p:
                if circuit[i][j] == 6:
                    row += "R"
                else:
                    row += "x"
            else:
                row += " "
        text += row
    print(text)


def print_circuit(arr):
    text = ""
    for i in range(len(arr)):
        row = arr[i]
        row_text = "\n"
        for j in row:
            if j != 0:
                if j == 6:
                    row_text += "R"
                else:
                    row_text += "x"
            else:
                row_text += " "
        text += row_text
    print(text)


# print_circuit(circuit)


def ti(arr, tup):
    if 0 > tup[0] or tup[0] >= len(arr) or 0 > tup[1] or tup[1] >= len(arr[0]):
        return 0
    return arr[tup[0]][tup[1]]


current_path = []


def get_path(position, curr_path, visited, end_point):
    global circuit
    curr_path.append(position)
    visited.append(position)
    if position == end_point:
        return curr_path
    possibilities = get_possibilities(position[0], position[1])
    above, below, right, left = possibilities
    availabilities = []
    for possibility in possibilities:
        try:
            value = ti(circuit, possibility)
            if value != 0 and possibility not in visited:
                availabilities.append(possibility)
        except IndexError:
            continue

    # Check if we are at an input node:
    current_value = ti(circuit, position)
    if current_value == 2:
        new_paths = [
            get_path(availability, [], visited.copy(), end_point)
            for availability in availabilities
        ]
        new_sols = []
        for i in range(len(availabilities)):
            # Check dimentionality
            item = new_paths[i][0]
            counter = 1
            while not isinstance(item, tuple):
                item = item[0]
                counter += 1
            if counter != 1:
                for new_p in new_paths[i]:
                    new_sols.append(curr_path + new_p)
            else:
                new_sols.append(curr_path + new_paths[i])
        return new_sols
    if len(availabilities) == 0:
        return curr_path
    next_pos = availabilities[0]
    if int(current_value) == 3:
        if current_value == 3.0:
            next_pos = above
        elif current_value == 3.25:
            next_pos = below
        elif current_value == 3.5:
            next_pos = right
        else:
            next_pos = left
    return get_path(next_pos, curr_path, visited, end_point)


# images:

def convert_color(im, old_c, new_c):
    im = im.convert('RGBA')

    data = np.array(im)  # "data" is a height x width x 4 numpy array
    red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability

    # Replace white with red... (leaves alpha values alone...)
    white_areas = (red == old_c[0]) & (blue == old_c[1]) & (green == old_c[2])
    data[..., :-1][white_areas.T] = new_c  # Transpose back needed

    im2 = Image.fromarray(data)
    return im2

new_color = (255, 255, 255)
old_color = (0, 0, 0)

# images:
cursor_img = ImageTk.PhotoImage(Image.open(
    "images/cursor.png").resize((cell_size, cell_size), Image.ANTIALIAS))

delete_img = Image.open("images/x.png").resize((cell_size, cell_size), Image.ANTIALIAS)
delete_img = delete_img if not dark_mode else convert_color(delete_img, old_color, new_color)
delete_img = ImageTk.PhotoImage(delete_img)



wire_straight_img = Image.open(f"images/wire_straight.png")
wire_straight_img = wire_straight_img if not dark_mode else convert_color(wire_straight_img, old_color, new_color)
wire_straight_imgs = {
    "horizontal": ImageTk.PhotoImage(wire_straight_img),
    "vertical": ImageTk.PhotoImage(wire_straight_img.rotate(90)),
}

wire_corner_img = Image.open(f"images/wire_corner.png")
wire_corner_img = wire_corner_img if not dark_mode else convert_color(wire_corner_img, old_color, new_color)
wire_corner_imgs = {
    "right_down": ImageTk.PhotoImage(wire_corner_img),
    "down_left": ImageTk.PhotoImage(wire_corner_img.rotate(90)),
    "left_up": ImageTk.PhotoImage(wire_corner_img.rotate(180)),
    "up_right": ImageTk.PhotoImage(wire_corner_img.rotate(270)),
}
wire_junction_img = Image.open(f"images/wire_junction.png")
wire_junction_img = wire_junction_img if not dark_mode else convert_color(wire_junction_img, old_color, new_color)
wire_junction_imgs = {
    "up": ImageTk.PhotoImage(wire_junction_img),
    "left": ImageTk.PhotoImage(wire_junction_img.rotate(90)),
    "down": ImageTk.PhotoImage(wire_junction_img.rotate(180)),
    "right": ImageTk.PhotoImage(wire_junction_img.rotate(270)),
}
wire_cross_img = Image.open(f"images/wire_cross.png")
wire_cross_img = wire_cross_img if not dark_mode else convert_color(wire_cross_img, old_color, new_color)
wire_cross_imgs = {"any": ImageTk.PhotoImage(wire_cross_img)}

input_node_junction_img = Image.open(f"images/input_node_junction.png")
input_node_junction_img = input_node_junction_img if not dark_mode else convert_color(input_node_junction_img, old_color, new_color)
input_node_junction_imgs = {
    "up": ImageTk.PhotoImage(input_node_junction_img),
    "left": ImageTk.PhotoImage(input_node_junction_img.rotate(90)),
    "down": ImageTk.PhotoImage(input_node_junction_img.rotate(180)),
    "right": ImageTk.PhotoImage(input_node_junction_img.rotate(270)),
}
input_node_cross_img = Image.open(f"images/input_node_cross.png")
input_node_cross_img = input_node_cross_img if not dark_mode else convert_color(input_node_cross_img, old_color, new_color)
input_node_cross_imgs = {"any": ImageTk.PhotoImage(input_node_cross_img)}

output_node_corner_left_img = Image.open(f"images/output_node_corner.png")
output_node_corner_left_img = output_node_corner_left_img if not dark_mode else convert_color(output_node_corner_left_img, old_color, new_color)
output_node_corner_left_imgs = {
    "down": ImageTk.PhotoImage(output_node_corner_left_img),
    "right": ImageTk.PhotoImage(output_node_corner_left_img.rotate(90)),
    "up": ImageTk.PhotoImage(output_node_corner_left_img.rotate(180)),
    "left": ImageTk.PhotoImage(output_node_corner_left_img.rotate(270)),
}

output_node_corner_right_img = ImageOps.mirror(output_node_corner_left_img)
output_node_corner_right_img = output_node_corner_right_img if not dark_mode else convert_color(output_node_corner_right_img, old_color, new_color)
output_node_corner_right_imgs = {
    "down": ImageTk.PhotoImage(output_node_corner_right_img),
    "right": ImageTk.PhotoImage(output_node_corner_right_img.rotate(90)),
    "up": ImageTk.PhotoImage(output_node_corner_right_img.rotate(180)),
    "left": ImageTk.PhotoImage(output_node_corner_right_img.rotate(270)),
}


output_node_junction_img = Image.open(f"images/output_node_junction.png")
output_node_junction_img = output_node_junction_img if not dark_mode else convert_color(output_node_junction_img, old_color, new_color)
output_node_junction_imgs = {
    "down": ImageTk.PhotoImage(output_node_junction_img),
    "right": ImageTk.PhotoImage(output_node_junction_img.rotate(90)),
    "up": ImageTk.PhotoImage(output_node_junction_img.rotate(180)),
    "left": ImageTk.PhotoImage(output_node_junction_img.rotate(270)),
}
output_node_cross_img = Image.open(f"images/output_node_cross.png")
output_node_cross_img = output_node_cross_img if not dark_mode else convert_color(output_node_cross_img, old_color, new_color)
output_node_cross_imgs = {
    "down": ImageTk.PhotoImage(output_node_cross_img),
    "right": ImageTk.PhotoImage(output_node_cross_img.rotate(90)),
    "up": ImageTk.PhotoImage(output_node_cross_img.rotate(180)),
    "left": ImageTk.PhotoImage(output_node_cross_img.rotate(270)),
}


resistor_img = Image.open(f"images/resistor.png")
resistor_img = resistor_img if not dark_mode else convert_color(resistor_img, old_color, new_color)
resistor_imgs = {
    "horizontal": ImageTk.PhotoImage(resistor_img),
    "vertical": ImageTk.PhotoImage(resistor_img.rotate(90)),
}

battery_img = Image.open(f"images/battery.png")
battery_img = battery_img if not dark_mode else convert_color(battery_img, old_color, new_color)
battery_imgs = {
    "right": ImageTk.PhotoImage(battery_img),
    "down": ImageTk.PhotoImage(battery_img.rotate(90)),
    "left": ImageTk.PhotoImage(battery_img.rotate(180)),
    "up": ImageTk.PhotoImage(battery_img.rotate(270)),
}

capacitor_img = Image.open(f"images/capacitor.png")
capacitor_img = capacitor_img if not dark_mode else convert_color(capacitor_img, old_color, new_color)
capacitor_imgs = {
    "horizontal": ImageTk.PhotoImage(capacitor_img),
    "vertical": ImageTk.PhotoImage(capacitor_img.rotate(90)),
}


class CircuitItem:
    imgs = {}
    default_state = None
    default_direction = None
    uid = 1

    def __init__(self, voltage=0, resistance=0, current=0, capacitance=0, charge=0):
        self._voltage = voltage
        self._resistance = resistance
        self._current = current
        self._capacitance = capacitance
        self._charge = charge
        self.flipped = False
        self.uid = CircuitItem.uid
        CircuitItem.uid += 1

    @property
    def voltage(self):
        return self._voltage

    @voltage.setter
    def voltage(self, v):
        self._voltage = round(v, 3)
        if self.resistance != 0:
            self.current = round(v / self.resistance, 3)

    @property
    def resistance(self):
        return self._resistance

    @resistance.setter
    def resistance(self, r):
        if r < 0:
            raise ValueError("Invalid resistance: r < 0")
        self._resistance = r

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, c):
        self._current = c

    @property
    def capacitance(self):
        return self._capacitance

    @capacitance.setter
    def capacitance(self, c):
        if c < 0:
            raise ValueError("Invalid capacitance: c < 0")
        self._capacitance = c

    @property
    def charge(self):
        return self._charge

    @charge.setter
    def charge(self, q):
        self._charge = q
        if self.capacitance != 0:
            self.voltage = q / self.capacitance

    def draw(self, i, j, direction=None, state=None):
        try:
            circuit_view.create_image(
                j * 20,
                i * 20,
                anchor=NW,
                image=self.imgs[state if state is not None else self.default_state][
                    direction if direction is not None else self.default_direction
                ],
            )
        except IndexError:
            pass


class CircuitSegment(CircuitItem):
    def __init__(self, contents):
        super().__init__()
        self.contents = contents

    @property
    def resistance(self):
        return round(sum([item.resistance for item in self.contents]), 3)

    @property
    def voltage(self):
        return self._voltage

    @voltage.setter
    def voltage(self, v):
        self._voltage = round(v, 3)
        if self.resistance != 0:
            self.current = round(v / self.resistance, 3)
        print(self.contents)
        for item in self.contents:
            item.voltage = self.current * item.resistance

    def __repr__(self):
        return f"{[item for item in self.contents]}"

    @property
    def capacitance(self):
        c_sum = 0
        for item in self.contents:
            if item.capacitance != 0:
                c_sum += 1 / item.capacitance
        return 0 if c_sum == 0 else 1 / c_sum

    @property
    def charge(self):
        return self._charge

    @charge.setter
    def charge(self, q):
        for item in self.contents:
            if item.capacitance != 0:
                item.charge = q


class Wire(CircuitItem):
    imgs = {
        "straight": wire_straight_imgs,
        "corner": wire_corner_imgs,
        "junction": wire_junction_imgs,
        "cross": wire_cross_imgs,
    }
    default_state = "straight"
    default_direction = "horizontal"

    def __init__(self, resistance=0):
        super().__init__(resistance=resistance)


def get_direction(dir):
    if dir == 0:
        return "up"
    elif dir == 0.25:
        return "down"
    elif dir == 0.5:
        return "right"
    else:
        return "left"


class InputNode(Wire):

    imgs = {"junction": input_node_junction_imgs,
            "cross": input_node_cross_imgs}

    default_state = "junction"
    default_direction = "right"

    def __init__(self):
        super().__init__(self)


class OutputNode(Wire):
    imgs = {
        "corner_left": output_node_corner_left_imgs,
        "corner_right": output_node_corner_right_imgs,
        "junction": output_node_junction_imgs,
        "cross": output_node_cross_imgs,
    }

    default_state = "junction"

    def __init__(self, direction):
        super().__init__()
        self.default_direction = get_direction(direction)

    def draw(self, i, j, direction=None, state=None):
        print(state)
        try:
            circuit_view.create_image(
                j * 20,
                i * 20,
                anchor=NW,
                image=self.imgs[state if state is not None else self.default_state][
                    direction
                    if direction is not None and direction != "any"
                    else self.default_direction
                ],
            )
        except IndexError:
            pass


class Resistor(CircuitItem):
    imgs = resistor_imgs
    default_direction = "horizontal"

    id = 1

    def __init__(self, resistance):
        super().__init__(resistance=resistance)
        self.id = Resistor.id
        Resistor.id += 1

    def __repr__(self):
        return f"Resistor({self.resistance})"

    def draw(self, i, j, direction=None):
        global draw_labels

        direction = self.default_direction if direction is None else direction
        if draw_labels:
            if self.flipped:
                multiplier = -3
                angle_offset = 180
            else:
                multiplier = 1
                angle_offset = 0
            if direction == "horizontal":
                # Draw labels above
                circuit_view.create_text(
                    j * 20 + 10,
                    i * 20 - multiplier*10,
                    text=f"{int(self.resistance) if self.resistance.is_integer() else self.resistance} Ω",
                    angle=angle_offset,
                    fill='white'
                )
            else:
                circuit_view.create_text(
                    j * 20 - multiplier*10,
                    i * 20 + 10,
                    text=f"{int(self.resistance) if self.resistance.is_integer() else self.resistance} Ω",
                    angle=angle_offset+90,
                    fill='white'
                )

        try:
            circuit_view.create_image(
                j * 20, i * 20, anchor=NW, image=self.imgs[direction]
            )
        except IndexError:
            pass


class Battery(CircuitItem):

    default_direction = "left"
    imgs = battery_imgs

    def __init__(self, voltage):
        super().__init__(voltage=voltage)

    def draw(self, i, j, direction=None):

        direction = self.default_direction if direction is None else direction
        if draw_labels:
            if self.flipped:
                multiplier = -3
                angle_offset = 180
            else:
                multiplier = 1
                angle_offset = 0
            if direction in ['left', 'right']:
                # Draw labels above
                circuit_view.create_text(
                    j * 20 + 10,
                    i * 20 - multiplier * 10,
                    text=f"{int(self.voltage) if self.voltage.is_integer() else self.voltage} V",
                    angle=angle_offset,
                    fill='white'
                )
            else:
                circuit_view.create_text(
                    j * 20 - multiplier * 10,
                    i * 20 + 10,
                    text=f"{int(self.voltage) if self.voltage.is_integer() else self.voltage} V",
                    angle=angle_offset+90,
                    fill='white'
                )

        try:
            circuit_view.create_image(
                j * 20,
                i * 20,
                anchor=NW,
                image=self.imgs[
                    self.default_direction if direction is None else direction
                ],
            )
        except IndexError:
            pass

    def __repr__(self):
        return f"Battery({self.voltage})"


class Capacitor(CircuitItem):

    id = 1

    imgs = capacitor_imgs
    default_direction = "horizontal"

    def __init__(self, capacitance):
        super().__init__(capacitance=capacitance)
        self.times = []
        self.charges = []
        self._tau = 0.0
        self.id = Capacitor.id
        Capacitor.id += 1

    @property
    def tau(self):
        return self.capacitance * R_eq

    def draw(self, i, j, direction=None):
        global draw_labels

        direction = self.default_direction if direction is None else direction
        if draw_labels:
            if self.flipped:
                multiplier = -3
                angle_offset = 180
            else:
                multiplier = 1
                angle_offset = 0
            if direction == "horizontal":
                # Draw labels above
                circuit_view.create_text(
                    j * 20 + 10,
                    i * 20 - multiplier * 10,
                    text=f"{int(self.capacitance) if self.capacitance.is_integer() else self.capacitance} F",
                    angle=angle_offset,
                    fill='white'
                )
            else:
                circuit_view.create_text(
                    j * 20 - multiplier * 10,
                    i * 20 + 10,
                    text=f"{int(self.capacitance) if self.capacitance.is_integer() else self.capacitance} F",
                    angle=angle_offset+90,
                    fill='white'
                )

        try:
            circuit_view.create_image(
                j * 20, i * 20, anchor=NW, image=self.imgs[direction]
            )
        except IndexError:
            pass


class ParallelCell(CircuitItem):
    def __init__(self, paths):
        super().__init__()
        self.paths = paths
        self.origin = paths[0][0]
        self.end = paths[0][-1]
        self._voltage = 0
        # Check paths for parallels within

        # 2D, each row is a path, each column represent object
        self.paths_items = []

        new_nodes = []
        for path in self.paths:

            # Check to see if current path contains one of the new nodes, disregard if so
            if any(node in new_nodes for node in path):
                continue

            path_items = []

            skip_until = False
            target = (0, 0)
            for i, step in enumerate(path[1:]):
                if skip_until and step != target:
                    continue

                skip_until = False
                item = ti(circuit, step)

                """# If it is a wire:
                if item == 1:
                    path_items.append(Wire())
                    # Check neighbors:
                    above = (step[0] - 1, step[1])
                    below = (step[0] + 1, step[1])
                    right = (step[0], step[1] + 1)
                    left = (step[0], step[1] - 1)
                    possibilities = [above, below, right, left]
                    availabilities = []
                    for possibility in possibilities:
                        try:
                            value = ti(circuit, possibility)
                            if value != 0:
                                availabilities.append(possibility)
                        except IndexError:
                            continue
                    # Do some other stuff that im too lazy to do rn
"""
                # If it is a resistor:
                if item == 6:
                    path_items.append(ti(circuit_objects, step))

                elif item == 7:
                    path_items.append(ti(circuit_objects, step))
                # If it is an input node
                elif item == 2:
                    new_nodes.append(step)
                    previous_item = ti(circuit, paths[0][i])
                    # Generate new paths starting at this node:

                    new_paths = get_path(step, [], [path[i]], self.end)

                    # print_path(new_path)
                    # Find the end, when num of input and output nodes are equal
                    print("new")
                    num_input = 0
                    num_output = 0
                    for new_step in new_paths[0]:
                        new_item = ti(circuit, new_step)
                        if new_item == 2:
                            num_input += 1
                        elif int(new_item) == 3:
                            num_output += 1
                        if num_input == num_output:
                            ending = new_step
                            break
                    # Shorten the paths
                    shortened_paths = []
                    for new_path in new_paths:
                        shortened_path = new_path[: new_path.index(ending) + 1]
                        if shortened_path not in shortened_paths:
                            shortened_paths.append(
                                new_path[: new_path.index(ending) + 1]
                            )
                    path_items.append(ParallelCell(shortened_paths))
                    skip_until = True
                    target = ending
            self.paths_items.append(CircuitSegment(path_items))

            # print(self.paths_items)

    def __repr__(self):
        return f"ParallelCell(paths_items={self.paths_items})"

    @property
    def voltage(self):
        return self._voltage

    @voltage.setter
    def voltage(self, v):
        self._voltage = v
        for path in self.paths_items:
            path.voltage = v
            if path.resistance != 0:
                path.current = round(v / path.resistance, 3)

    @property
    def resistance(self):
        sum = 0
        for segment in self.paths_items:
            if segment.resistance > 0:
                sum += 1 / segment.resistance

            # if even just 1 path has 0 resistance, whole cell has 0
            else:
                return 0
        return 0 if sum == 0 else round(1 / sum, 3)

    @property
    def charge(self):
        return self._charge

    @charge.setter
    def charge(self, q):
        self._charge = q
        for path in self.paths_items:
            path.charge = q * (path.capacitance / self.capacitance)

    @property
    def capacitance(self):
        return sum([segment.capacitance for segment in self.paths_items])


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
        self.voltage_label = Label(self.top, text="Voltage")
        self.voltage_label.pack()

        entry = StringVar()
        entry.set(default)
        self.voltage_box = Entry(self.top, textvariable=entry)
        self.reg = self.top.register(validate_voltage)
        self.voltage_box.config(
            validate="key", validatecommand=(self.reg, "%P"))
        self.voltage_box.pack()
        self.flip = IntVar(value=int(flip_default))
        self.flip_check = Checkbutton(
            self.top, text="Flip label", variable=self.flip)
        self.flip_check.pack()

        self.submit_button = Button(self.top, text="Submit", command=self.send)
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
        self.capacitance_label = Label(self.top, text="Capacitance")
        self.capacitance_label.pack()

        entry = StringVar()
        entry.set(default)
        self.capacitance_box = Entry(self.top, textvariable=entry)
        self.reg = self.top.register(validate_resistance)
        self.capacitance_box.config(
            validate="key", validatecommand=(self.reg, "%P"))
        self.capacitance_box.pack()
        self.flip = IntVar(value=int(flip_default))
        self.flip_check = Checkbutton(
            self.top, text="Flip label", variable=self.flip)
        self.flip_check.pack()
        self.submit_button = Button(self.top, text="Submit", command=self.send)
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
        self.resistance_label = Label(self.top, text="Resistance")
        self.resistance_label.pack()
        entry = StringVar()
        entry.set(default)
        self.resistance_box = Entry(self.top, textvariable=entry)
        self.reg = self.top.register(validate_resistance)
        self.resistance_box.config(
            validate="key", validatecommand=(self.reg, "%P"))
        self.resistance_box.pack()
        self.flip = IntVar(value=int(flip_default))
        self.flip_check = Checkbutton(
            self.top, text="Flip label", variable=self.flip)
        self.flip_check.pack()

        self.submit_button = Button(self.top, text="Submit", command=self.send)
        self.submit_button.pack()
        self.top.update()
        w, h = self.top.winfo_width(), self.top.winfo_height()
        self.top.geometry(f"+{x + 20}+{y - int(h / 2)}")

    def send(self):
        global resistance, flip
        resistance = float(self.resistance_box.get())
        flip = bool(self.flip.get())
        self.top.destroy()


draw_lines = True
blockSize = 20  # Set the size of the grid block
lines_original = Image.open("images/lines.png")
if dark_mode:
    lines = convert_color(lines_original, (128, 128, 128), (64, 64, 64))
else:
    lines = lines_original
print(lines.mode)
print(lines.size)
#lines.thumbnail((blockSize*circuit_width+6, blockSize*circuit_height+6), Image.ANTIALIAS)
lines_img = ImageTk.PhotoImage(lines)


def draw_grid():

    global draw_lines

    if draw_lines:
        im = circuit_view.create_image(
            0, 0,
            anchor=NW,
            image=lines_img,
        )
        circuit_view.tag_lower(im)
    else:
        for i in range(circuit_width + 1):

            for j in range(circuit_height + 1):
                x = i * blockSize
                y = j * blockSize
                circuit_view.create_oval(x-1, y-1, x+1, y+1, fill="#B3B3B3")
    circuit_view.update()
    #circuit_view.postscript(file="lines.ps", colormode='color')


# GUI


def get_possibilities(i, j):
    up = (i - 1, j)
    down = (i + 1, j)
    right = (i, j + 1)
    left = (i, j - 1)
    return [up, down, right, left]


def get_neighbors(arr, possibilities):
    neighbors = []
    for possibility in possibilities:
        try:
            value = ti(arr, possibility)
            if value != 0:
                neighbors.append(possibility)
        except IndexError:
            continue
    return neighbors


def draw_circuit():
    global circuit, circuit_objects
    circuit_view.delete(ALL)

    print("num elements: ",len(circuit_objects_list))
    #draw_grid()

    for i, row in enumerate(circuit):
        for j, item in enumerate([int(x) for x in row]):
            if item == 0:
                continue

            elif item in [1, 2, 3, 4, 5, 6, 7]:
                obj = circuit_objects[i][j]
                # Check for neighbors
                possibilities = get_possibilities(i, j)
                up, down, right, left = possibilities
                neighbors = get_neighbors(circuit, possibilities)

                # if it's output node
                if item == 3:
                    direction = obj.default_direction
                    print(direction)
                    if direction == "up":
                        direction_neighbor = up
                    elif direction == "down":
                        direction_neighbor = down
                    elif direction == "left":
                        direction_neighbor = left
                    else:
                        direction_neighbor = right
                    print(direction_neighbor, neighbors)
                    if direction_neighbor not in neighbors:
                        print("added")
                        neighbors.append(direction_neighbor)
                    for neighbor in neighbors:
                        if neighbor == up:
                            print("up")
                        elif neighbor == down:
                            print("down")
                        elif neighbors == right:
                            print("right")
                        elif neighbor == left:
                            print("left")
                    print(len(neighbors))
                if len(neighbors) == 0:
                    obj.draw(i, j)
                elif len(neighbors) == 1:
                    # if on same row, horizontal
                    if item == 3:
                        obj.draw(i, j)
                        continue
                    if neighbors[0][0] == i:
                        if item not in [2, 5]:
                            obj.draw(i, j, direction="horizontal")

                        # input node - point in direction of neighbor
                        elif item == 2:
                            if right in neighbors:
                                obj.draw(i, j, state="junction",
                                         direction="left")
                            else:
                                obj.draw(i, j, state="junction",
                                         direction="right")
                        elif item == 5:
                            if dir == 1:
                                obj.draw(i, j, direction="right")
                            else:
                                obj.draw(i, j, direction="left")
                        # print(type(obj), "horizontal")
                    else:
                        if item not in [2, 3, 5]:
                            obj.draw(i, j, direction="vertical")

                        # input node - point in direction of neigbor
                        elif item == 2:
                            if up in neighbors:
                                obj.draw(i, j, state="junction",
                                         direction="down")
                            else:
                                obj.draw(i, j, state="junction",
                                         direction="up")
                        elif item == 5:
                            if dir == 1:
                                obj.draw(i, j, direction="down")
                            else:
                                obj.draw(i, j, direction="up")
                elif len(neighbors) == 2:
                    # Either straight or corner piece

                    # If straight, check to see if either x or y of both are equal:
                    # for output node, unless neightbor[0] is not opposite direction, just draw, else cross
                    if neighbors[0][0] == neighbors[1][0]:
                        # same row - horizontal
                        if item not in [2, 3, 5]:
                            obj.draw(i, j, direction="horizontal")
                        # input node - point up
                        elif item == 2:
                            obj.draw(i, j, state="junction", direction="up")

                        elif item == 3:
                            obj.draw(i, j, state="cross")
                        elif item == 5:
                            if dir == 1:
                                obj.draw(i, j, direction="right")
                            else:
                                obj.draw(i, j, direction="left")

                    elif neighbors[0][1] == neighbors[1][1]:
                        # same column - vertical
                        if item not in [2, 3, 5]:
                            obj.draw(i, j, direction="vertical")
                        # input node - point right
                        elif item == 2:
                            obj.draw(i, j, state="junction", direction="right")
                        elif item == 3:
                            obj.draw(i, j, state="cross")
                        elif item == 5:
                            if dir == 1:
                                obj.draw(i, j, direction="down")
                            else:
                                obj.draw(i, j, direction="up")

                    else:
                        # corner
                        if item == 1:
                            if down in neighbors:
                                # down and right - default
                                if right in neighbors:
                                    # right down
                                    obj.draw(
                                        i, j, state="corner", direction="right_down"
                                    )
                                else:
                                    # down left
                                    obj.draw(i, j, state="corner",
                                             direction="up_right")
                            else:
                                # down and right - default
                                if right in neighbors:
                                    # upright
                                    obj.draw(
                                        i, j, state="corner", direction="down_left"
                                    )
                                else:
                                    # left-up left
                                    obj.draw(i, j, state="corner",
                                             direction="left_up")
                        elif item == 2:
                            if up == neighbors[0]:
                                obj.draw(i, j, state="junction",
                                         direction="down")
                            elif down == neighbors[0]:
                                obj.draw(i, j, state="junction",
                                         direction="up")
                            elif right == neighbors[0]:
                                obj.draw(i, j, state="junction",
                                         direction="left")
                            else:
                                obj.draw(i, j, state="junction",
                                         direction="right")

                        elif item == 3:
                            obj.draw(i, j)

                elif len(neighbors) == 3:
                    if item in [1, 2]:
                        for possibility in possibilities:
                            if possibility not in neighbors:
                                if possibility == down:
                                    obj.draw(i, j, state="junction",
                                             direction="down")
                                elif possibility == left:
                                    obj.draw(i, j, state="junction",
                                             direction="left")
                                elif possibility == up:
                                    obj.draw(i, j, state="junction",
                                             direction="up")
                                else:
                                    obj.draw(i, j, state="junction",
                                             direction="right")
                                break
                    if item == 3:

                        # first check if we should do junciton or corner - if there is a neighbor opposite to direction, do corner
                        found = False
                        for neighbor in neighbors:
                            if neighbor != direction_neighbor and (
                                neighbor[0] == direction_neighbor[0]
                                or neighbor[1] == direction_neighbor[1]
                            ):
                                found = True
                                break
                        if found:
                            # if the neighbor that is not parallel to direction is to the left of direction, do left
                            found = False
                            for neighbor in neighbors:
                                if (
                                    neighbor != direction_neighbor
                                    and neighbor[0] != direction_neighbor[0]
                                    and neighbor[1] != direction_neighbor[1]
                                ):
                                    found = True
                                    if direction_neighbor == up:
                                        # print(neighbor, left)
                                        if neighbor == left:
                                            state = "corner_left"
                                        else:
                                            state = "corner_right"

                                    elif direction_neighbor == left:
                                        if neighbor == down:
                                            state = "corner_left"
                                        else:
                                            state = "corner_right"
                                    elif direction_neighbor == down:
                                        if neighbor == right:
                                            state = "corner_left"
                                        else:
                                            state = "corner_right"
                                    else:
                                        if neighbor == up:
                                            state = "corner_left"
                                        else:
                                            state = "corner_right"
                                    print("state: ", state)
                                    obj.draw(i, j, state=state)
                                    break

                        else:
                            obj.draw(i, j, state="junction")

                else:
                    obj.draw(i, j, state="cross", direction="any")

    draw_grid()


def clear_circuit():
    global circuit, circuit_objects, circuit_objects_list, capacitors
    circuit = [[0] * circuit_width for _ in range(circuit_height)]
    circuit_objects = [[0] * circuit_width for _ in range(circuit_height)]
    circuit_objects_list = []
    capacitors = []

    draw_circuit()


def key(event):
    print("pressed", repr(event.char))


x, y = (0, 0)


def add_wire():
    add_item(1)


def add_resistor():
    add_item(6)


def add_battery(*args):
    add_item(5)


def add_capacitor():
    add_item(7)


def add_input_node():
    add_item(2)


def add_output_node():
    add_item(3)


def delete_item():
    add_item(0)


def add_item(code):
    global x, y, circuit, circuit_objects, circuit_objects_list
    print(x, y)
    if code == 0:
        item = ti(circuit, (y, x))
        if item == 0:
            return
        if item == 7:
            print(len(capacitors))
            id = ti(circuit_objects, (y, x)).id
            for i, capacitor in enumerate(capacitors):
                if capacitor.id == id:
                    capacitors.pop(i)
                    break
            print(len(capacitors))
        # remove from circuit obejects list
        obj = ti(circuit_objects, (y, x))
        for i, item in enumerate(circuit_objects_list):
            if item.uid == obj.uid:
                circuit_objects_list.pop(i)
                break

        new_obj = 0
    elif code == 1:
        new_obj = Wire()
    elif code == 2:
        new_obj = InputNode()
    elif int(code) == 3:
        new_obj = OutputNode(direction=round(code % 1, 2))
    elif code == 5:
        new_obj = Battery(voltage=15.0)
    elif code == 6:
        new_obj = Resistor(10.0)
    elif code == 7:
        new_obj = Capacitor(10.0)
        capacitors.append(new_obj)

    circuit[y][x] = code
    circuit_objects[y][x] = new_obj
    if new_obj != 0:
        circuit_objects_list.append(new_obj)
    draw_circuit()


m = Menu(root, tearoff=0)
m.add_command(label="Input Node", underline=1, command=add_input_node)
m.add_command(label="Output Node", underline=1, command=add_output_node)
m.add_command(label="Resistor", underline=1, command=add_resistor)
m.add_command(label="Battery", underline=1, command=add_battery)
m.add_command(label="Capacitor", underline=1, command=add_capacitor)
m.add_separator()
m.add_command(label="Delete", underline=0, command=delete_item)


def right_click(event):
    global x, y
    try:
        m.post(event.x_root, event.y_root)
    finally:
        m.grab_release()


old_x, old_y = None, None

username = ""

mode = 0


def left_click(event):
    global circuit, circuit_objects, old_x, old_y, capacitance, resistance, voltage, x, y, mode
    x, y = (event.x // 20, event.y // 20)

    if old_x == x and old_y == y:
        return
    old_x, old_y = x, y
    item = int(circuit[y][x])
    #print(item, ti(circuit_objects, (x, y)))

    # If mode is 0, select tool
    if mode == 0:
        if item == 3:
            real_item = circuit[y][x]
            if real_item == 3.0:
                circuit_objects[y][x] = OutputNode(0.5)
                circuit[y][x] = 3.5
            elif real_item == 3.5:
                circuit_objects[y][x] = OutputNode(0.25)
                circuit[y][x] = 3.25
            elif real_item == 3.25:
                circuit_objects[y][x] = OutputNode(0.75)
                circuit[y][x] = 3.75
            else:
                circuit_objects[y][x] = OutputNode(0.0)
                circuit[y][x] = 3.0

        # Allow to change battery voltage:
        elif item == 5:
            obj = circuit_objects[y][x]
            battery_dialog = BatteryDialog(
                root, obj.voltage, obj.flipped, event.x_root, event.y_root)
            root.wait_window(battery_dialog.top)
            #print("voltage: ", gui.voltage)
            obj.flipped = flip
            obj.voltage = voltage
        # Allow to change resistor
        elif item == 6:
            obj = circuit_objects[y][x]
            resistance_dialog = ResistorDialog(
                root, obj.resistance, obj.flipped, event.x_root, event.y_root)
            root.wait_window(resistance_dialog.top)
            #print("voltage: ", gui.resistance)
            obj.flipped = flip
            obj.resistance = resistance
            print(obj)

        elif item == 7:
            print(ti(circuit_objects, (y, x)).charge)
            obj = circuit_objects[y][x]
            capacitance_dialog = CapacitorDialog(
                root, obj.capacitance, obj.flipped, event.x_root, event.y_root)
            root.wait_window(capacitance_dialog.top)
            #print("capacitance: ", gui.capacitance)
            #print("charge:", obj.charge)
            obj.flipped = flip
            obj.capacitance = capacitance
        # print("clicked at", x, y)
    else:
        add_item(mode if mode != 4 else 0)

    draw_circuit()


# draw the grid
def handle_key(event):
    global circuit_objects, x, y
    print(event.x, event.y)
    print(event.x_root, event.y_root)
    #x, y = (event.x // 20, event.y // 20)

    # take care of inconsitencies with mouse position
    #x, y = (circuit_view.winfo_pointerx() // 20, circuit_view.winfo_pointery() // 20)
    print(x, y)
    if event.char == "r":
        add_resistor()
    elif event.char == "b":
        add_battery()
    elif event.char == "i":
        add_input_node()
    elif event.char == "o":
        add_output_node()
    elif event.char == "c":
        add_capacitor()
    elif event.char == "t":
        item = ti(circuit_objects, (y, x))
        print(item)
        print("voltage: ", item.voltage)
        print("resistance: ", item.resistance)
        print("current: ", item.current)


def reset(event):
    global old_x, old_y
    old_x, old_y = None, None


def select_wire():
    global mode
    mode = 1


def select_input_node():
    global mode
    mode = 2


def select_output_node():
    global mode
    mode = 3


def select_resistor():
    global mode
    mode = 6


def select_battery():
    global mode
    mode = 5


def select_capacitor():
    global mode
    mode = 7


def select_none():
    global mode
    mode = 0


def select_delete():
    global mode
    mode = 4


def update_pos(event):
    global label2, x, y
    x = event.x // 20
    y = event.y // 20


circuit_view.bind("<Motion>", update_pos)
circuit_view.bind("<Key>", key)
circuit_view.bind("<B1-Motion>", left_click)
circuit_view.bind("<Button-1>", left_click)
circuit_view.bind("<ButtonRelease-1>", reset)
circuit_view.bind("<Button-3>", right_click)

circuit_view.bind_all("<KeyRelease>", handle_key)


R_eq = 0
I_tot = 0
overview = ttk.LabelFrame(options_view, text="Overview")
overview.grid(row=0, column=0, pady=padding[1])
label1 = ttk.Label(overview, text=f"Total Resistance: {R_eq}").grid(
    row=0, column=0)
label2 = ttk.Label(overview, text=f"Total Current: {I_tot}")
label2.grid(
    row=1, column=0, sticky="w"
)


builder_button_padding = (5, 5)
builder = ttk.LabelFrame(options_view, text="Builder")
builder.grid(row=1, column=0, pady=(0, padding[1]))

# row 1
pointer_button = ttk.Button(builder, image=cursor_img, command=select_none).grid(
    row=0, column=0, padx=builder_button_padding[0], pady=builder_button_padding[1])
pointer_button = ttk.Button(builder, image=delete_img, command=select_delete).grid(
    row=0, column=1, padx=(0, builder_button_padding[0]), pady=builder_button_padding[1])

# row 2
wire_button = ttk.Button(builder, image=wire_straight_imgs['horizontal'], command=select_wire).grid(
    row=1, column=0, padx=builder_button_padding[0], pady=(0, builder_button_padding[1]))
input_node_button = ttk.Button(builder, image=input_node_junction_imgs['right'], command=select_input_node).grid(
    row=1, column=1, padx=(0, builder_button_padding[0]), pady=(0, builder_button_padding[1]))
output_node_button = ttk.Button(builder, image=output_node_cross_imgs['right'], command=select_output_node).grid(
    row=1, column=2, padx=(0, builder_button_padding[0]), pady=(0, builder_button_padding[1]))

# row 3
battery_button = wire_button = ttk.Button(builder, image=battery_imgs['left'], command=select_battery).grid(
    row=2, column=0, padx=builder_button_padding[0], pady=(0, builder_button_padding[1]))
resistor_button = wire_button = ttk.Button(builder, image=resistor_imgs['horizontal'], command=select_resistor).grid(
    row=2, column=1, padx=(0, builder_button_padding[0]), pady=(0, builder_button_padding[1]))
capacitor_button = wire_button = ttk.Button(builder, image=capacitor_imgs['horizontal'], command=select_capacitor).grid(
    row=2, column=2, padx=(0, builder_button_padding[0]), pady=(0, builder_button_padding[1]))

labelframe = ttk.LabelFrame(options_view, text="This is a LabelFrame").grid(
    row=3, column=0, sticky='w')


dir = 1
cw = bool(dir)


def run_circuit():
    # Run circuit and update labels
    global circuit, circuit_objects, circuit_objects_list, R_eq, capacitors, style
    style.theme_use(style_str)
    # Get origin, end, and already_visited
    # end is battery location, origin is 2 away, already visited is 1 away
    for i, row in enumerate(circuit):
        for j, item in enumerate(row):
            if item == 5:
                end = (i, j)

    # get neighbors for battery
    i, j = end
    up = (i - 1, j)
    down = (i + 1, j)
    right = (i, j + 1)
    left = (i, j - 1)
    possibilities = [up, down, right, left]
    neighbors = []
    for possibility in possibilities:
        try:
            value = ti(circuit, possibility)
            if value != 0:
                neighbors.append(possibility)
        except IndexError:
            continue

    if len(neighbors) != 2:
        raise ValueError("batter not connected properly")
    already_visited = []
    if neighbors[0][0] == neighbors[1][0]:
        # horizontal
        if cw:
            already_visited.append(left)
        else:
            already_visited.append(right)
    else:
        # vertical
        if cw:
            already_visited.append(up)
        else:
            already_visited.append(down)

    # repeat for origin
    i, j = already_visited[0]
    up = (i - 1, j)
    down = (i + 1, j)
    right = (i, j + 1)
    left = (i, j - 1)
    possibilities = [up, down, right, left]
    neighbors = []
    for possibility in possibilities:
        try:
            value = ti(circuit, possibility)
            if value != 0 and value != 5:
                neighbors.append(possibility)
        except IndexError:
            continue
    origin = neighbors[0]
    current_path = []
    print(
        origin,
        ti(circuit, origin),
        already_visited,
        ti(circuit, already_visited[0]),
        end,
        ti(circuit, end),
    )
    paths = get_path(origin, current_path, already_visited, end)

    # New approach

    # Iterate through each step, checking the item at step
    x_path = []
    circuit_objs = []

    skip_until = False
    target = (0, 0)
    if isinstance(paths[0], tuple):
        paths = [paths]
    for i, step in enumerate(paths[0][1:]):
        if skip_until and step != target:
            continue

        skip_until = False
        item = ti(circuit, step)
        x_path.append(step)

        # print(item)

        # Check for resistor:
        if item == 6:
            circuit_objs.append(ti(circuit_objects, step))

        elif item == 7:
            circuit_objs.append(ti(circuit_objects, step))

        # Check for node:
        elif item == 2:
            previous_item = ti(circuit, paths[0][i])
            # Generate new paths starting at this node:

            new_paths = get_path(step, [], [paths[0][i]], end)

            # print_path(new_path)
            # Find the end, when num of input and output nodes are equal
            num_input = 0
            num_output = 0
            # print("newpaths0")
            # print_path(new_paths[0])
            for new_step in new_paths[0]:

                new_item = ti(circuit, new_step)
                if new_item == 2:
                    num_input += 1
                elif int(new_item) == 3:
                    num_output += 1
                if num_input == num_output:
                    ending = new_step
                    break
            # Shorten the paths
            shortened_paths = []
            for new_path in new_paths:
                shortened_path = new_path[: new_path.index(ending) + 1]
                if shortened_path not in shortened_paths:
                    shortened_paths.append(
                        new_path[: new_path.index(ending) + 1])
                    # print_path(new_path[:new_path.index(ending)+1])
            # print(shortened_paths)

            circuit_objs.append(ParallelCell(shortened_paths))
            skip_until = True
            target = ending

    # print_path(x_path)
    print("circuit_items", circuit_objs)

    circuit_resistance = sum([x.resistance for x in circuit_objs])
    print("resistance", circuit_resistance)
    circuit_objs = CircuitSegment(circuit_objs)
    #R_eq = sum([x.resistance for x in circuit_objs])
    R_eq = circuit_objs.resistance
    V_tot = ti(circuit_objects, end).voltage
    I_tot = V_tot / R_eq
    C_eq = circuit_objs.capacitance
    print("equivalent capacitance: ", C_eq)
    for item in circuit_objs.contents:
        item.voltage = item.resistance * I_tot

    # We can reduce the circuit such that it only has 1 capacitor of capacitance C_eq and 1 resistor of R_eq

    # Voltage of capacitor is V_tot - V_res = V_tot - R_eq*I_tot

    # V_c = V_tot - R_eq*I_tot
    V_c = V_tot
    Q = C_eq * V_c

    # Set each capacitor in series to have a charge of Q
    circuit_objs.charge = Q
    for capacitor in capacitors:
        capacitor.times = []
        capacitor.charges = []
    # compute for 10 time constants
    print("current_circuit: ", circuit_objs)
    circuit_tau = R_eq * C_eq
    for cycle in range(10):
        current_time = cycle * circuit_tau
        for capacitor in capacitors:
            current_charge = capacitor.charge * (1 - math.exp(-cycle))
            capacitor.times.append(current_time)
            capacitor.charges.append(current_charge)




    if len(capacitors) > 0:
        fig, ax = plt.subplots(nrows=len(capacitors), ncols=1)

        for i, capacitor in enumerate(capacitors):

            x_new = np.linspace(0, capacitor.times[-1], 300)
            a_BSpline = interpolate.make_interp_spline(
                capacitor.times, capacitor.charges)
            y_new = a_BSpline(x_new)
            try:
                ax[i].plot(x_new, y_new)
            except TypeError:
                ax.plot(x_new, y_new)
        plt.show()


    #EXPERIMENTAL
    things = {'wire':[], 'input':[], 'output':[], 'resistor':[], 'battery':[], 'capacitor':[]}
    for item in circuit_objects_list:
        if isinstance(item, Wire):
            things['wire'].append(item)

        elif isinstance(item, InputNode):
            things['input'].append(item)

        elif isinstance(item, OutputNode):
            things['output'].append(item)

        elif isinstance(item, Resistor):
            things['resistor'].append(item)

        elif isinstance(item, Battery):
            things['battery'].append(item)

        elif isinstance(item, Capacitor):
            things['capacitor'].append(item)

    print(things)





    print("total_current", I_tot)
    print(R_eq)


run_button = ttk.Button(options_view, text="Run",
                        command=run_circuit).grid(row=4, column=0, pady=padding[1])


def toggle_labels():
    global draw_labels
    draw_labels ^= True
    draw_circuit()


labels_button = ttk.Checkbutton(
    options_view, text="Hide Labels", command=toggle_labels).grid(row=6, sticky=W)


clear_button = ttk.Button(options_view, text="Clear", command=clear_circuit).grid(
    row=5, column=0, pady=(0, padding[1])
)

draw_grid()

mainloop()
