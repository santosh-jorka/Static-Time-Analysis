from di_tdi_values import main_function



memory_map = {}
input_String_capacitance_Gates={}
stack = []
fanin_connections={}
fanout_connections = {}
def main1():
    # Open the file
    with open('ckt_details.txt', 'r') as file:
        # Read the lines of the file
        lines = file.readlines()

        # Flag to indicate when to start reading after Fanin section
        start_reading = False

        # Dictionary to store the Fanin connections


        # Flag to indicate whether to start reading fanout connections
        read_fanout = False
        outputs =[]

        # Loop through the lines
        for line in lines:
            # Check if the line starts with 'Fanin'
            if not line:
                continue
            if line.startswith('Fanout'):
                # Set the flag to start reading fanout connections
                read_fanout = True
                continue

            # If the flag is set, start reading fanout connections
            if read_fanout and not line.startswith('Fanin'):
                # Split the line by colon to separate the key and values

                parts = line.strip().split(":")
                if parts and parts != ['']:
                    gate_name1 = parts[0].strip()


                # Trim any extra whitespace from the values and split them by comma
                    #print(parts)
                    inputs1 = parts[1].strip().split(', ')
                    fanout_connections[gate_name1] = inputs1
                    for input in inputs1:
                        if input.startswith("OUTPUT"):
                            outputs.append(gate_name1)
            if line.startswith('Fanin') :
                # Set the flag to True to start reading
                read_fanout = False
                start_reading = True
            elif start_reading:
                # Split the line by ':'
                parts = line.strip().split(':')

                if parts and parts !=['']:
                # Extract the gate name and its inputs
                    gate_name = parts[0].strip()

                    inputs = parts[1].strip().split(', ')
                    for input in inputs:
                        if input.startswith("INPUT"):
                            add_element_to_dict(input,gate_name)

                # Store the gate name and its inputs in the dictionary
                fanin_connections[gate_name] = inputs

    # Print the Fanin connections
    print(fanout_connections)
    for gate in fanin_connections:
        stack.append(gate)
        calculate_output_value(gate,{})
        #print(memory_map)
        if stack:
            stack.pop()
    return fanin_connections,fanout_connections,outputs

def add_element_to_dict( key, element):
    if key in input_String_capacitance_Gates:
        # Key exists, append element to the list
        input_String_capacitance_Gates[key].append(element)
    else:
        # Key does not exist, add key with list containing element
        input_String_capacitance_Gates[key] = [element]


def getAiValue(mem_map_values,output_gate):
    aiValueList =[]
    ai=0
    ti=0
    max=-1
    if output_gate == "AND-U34":
        for self in mem_map_values:
             print( f"STA(input_gate_name={self.input_gate_name}, gate_name={self.gate_name}, ai={self.ai}, ti={self.ti}, cl={self.cl}, di={self.di}, tdi={self.tdi}), rat={self.rat}), slack ={self.slack})")

    for value in mem_map_values:
        if len(mem_map_values) >2:
            value.di= value.di * len(mem_map_values)/2
            value.tdi = value.tdi * len(mem_map_values)/2
        if value.ai + value.di > max:
            max = value.ai + value.di
            ai=value.ai + value.di
            ti=value.tdi
    return ai,ti


