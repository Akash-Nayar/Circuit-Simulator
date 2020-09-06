import pygame, sys, math
from tkinter import *
import tkinter as tk

from PIL import Image, ImageTk

root = Tk()
display_width = 1280
display_height = 720

circuit_width = 50
circuit_height = 30

cell_size = 20
canvas_width = circuit_width * cell_size
canvas_height = circuit_height * cell_size

circuit_view = Canvas(root,
           width=canvas_width,
           height=canvas_height)




circuit = [[0] * circuit_width for _ in range(circuit_height)]
circuit_objects = [[0] * circuit_width for _ in range(circuit_height)]

end = (10, 5)
origin = (10, 3)
already_visited = [(10, 4)]


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


print_circuit(circuit)


def ti(arr, tup):
    if 0 > tup[0] or tup[0] >= len(arr) or 0 > tup[1] or tup[1] >= len(arr[0]):
        return 0
    return arr[tup[0]][tup[1]]


current_path = []


def get_path(position, curr_path, visited, end_point):
    curr_path.append(position)
    visited.append(position)
    if position == end_point:
        return curr_path
    above = (position[0] - 1, position[1])
    below = (position[0] + 1, position[1])
    right = (position[0], position[1] + 1)
    left = (position[0], position[1] - 1)
    possibilities = [above, below, right, left]
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
            # Check dimentionalityt
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
wire_straight_img = Image.open('images/wire_straight.png')
wire_straight_imgs = {
    "horizontal": ImageTk.PhotoImage(wire_straight_img),
    "vertical": ImageTk.PhotoImage(wire_straight_img.rotate(90))
}

wire_corner_img = Image.open('images/wire_corner.png')
wire_corner_imgs = {
    "right_down": ImageTk.PhotoImage(wire_corner_img),
    "down_left": ImageTk.PhotoImage(wire_corner_img.rotate(90)),
    "left_up": ImageTk.PhotoImage(wire_corner_img.rotate(180)),
    "up_right": ImageTk.PhotoImage(wire_corner_img.rotate(270))
}
wire_junction_img = Image.open('images/wire_junction.png')
wire_junction_imgs = {
    "up": ImageTk.PhotoImage(wire_junction_img),
    "left": ImageTk.PhotoImage(wire_junction_img.rotate(90)),
    "down": ImageTk.PhotoImage(wire_junction_img.rotate(180)),
    "right": ImageTk.PhotoImage(wire_junction_img.rotate(270))
}
wire_cross_img = Image.open('images/wire_cross.png')
wire_cross_imgs = {"any": ImageTk.PhotoImage(wire_cross_img)}

resistor_img = Image.open('images/resistor.png')
resistor_imgs = {
    "horizontal": ImageTk.PhotoImage(resistor_img),
    "vertical": ImageTk.PhotoImage(resistor_img.rotate(90))
}

battery_img = Image.open('images/battery.png')
battery_imgs = {
    "right": ImageTk.PhotoImage(battery_img),
    "down": ImageTk.PhotoImage(battery_img.rotate(90)),
    "left": ImageTk.PhotoImage(battery_img.rotate(180)),
    "up": ImageTk.PhotoImage(battery_img.rotate(270))
}


class CircuitItem:
    imgs = {}
    default_state = None
    default_direction = None

    def __init__(self):
        self._voltage = 0
        self._resistance = 0
        self._current = 0

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

    def draw(self, i, j, direction=None, state=None):
        try:
            circuit_view.create_image(j * 20, i * 20, anchor=NW, image=self.imgs[state if state is not None else self.default_state][direction if direction is not None else self.default_direction])
        except IndexError:
            pass


class CircuitSegment(CircuitItem):
    def __init__(self, contents):
        self.contents = contents
        self._voltage = 0
        self._resistance = 0
        self._current = 0

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
        self._resistance = resistance

    @property
    def resistance(self):
        return super().resistance


class Resistor(CircuitItem):
    imgs = resistor_imgs
    default_direction = "horizontal"

    def __init__(self, resistance):
        self._resistance = resistance

    @property
    def resistance(self):
        return super().resistance

    def __repr__(self):
        return f"Resistor({self.resistance})"

    def draw(self, i, j, direction=None):
        try:
            circuit_view.create_image(j*20, i*20, anchor=NW, image=self.imgs[self.default_direction if direction is None else direction])
        except IndexError:
            pass


