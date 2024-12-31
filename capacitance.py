def fix_input_capacitance(input_file):
    # Dictionary to store gate type and corresponding input capacitance
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

    # Dictionary to store desired capacitance for each gate
    capacitance_dict = {}
    # Dictionary to store the count of sources for each destination gate
    source_count_dict = {}
    # Dictionary to store fan-in capacitance for each gate
    fanin_count_dict = {}

    # Flag to indicate if we are within the Fanout or Fanin section
    in_fanout_section = False
    in_fanin_section = False

    # Read the input file and parse gate type and inputs
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("Fanout"):
                in_fanout_section = True
                in_fanin_section = False
                continue
            elif line.startswith("Fanin"):
                in_fanout_section = False
                in_fanin_section = True
                continue
            elif in_fanout_section and line:
                parts = line.split(": ")
                if len(parts) != 2:
                    print(f"Ignoring line: {line}. Malformed input.")
                    continue
                output_gate, input_gates = parts[0], parts[1]
                input_gates = input_gates.split(", ")
                total_capacitance = 0
                for gate in input_gates:
                    if gate.startswith("OUTPUT"):
                        total_capacitance += gate_input_capacitance["OUTPUT"]
                    else:
                        gate_type = gate.split("-")[0]
                        if gate_type in gate_input_capacitance:
                            total_capacitance += gate_input_capacitance[gate_type]
                            # Update source count dictionary
                            if output_gate not in source_count_dict:
                                source_count_dict[output_gate] = 1
                            else:
                                source_count_dict[output_gate] += 1
                        else:
                            print(f"Unknown gate type: {gate_type}. Skipping.")

                capacitance_dict[output_gate] = total_capacitance

            elif in_fanin_section and line:
                parts = line.split(": ")
                if len(parts) != 2:
                    print(f"Ignoring line: {line}. Malformed input.")
                    continue
                output_gate, input_gates = parts[0], parts[1]
                input_gates = input_gates.split(", ")
                if output_gate in capacitance_dict:
                    output_capacitance = capacitance_dict[output_gate]
                    for gate in input_gates:
                        if gate.startswith("INPUT"):
                            gate_name = gate.split("-")[1]
                            source_capacitance = output_capacitance
                        else:
                            gate_type = gate.split("-")[0]
                            if gate_type in gate_input_capacitance:
                                source_capacitance = gate_input_capacitance[gate_type]
                            else:
                                print(f"Unknown gate type: {gate_type}. Skipping.")
                                continue
                        if output_gate not in fanin_count_dict:
                            fanin_count_dict[output_gate] = {}
                        fanin_count_dict[output_gate][gate] = source_capacitance

    # Update fanin capacitance for destination gates
    for dest_gate, fanin_dict in fanin_count_dict.items():
        dest_capacitance = capacitance_dict[dest_gate]
        for source_gate in fanin_dict:
            fanin_dict[source_gate] = dest_capacitance

    return capacitance_dict, source_count_dict, fanin_count_dict
    #return capacitance_dict, source_count_dict