def calculate_output_value(output_gate,gate_dict):
    #print(output_gate)
    if output_gate == "INPUT-INSTQUEUE_REG_1__0__SCAN_IN":
        print(stack)
    #print(memory_map)
    if len(stack) == 0:
        return 1
    if output_gate in memory_map and not output_gate.startswith("INPUT"):
        stack.pop()
        if stack:
            return calculate_output_value( stack[-1],gate_dict)

    if output_gate.startswith("INPUT"):
        gateName=gate_dict[output_gate]
        if output_gate == "INPUT-STATO_REG_1__SCAN_IN":
            print(gateName)
        if output_gate in memory_map:
            memory_map[output_gate].append(main_function(output_gate,gateName,0,0.002,calculate_capacitance_value(output_gate)))
        else:
            memory_map[output_gate]= [main_function(output_gate,gateName,0,0.002,calculate_capacitance_value(output_gate))]

        stack.pop()
        calculate_output_value( stack[-1],gate_dict )

    if output_gate in fanin_connections:
        input_gates = fanin_connections[output_gate]
        #print(output_gate,input_gates)
        size = 0
        isSizeSame = False
        mem_map_values = []
        #if output_gate == "AND-199":
            #print(input_gates)
        for input_gate in input_gates:
            if input_gate in memory_map:

                values = memory_map[input_gate]
                for value in values:
                    if value.gate_name == output_gate:
                        mem_map_values.append(value)
                        size += 1
        #if output_gate == "AND-199":
            #print(size)
        if size == len(input_gates):
            isSizeSame =True

        if isSizeSame:
            ai,ti = getAiValue(mem_map_values,output_gate)
            #if output_gate == "AND-199":
                #print(ai,ti)
            #gateName = gate_dict[output_gate]
            input_to_list = fanout_connections[output_gate]
            #print(input_to_list)
            mem_list=[]
            for input_to in input_to_list:
                mem_list.append(main_function(output_gate,input_to, ai,ti,0))
            memory_map[output_gate] = mem_list
            if stack:
                stack.pop()
            if stack:
                calculate_output_value(stack[-1], gate_dict)
        else:
            for input_gate in  input_gates:
                stack.append(input_gate)
                gate_dict[input_gate] = output_gate
            calculate_output_value(stack[-1],gate_dict)


    return 1

def calculate_capacitance_value(input):
    gate_input_capacitance = {
        "NAND": 1.599032,
        "NOR": 1.714471,
        "AND": 0.918145,
        "OR": 0.946814,
        "XOR": 2.411453,
        "INV": 1.700230,
        "NOT": 1.700230,
        "BUFF": 0.974659,
        "OUTPUT": 6.80092  # Default capacitance for output gates
    }

    gateList = input_String_capacitance_Gates[input]
    capacitance=0
    for gate in gateList:
        gateName = gate.split('-')[0]
        capacitance+=gate_input_capacitance[gateName]

    return capacitance


def get_min_rat_value(output):
    outputs = memory_map[output]
    min = 1000
    for sat in outputs:
        if sat.rat < min :
            min = sat.rat
    return min


def is_recursion_true(outputs,fan_in):
    for output in outputs:
        if output in fan_in:
            return False
    return True

def is_havin_outPut_in_list(fanOutList):
    for fanout in fanOutList:
        if fanout.startswith("OUTPUT"):
            return True;

    return False


def backward_traversal(fan_in,fan_out,outputs,ai):
    
    outputs_list = []
    #print("11111111111111111111111111111111111111")
    #print(outputs)
    if is_recursion_true(outputs,fan_in):
        return 1
    for output in outputs:
        if output in fan_out and is_havin_outPut_in_list(fan_out[output]):
            sat_list = memory_map[output]
            for sat in sat_list:
                if sat.gate_name.startswith("OUTPUT"):
                    sat.rat = 1.1 * ai
                    sat.slack = sat.rat - sat.ai
        if output in fan_in:
            inputs = fan_in[output]
            for input in inputs:
                if input not in outputs_list:
                    outputs_list.append(input)
                sat_list = memory_map[input]
                for sat in sat_list:
                    if sat.gate_name == output:
                        sat.rat = get_min_rat_value(output) - sat.di
                        sat.slack = sat.rat -sat.ai

    backward_traversal(fan_in,fan_out,outputs_list,ai)
    return 1


def find_min_slack_in_sat(sat_List):
    min = 1000
    return_sat = {}
    for sat in sat_List:
        #print(f"STA(input_gate_name={sat.input_gate_name}, gate_name={sat.gate_name}, ai={sat.ai}, ti={sat.ti}, cl={sat.cl}, di={sat.di}, tdi={sat.tdi}), rat={sat.rat}), slack ={sat.slack})")
        if sat.slack<min: # and not sat.gate_name.startswith("OUTPUT"):
            min=sat.slack
            return_sat = sat

    return return_sat