class ParallelCell(CircuitItem):
    def __init__(self, paths):
        self.paths = paths
        self.origin = paths[0][0]
        self.end = paths[0][-1]
        self._voltage = 0
        # Check paths for parallels within
        print("got here")
        # for path in paths:
        # print_path(path)

        # 2D, each row is a path, each column represent object
        self.paths_items = []

        new_nodes = []
        for path in self.paths:
            # print_path(path)

            # Check to see if current path contains one of the new nodes, disregard if so
            if any(node in new_nodes for node in path):
                # print('path has new node:')
                # print_path(path)
                continue

            # print('path does not have new node:')
            # print_path(path)

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
                    path_items.append(Resistor(10))

                # If it is an input node
                if item == 2:
                    new_nodes.append(step)
                    previous_item = ti(circuit, paths[0][i])
                    # Generate new paths starting at this node:

                    new_paths = get_path(step, [], [path[i]], end)

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
        return 0 if sum == 0 else round(1 / sum, 3)


def get_items(cir_objs):
    current_path = []
    paths = get_path(origin, current_path, already_visited, end)

    print("paths", paths)

    for path in paths:
        print_path(path)

    # New approach

    # Iterate through each step, checking the item at step
    x_path = []
    circuit_items = []

    skip_until = False
    target = (0, 0)
    for i, step in enumerate(paths[0][1:]):
        if skip_until and step != target:
            continue

        skip_until = False
        item = ti(circuit, step)
        x_path.append(step)

        # print(item)

        # Check for resistor:
        if item == 6:
            circuit_items.append(Resistor(10))

        # Check for node:
        if item == 2:
            previous_item = ti(circuit, paths[0][i])
            # Generate new paths starting at this node:

            new_paths = get_path(step, [], [paths[0][i]], end)

            # print_path(new_path)
            # Find the end, when num of input and output nodes are equal
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
                    shortened_paths.append(new_path[: new_path.index(ending) + 1])
                    # print_path(new_path[:new_path.index(ending)+1])
            # print(shortened_paths)

            circuit_items.append(ParallelCell(shortened_paths))
            skip_until = True
            target = ending

    # print_path(x_path)
    print("circuit_items", circuit_items)

    circuit_resistance = sum([x.resistance for x in circuit_items])
    print("resistance", circuit_resistance)

    R_tot = sum([x.resistance for x in circuit_items])
    V_tot = 15
    I_tot = V_tot / R_tot
    for item in circuit_items:
        item.voltage = item.resistance * I_tot

    for item in circuit_items[0].paths_items:
        print(item.resistance, item.current, item.voltage)

    print("total_current", I_tot)
    print(circuit_items[0].resistance)


def draw_grid():
    blockSize = 20  # Set the size of the grid block

    for i in range(circuit_width + 1):
        circuit_view.create_line(cell_size * i, 0, cell_size * i, canvas_height, fill="#B3B3B3")
    for j in range(circuit_height + 1):
        circuit_view.create_line(0, cell_size*j, canvas_width, cell_size*j, fill="#B3B3B3")
# GUI

