import re
from bisect import bisect_left
import capacitance
from STA import STA

gate_name_link = {"NAND": "NAND2_X1","NOR": "NOR2_X1", "AND":"AND2_X1", "OR":"OR2_X1", "XOR":"XOR2_X1", "INV":"INV_X1", "BUFF":"BUF_X1", "INV_X1":"INV_X1"}
def parse_input_file_di(file_name):
    gate_data = {}
    with open(file_name, 'r') as file:
        lines = file.readlines()

    current_cell = None
    for idx, line in enumerate(lines):
        line = line.strip()
        if line.startswith('cell:'):
            current_cell = line.split(':')[1]
            gate_data[current_cell] = {'input_slews': [], 'load_caps': [], 'delays': []}
        elif current_cell is not None:
            if line.startswith('input slews:'):
                gate_data[current_cell]['input_slews'] = [float(x.strip()) for x in line.split(':')[1].split(',')]
            elif line.startswith('load cap:'):
                gate_data[current_cell]['load_caps'] = [float(x.strip()) for x in line.split(':')[1].split(',')]
            elif line.startswith('delays:'):
                delays = []
                for delay_line in lines[idx+1:]:
                    delay_line = delay_line.strip()
                    if delay_line.startswith('cell:') or delay_line.strip() == '':
                        break
                    delays.append([float(x) for x in delay_line.split(';')[0].split(',')])
                gate_data[current_cell]['delays'] = delays

    return gate_data


def generate_cell_data_di(gate_data, gate_name):
    return gate_data.get(gate_name, None)



def find_di(Input_gatename, file_name, gate_name, ai, ti, cl, source_count_dict):

    if gate_name.upper() == "NOT":
        gate_name = "INV"

    gate_data = parse_input_file_di(file_name)

    cell_data = gate_data.get(gate_name_link[gate_name], None)

    if cell_data is None:
        return None

    input_slews = cell_data["input_slews"]
    load_caps = cell_data["load_caps"]
    delays = cell_data["delays"]

    if not input_slews or not load_caps or not delays:
        return None

    # Convert ti and cl to floats
    ti = float(ti)
    cl = float(cl)

    # Find predecessor and successor for ti in input slews
    t_slews = sorted(input_slews)
    if ti < t_slews[0]:
        t1 = t_slews[0]
        t2 = t_slews[1]
    elif ti > t_slews[-1]:
        t1 = t_slews[-2]
        t2 = t_slews[-1]
    else:
        t_index = None
        for idx, t in enumerate(t_slews):
            if abs(ti - t) < 1e-6:  # Check for close match within tolerance
                t_index = idx
                break
        if t_index is None:  # No close match found
            t_index = bisect_left(t_slews, ti)
            #print(t_index)
        if t_index < len(t_slews) - 1:
            t1 = t_slews[t_index-1]
            t2 = t_slews[t_index ]
        else:
            t1 = t_slews[-2]
            t2 = t_slews[-1]

    #print(Input_gatename,t1,t2,t_slews)
    # Find predecessor and successor for cl in load caps
    c_caps = sorted(load_caps)
    if cl < c_caps[0]:
        c1 = c_caps[0]
        c2 = c_caps[1]
    elif cl > c_caps[-1]:
        c1 = c_caps[-2]
        c2 = c_caps[-1]
    else:
        c_index = None
        for idx, c in enumerate(c_caps):
            if abs(cl - c) < 1e-6:  # Check for close match within tolerance
                c_index = idx
                break
        if c_index is None:  # No close match found
            c_index = bisect_left(c_caps, cl)
        if c_index < len(c_caps) - 1:
            c1 = c_caps[c_index-1]
            c2 = c_caps[c_index ]
        else:
            c1 = c_caps[-2]
            c2 = c_caps[-1]

    # Check for exact match in input slews and load caps
    if ti in t_slews and cl in c_caps:
        it = t_slews.index(ti)
        ic = c_caps.index(cl)
        di = delays[it][ic]
        return di

    # Check for division by zero
    if c2 == c1 or t2 == t1:
        return None

    # Get values from delays matrix for interpolation
    it1 = bisect_left(t_slews, t1)
   # print(Input_gatename,it1)
    it2 = bisect_left(t_slews, t2)
    ic1 = bisect_left(c_caps, c1)
    ic2 = bisect_left(c_caps, c2)

    # Get values from delays matrix
    v11 = delays[it1][ic1]
    v12 = delays[it1][ic2]
    v21 = delays[it2][ic1]
    v22 = delays[it2][ic2]
    #print(Input_gatename,v11,v12,v21,v22)
    # Interpolate to find di value
    #print(Input_gatename, c1, c2)
    di = ((v11 * (c2 - cl) * (t2 - ti)) +
          (v12 * (cl - c1) * (t2 - ti)) +
          (v21 * (c2 - cl) * (ti - t1)) +
          (v22 * (cl - c1) * (ti - t1))) / ((c2 - c1) * (t2 - t1))




    #print(Input_gatename,di)
    return di


