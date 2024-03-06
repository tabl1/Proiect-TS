import tkinter as tk
import schemdraw as schem
import schemdraw.elements as e
import matplotlib
matplotlib.rcParams['figure.max_open_warning'] = 70
# bug de rezolvat cand dau back dintr un nod nou format

def orientation(p, q, r):
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    if val == 0:
        return 0  # Collinear
    return 1 if val > 0 else 2  # Clockwise or counterclockwise


def on_segment(p, q, r):
    return (
            (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0])) and
            (q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1]))
    )


def point_on_line_segment(point, start, end):
    return orientation(start, point, end) == 0 and on_segment(start, point, end)


def check_intersection_with_lines(point, lines):
    count = 0
    for line in lines:
        start, end = line
        if point_on_line_segment(point, start, end):
            count += 1
            if count >= 2:
                return True
    return False


def approximate_point(point, tolerance=1e-6):
    x, y = point
    return round(x), round(y) if abs(x - round(x)) <= tolerance and abs(y - round(y)) <= tolerance else (x, y)


def approximate_lines_vector(lines_vector, tolerance=1e-6):
    approximated_vector = []

    for line in lines_vector:
        start, end = line
        approximated_start = approximate_point(start, tolerance)
        approximated_end = approximate_point(end, tolerance)
        approximated_vector.append((approximated_start, approximated_end))

    return approximated_vector


def create_lines_vector():
    lines_vector = []

    for element in d.elements:
        if not isinstance(element, e.Dot):
            x1, y1 = element.start
            x2, y2 = element.end
            lines_vector.append(((x1, y1), (x2, y2)))

    return lines_vector

def check_intersection(point_next):
    global for_node
    elements = d.elements
    coordinate_vector = create_lines_vector()
    coordinate_vector = approximate_lines_vector(coordinate_vector)
    point_next = approximate_point(point_next)
    if check_intersection_with_lines(point_next, coordinate_vector):
        elements.pop()
        d.add(e.Dot(label='Node').at(point_next))
        for_node = True

def create_drawing():
    e.style(e.STYLE_IEC)
    return schem.Drawing()


def add_component(component_type):
    global resistance_index, coil_index, capacitor_index, source_index, point_next, for_next_bug

    delete_point()

    if for_next_bug:
        d.elements.remove(d.elements[-1])
        for_next_bug = False

    if component_type == 'resistor':
        d.add(e.Resistor(label='R' + str(resistance_index), d=direction))
        next_point()
        resistance_index += 1
        check_intersection(point_next)
    elif component_type == 'coil':
        d.add(e.Inductor(label='L' + str(coil_index), d=direction))
        next_point()
        check_intersection(point_next)
        coil_index += 1
    elif component_type == 'capacitor':
        d.add(e.Capacitor(label='C' + str(capacitor_index), d=direction))
        next_point()
        check_intersection(point_next)
        capacitor_index += 1
    elif component_type == 'voltage_source':
        d.add(e.SourceV(label='V' + str(source_index), d=direction))
        next_point()
        check_intersection(point_next)
        source_index += 1
    elif component_type == 'line':
        d.add(e.Line(d=direction))
        next_point()
        check_intersection(point_next)

    update_svg()


def next_point():
    global point_next
    if d.elements:
        last = d.elements[-1]
        d.add(e.Dot(label='NEXT', color='Red').at(last.end))
        point_next = last.end


def delete_point():
    global for_node
    if d.elements and not for_node:
        d.undo()
    for_node = False


def connect_components():
    delete_point()
    first = d.elements[0]
    last = d.elements[-1]
    if direction == 'up' or direction == 'down':
        d.add(e.Wire('|-').at(first.start).to(last.end))
    else:
        d.add(e.Wire('-|').at(first.start).to(last.end))

    d.add(e.Dot().at(first.start))
    d.add(e.Dot().at(last.end))
    update_svg()

def go_back():
    global for_next_bug
    if len(d.elements) >= 3:
        last_element = d.elements[-3]
        d.elements.pop()
        if len(d.elements) >= 2:
            d.add(e.Dot(label='NEXT', color='red').at(last_element.end))
            d.add(e.Line(color='None'))
        update_svg()
        for_next_bug = True

def update_direction(new_direction):
    global direction
    direction = new_direction


def update_svg():
    image_data = d.get_imagedata(fmt="png")
    with open("temp.png", "wb") as img_file:
        img_file.write(image_data)
    photo = tk.PhotoImage(file="temp.png")
    image_label.configure(image=photo)
    image_label.image = photo


def undo_button():
    d.undo()
    update_svg()

def on_closing():
    root.destroy()
    root.quit()

def main():
    global canvas, d, direction, resistance_index, coil_index, capacitor_index, source_index, for_node, image_label, for_next_bug, root
    root = tk.Tk()
    canvas = tk.Canvas(root, width=400, height=20)
    canvas.pack()

    d = create_drawing()
    direction = 'right'
    resistance_index = 1
    coil_index = 1
    capacitor_index = 1
    source_index = 1
    for_node = False
    for_next_bug = False

    component_buttons = [
        ('Resistor', 'resistor'),
        ('Coil', 'coil'),
        ('Capacitor', 'capacitor'),
        ('Voltage Source', 'voltage_source'),
        ('Line', 'line')
    ]

    for text, component_type in component_buttons:
        button = tk.Button(root, text='Add ' + text, command=lambda t=component_type: add_component(t))
        button.pack()

    connect_button = tk.Button(root, text='Connect First and Last', command=connect_components)
    connect_button.pack()

    direction_buttons = [
        ('Up', 'up'),
        ('Down', 'down'),
        ('Left', 'left'),
        ('Right', 'right')
    ]

    for text, new_direction in direction_buttons:
        button = tk.Button(root, text=text, command=lambda d=new_direction: update_direction(d))
        button.pack()

    image_label = tk.Label(root)
    image_label.pack()

    button = tk.Button(root, text='Undo', command=undo_button)
    button.pack()

    button = tk.Button(root, text='Back', command=go_back)
    button.pack()


    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()