def draw_circuit():
    global circuit, circuit_objects
    print(circuit)
    circuit_view.delete(ALL)
    draw_grid()
    for i, row in enumerate(circuit):
        for j, item in enumerate(row):
            if item == 0:
                continue

            elif int(item) in [1, 2, 3, 4, 5, 6]:
                obj = circuit_objects[i][j]
                # Check for neighbors
                up = (i - 1, j)
                down = (i + 1, j)
                right = (i, j + 1)
                left = (i, j - 1)
                possibilities = [up, down, right, left]
                neighbors = []
                for possibility in possibilities:
                    try:
                        value = ti(circuit, possibility)
                        if item == 6:
                            print(possibility, value)
                        if value != 0:
                            neighbors.append(possibility)
                    except IndexError:
                        continue
                print(obj, len(neighbors))
                if len(neighbors) == 0:
                    obj.draw(i, j)
                elif len(neighbors) == 1:
                    # if on same row, horizontal
                    if neighbors[0][0] == i:
                        obj.draw(i, j, direction="horizontal")
                        print(type(obj), 'horizontal')
                    else:
                        obj.draw(i, j, direction="vertical")
                        print(type(obj), 'vertical')
                elif len(neighbors) == 2:
                    # Either straight or corner piece

                    # If straight, check to see if either x or y of both are equal:

                    if neighbors[0][0] == neighbors[1][0]:
                        # same row - horizontal
                        if item not in [5]:
                            obj.draw(i, j, direction="horizontal")
                            # surface.blit(wire_straight_imgs['horizontal'], (20*j, 20*i))
                        elif item == 5:
                            if dir == 1:
                                surface.blit(
                                    battery_imgs["right"], (20 * j, 20 * i)
                                )
                            else:
                                surface.blit(
                                    battery_imgs["left"], (20 * j, 20 * i)
                                )


                    elif neighbors[0][1] == neighbors[1][1]:
                        # same column - vertical
                        if item not in [5]:
                            obj.draw(i, j, direction="vertical")
                            # surface.blit(wire_straight_imgs['vertical'], (20 * j, 20 * i))
                        elif item == 5:
                            if dir == 1:
                                surface.blit(
                                    battery_imgs["down"], (20 * j, 20 * i)
                                )
                            else:
                                surface.blit(
                                    battery_imgs["up"], (20 * j, 20 * i)
                                )


                    else:
                        # corner
                        if item in [1, 2, 3]:
                            if down in neighbors:
                                # down and right - default
                                if right in neighbors:
                                    # right down
                                    obj.draw(
                                        i, j, state="corner", direction="right_down"
                                    )
                                    # surface.blit(wire_corner_imgs['right_down'], (20 * j, 20 * i))
                                else:
                                    # down left
                                    obj.draw(
                                        i, j, state="corner", direction="up_right"
                                    )
                                    # surface.blit(wire_corner_imgs['up_right'], (20 * j, 20 * i))
                            else:
                                # down and right - default
                                if right in neighbors:
                                    # upright
                                    obj.draw(
                                        i, j, state="corner", direction="down_left"
                                    )
                                    # surface.blit(wire_corner_imgs['down_left'], (20 * j, 20 * i))
                                else:
                                    # left-up left
                                    obj.draw(
                                        i, j, state="corner", direction="left_up"
                                    )
                                    # surface.blit(wire_corner_imgs['left_up'], (20 * j, 20 * i))

                elif len(neighbors) == 3:
                    for possibility in possibilities:
                        if possibility not in neighbors:
                            if possibility == down:
                                obj.draw(
                                    i, j, state="junction", direction="down"
                                )
                                # surface.blit(wire_junction_imgs['down'], (20 * j, 20 * i))
                            elif possibility == left:
                                obj.draw(
                                    i, j, state="junction", direction="left"
                                )
                                # surface.blit(wire_junction_imgs['left'], (20 * j, 20 * i))
                            elif possibility == up:
                                obj.draw(i, j, state="junction", direction="up")
                                # surface.blit(wire_junction_imgs['up'], (20 * j, 20 * i))
                            else:
                                obj.draw(
                                    i, j, state="junction", direction="right"
                                )
                                # surface.blit(wire_junction_imgs['right'], (20 * j, 20 * i))

                else:
                    obj.draw(i, j, state="cross", direction="any")



circuit_view.pack()
def key(event):
    print("pressed", repr(event.char))



x, y = (0, 0)

def add_resistor():
    add_item(6)

def add_battery():
    add_item(5)

def add_input_node():

    add_item(2)

def add_output_node():
    add_item(3)

def delete_item():
    add_item(0)





def add_item(code):
    global x, y, circuit, circuit_objects
    if code == 0:
        new_obj = 0
    if code == 1:
        new_obj = Wire()

    elif code == 6:
        new_obj = Resistor(10)

    circuit[y][x] = code
    circuit_objects[y][x] = new_obj
    draw_circuit()






def choose_object(selection):
    global next_object

m = Menu(root, tearoff=0)
m.add_command(label="Input Node", command=add_input_node)
m.add_command(label="Output Node", command=add_output_node)
m.add_command(label="Resistor", command=add_resistor)
m.add_command(label="Battery", command=add_battery)
m.add_separator()
m.add_command(label="Delete", command=delete_item)


def right_click(event):
    global next_item, x, y
    x, y = (event.x // 20, event.y // 20)

    print("right clicked at", event.x, event.y)
    try:
        m.post(event.x_root, event.y_root)
    finally:
        m.grab_release()
        print('here')

        #print(next_item)

def left_click(event):
    global circuit, circuit_objects
    x, y = (event.y // 20, event.x // 20)
    circuit[x][y] = 1
    circuit_objects[x][y] = Wire()
    print("clicked at", x, y)
    draw_circuit()


#draw the grid

circuit_view.bind("<Key>", key)
circuit_view.bind("<Button-1>", left_click)
circuit_view.bind("<Button-3>", right_click)



draw_grid()
mainloop()




# 1 = cw, 2 = ccw
dir = 1
FPS = 60