import re
from bisect import bisect_left
def parse_input_file_tdi(file_name):
    gate_data = {}
    with open(file_name, 'r') as file:
        lines = file.readlines()

    current_cell = None
    for idx, line in enumerate(lines):
        line = line.strip()
        if line.startswith('cell:'):
            current_cell = line.split(':')[1]
            gate_data[current_cell] = {'input_slews': [], 'load_caps': [], 'slews': []}
        elif current_cell is not None:
            if line.startswith('input slews:'):
                gate_data[current_cell]['input_slews'] = [float(x.strip()) for x in line.split(':')[1].split(',')]
            elif line.startswith('load cap:'):
                gate_data[current_cell]['load_caps'] = [float(x.strip()) for x in line.split(':')[1].split(',')]
            elif line.startswith('slews:'):
                slews = []
                for delay_line in lines[idx+1:]:
                    delay_line = delay_line.strip()
                    if delay_line.startswith('cell:') or delay_line.strip() == '':
                        break
                    slews.append([float(x) for x in delay_line.split(';')[0].split(',')])
                gate_data[current_cell]['slews'] = slews

    return gate_data


def generate_cell_data_tdi(gate_data, gate_name):
    return gate_data.get(gate_name, None)



def find_di_tdi(Input_gatename, file_name, gate_name, ai, ti, cl, source_count_dict):
    if gate_name.upper() == "NOT":
        gate_name = "INV_X1"

    gate_data = parse_input_file_tdi(file_name)

    if gate_name not in gate_name_link:
        print(f"Error: Gate name '{gate_name}' not found in gate_name_link dictionary.")
        return None

    # Retrieve the corresponding gate name from the gate_name_link dictionary
    mapped_gate_name = gate_name_link[gate_name]

    cell_data = gate_data.get(mapped_gate_name, None)



    if cell_data is None:
        return None


    input_slews = cell_data["input_slews"]
    load_caps = cell_data["load_caps"]
    slews = cell_data["slews"]

    if not input_slews or not load_caps or not slews:
        return None

    # Convert ti and cl to floats
    ti = float(ti)
    cl = float(cl)

    # Find predecessor and successor for ti in input slews
    t_slews = sorted(input_slews)
    if ti < t_slews[0]:
        t1 = t_slews[0]
        t2 = t_slews[1]
    elif ti > t_slews[-1]:
        t1 = t_slews[-2]
        t2 = t_slews[-1]
    else:
        t_index = None
        for idx, t in enumerate(t_slews):
            if abs(ti - t) < 1e-6:  # Check for close match within tolerance
                t_index = idx
                break
        if t_index is None:  # No close match found
            t_index = bisect_left(t_slews, ti)
        if t_index < len(t_slews) - 1:
            t1 = t_slews[t_index-1]
            t2 = t_slews[t_index ]
        else:
            t1 = t_slews[-2]
            t2 = t_slews[-1]

    # Find predecessor and successor for cl in load caps
    c_caps = sorted(load_caps)
    if cl < c_caps[0]:
        c1 = c_caps[0]
        c2 = c_caps[1]
    elif cl > c_caps[-1]:
        c1 = c_caps[-2]
        c2 = c_caps[-1]
    else:
        c_index = None
        for idx, c in enumerate(c_caps):
            if abs(cl - c) < 1e-6:  # Check for close match within tolerance
                c_index = idx
                break
        if c_index is None:  # No close match found
            c_index = bisect_left(c_caps, cl)
        if c_index < len(c_caps) - 1:
            c1 = c_caps[c_index-1]
            c2 = c_caps[c_index]
        else:
            c1 = c_caps[-2]
            c2 = c_caps[-1]

    # Check for exact match in input slews and load caps
    if ti in t_slews and cl in c_caps:
        it = t_slews.index(ti)
        ic = c_caps.index(cl)
        di = slews[it][ic]
        return di

    # Check for division by zero
    if c2 == c1 or t2 == t1:
        return None

    # Get values from delays matrix for interpolation
    it1 = bisect_left(t_slews, t1)
    it2 = bisect_left(t_slews, t2)
    ic1 = bisect_left(c_caps, c1)
    ic2 = bisect_left(c_caps, c2)

    # Get values from delays matrix
    v11 = slews[it1][ic1]
    v12 = slews[it1][ic2]
    v21 = slews[it2][ic1]
    v22 = slews[it2][ic2]



    # Interpolate to find di value
    di = ((v11 * (c2 - cl) * (t2 - ti)) +
          (v12 * (cl - c1) * (t2 - ti)) +
          (v21 * (c2 - cl) * (ti - t1)) +
          (v22 * (cl - c1) * (ti - t1))) / ((c2 - c1) * (t2 - t1))



    return di




def main_function(Input_gatename, gatename, ai, ti, cl):
    gatename2 = gatename.partition('-')[0]
    if gatename.upper() == "NOT":
        gatename = "INV"
    di =0
    tdi =0
    source_count_dict={}
    capacitance_dict={}
    fanin_count_dict = {}
    capacitance_dict, source_count_dict,fanin_count_dict = capacitance.fix_input_capacitance("ckt_details.txt")
    #cl = capacitance_dict[Input_gatename]

    if gatename in fanin_count_dict:
        cl = fanin_count_dict[gatename].get(Input_gatename, 0)
        #print("cl value is",cl)

    if gatename2 != "OUTPUT":
        di = find_di(Input_gatename, "delay_LUT.txt", gatename2, ai, ti, cl, source_count_dict)
        tdi = find_di_tdi(Input_gatename, "slew_LUT.txt", gatename2, ai, ti, cl, source_count_dict)
    sta = STA(Input_gatename,gatename,ai,ti,cl,di,tdi,0,0)
    return sta


#values = main_function("Input-1", "NAND-16", 0, 0.198535,59.356700)

#print(values)



#di_NAND = find_di("delay_LUT.txt","NAND2_X1", 0, 0.198535,59.356700)

# Need to write a code to add the input values of di value and store it in a map/list/dict

#print("The di value for", di_NAND)