def find_critical_path(fan_in,fan_out,outputs,path):
    #print(outputs)
    min_sat_list = []
    if is_recursion_true(outputs,fan_in):
        for output in outputs:
            sat_List = memory_map[output]
            min_sat_list.append(find_min_slack_in_sat(sat_List))

        min_slack_sat = find_min_slack_in_sat(min_sat_list)
        path.append(min_slack_sat.gate_name)
        path.append(min_slack_sat.input_gate_name)
        return 1

    for output in outputs:
        sat_List = memory_map[output]
        min_sat_list.append(find_min_slack_in_sat(sat_List))

    min_slack_sat = find_min_slack_in_sat(min_sat_list)
    path.append(min_slack_sat.gate_name)
    str = min_slack_sat.input_gate_name
    if not str.startswith("INPUT"):
        find_critical_path(fan_in,fan_out,fan_in[min_slack_sat.input_gate_name],path)

    return 1


def get_circuit_delay(outputs):
    max = -1
    for gate, stas in memory_map.items():
        if gate in outputs:
            for sta in stas:
                if sta.ai >max:
                    max=sta.ai
    return max

def write_in_file(outputs,critical_path):
    print(critical_path)
    circuit_delay = get_circuit_delay(outputs)
    line_list =[]
    line1 = "Circuit delay: "+ str(circuit_delay*1000)+"ps"
    line_list.append("\n")
    line2 = "Gate slacks: "
    line_list.append(line1)
    line_list.append("\n")
    line_list.append(line2)
    line_list.append("\n")
    for gate, stas in memory_map.items():
        if gate.startswith("INPUT"):
            min_sat = find_min_slack_in_sat(stas)
            line = min_sat.input_gate_name+ " : "+ str(min_sat.slack *1000)+"ps"
            line_list.append(line)
            line_list.append("\n")
    for gate, stas in memory_map.items():
        min_sat = find_min_slack_in_sat(stas)
        strin=min_sat.gate_name
        if strin.startswith("OUTPUT"):
            line = min_sat.gate_name + " : " + str(min_sat.slack * 1000) + "ps"
            line_list.append(line)
            line_list.append("\n")
    for gate, stas in memory_map.items():
        if not gate.startswith("INPUT"):
            min_sat = find_min_slack_in_sat(stas)
            line = min_sat.gate_name + " : " + str(min_sat.slack * 1000) + "ps"
            line_list.append(line)
            line_list.append("\n")

    line_list.append("\n")
    line3 = "Critical path: "
    line_list.append(line3)

    critical_path = critical_path[::-1]
    line4 =""
    for gate in critical_path:
        line4 = gate +","
        line_list.append(line4)




    with open('ckt_traversal.txt', 'w') as file:
        file.writelines(line_list)


def find_max_ai_sta(sat_list):
    max=-1
    max_sta = {}
    for sta in sat_list:
        if sta.ai > max:
            max = sta.ai
            max_sta = sta
    return max_sta


def main2():
    fan_in, fan_out, outputs = main1()
    #print(outputs)
    max_sta_list =[]
    for output in outputs:
        if output in memory_map:
            sat_list = memory_map[output]
            max_sta_list.append(find_max_ai_sta(sat_list))
    max_rta_sta = find_max_ai_sta(max_sta_list)

    print(max_rta_sta)
    print("fan_in**************************************")
    print(fan_in)
    print("fan_out**************************************")
    print(fan_out)
    backward_traversal(fan_in, fan_out, outputs,max_rta_sta.ai)
    path = []
    critical_path = find_critical_path(fan_in, fan_out, outputs, path)
    print("bcssc;sc")
    #print(path)
    for key, values in memory_map.items():
        print(key)
        for self in values:
            print(
                f"STA(input_gate_name={self.input_gate_name}, gate_name={self.gate_name}, ai={self.ai}, ti={self.ti}, cl={self.cl}, di={self.di}, tdi={self.tdi}), rat={self.rat}), slack ={self.slack})")

    write_in_file(outputs,path)

if __name__ == "__main__":
    main2()