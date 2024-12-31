import argparse
import re

from gate_type import Gate
from LUT import LUT

def read_bench_file(file_path):
    inputs = []
    outputs = []
    gates = []
    gateMap = {}
    outputGateTypes ={}
    gateCount = {}

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('#') or line == '':
                continue  # Skip comments and empty lines
            elif line.startswith('INPUT'):
                inputs.append(line.split('(')[1].split(')')[0])
            elif line.startswith('OUTPUT'):
                outputs.append(line.split('(')[1].split(')')[0])
            else:
                parts = line.split("=")
                output = parts[0].strip()
                # Output value
                gateInputs = parts[1].split("(")[1].split(")")[0].split(", ")  # Input values
                gateType = parts[1].split('(')[0].strip()
                gate = Gate(gateType, output, gateInputs)
                if gateType in gateCount:
                    count = gateCount[gateType]
                    gateCount[gateType] = count+1
                else:
                    gateCount[gateType] = 1
                gates.append(gate)
                print(gate.gateType,gate.output, gate.inputs)


                for input in gateInputs:
                    if input in gateMap:
                        input_value = gateMap[input]

                        input_value.append({gateType:output})
                    else:
                        listOutput = []
                        listOutput.append({gateType:output})
                        gateMap[input] = listOutput
                outputGateTypes[output] = gateType

    #print("**************************************")
    #print(outputs)
    return inputs, outputs, gates,gateMap,outputGateTypes,gateCount

def read_ckt(file_path):
    inputs, outputs, gates,gateMap,outputGateTypes,gateCount = read_bench_file(file_path)

    print("Inputs:", inputs)
    print("gateMap:", gateMap)
    count =1
    for gate in gates:
         print(count)
         print(gate.gateType)
         print(gate.output)
         print(gate.inputs)
         print(" ")
         count=count+1

   
    print("outputGateTypes:",outputGateTypes)

    line1 = str(len(inputs)) + "  primary inputs"
    line2 = str(len(outputs)) + "  primary outputs"
    line3 = ""
    for key in gateCount:
        line3+= str(gateCount[key])+ " "+ key +" Gates\n"


    line4 = "Fanout..."

    line5 =""
    line6 = "Fanin..."
    line7 = ""

    for gate in gates:
        #print("...............")
        #print(gate.output)
        output = str(gate.output)
        #print(gateMap[output])
        if output in gateMap:
            line5+= gate.gateType+"-"+str(output)+": "
            for out in gateMap[output]:
                gateType = list(out.keys())[0]
                value = out.get(gateType)
                line5+=gateType+"-"+str(value)+", "
            if output in outputs:
                line5+="OUTPUT-"+ str(output)
            if line5.endswith(", "):
                line5 = line5[:-2]
            line5+="\n"
        elif gate.output in outputs:
            #print("********")
            output = gate.output
            #print(output)
            line5+=gate.gateType+"-"+ str(output) +": OUTPUT-"+ str(output) + "\n"

        line7+=gate.gateType+"-"+str(output)+": "

        for input in gate.inputs:
            if input in inputs:
                line7+="INPUT-"+str(input)+", "
            elif input in outputGateTypes:
                line7+=outputGateTypes[input]+"-"+ str(input)+", "
        if line7.endswith(", "):
            line7 = line7[:-2]
        line7 += "\n"




    lines = [line1+"\n", line2+"\n",line3+"\n",line4+"\n",line5+"\n",line6+"\n",line7+"\n"]

    with open('ckt_details.txt', 'w') as file:
        file.writelines(lines)

def generate_delay_UT(file_path):
    cell_name = None
    input_slews = None
    load_cap = None
    delays = []
    lut_list = []

    isCellDelayFlag = False
    isCellDelayValueFlag = False

    with open(file_path, 'r') as f:
        for line in f:
            # Extracting cell name

            cell_name_match = re.match(r'.*cell \((.*?)\)', line)

            if cell_name_match:
                cell_name = cell_name_match.group(1)
                continue

            # Extracting input slews
            cell_delay_match = re.match(r'\s*cell_delay', line)
            if cell_delay_match:
                isCellDelayFlag = True
                continue

            input_slews_match = re.match(r'\s*index_1 \((.*?)\)', line)

            if input_slews_match and isCellDelayFlag:
                input_str = input_slews_match.group(1)
                input_str = input_str.replace('"', '')
                input_slews = input_str.split(',')
                continue

            # Extracting load cap
            load_cap_match = re.match(r'\s*index_2 \((.*?)\)', line)
            if load_cap_match and isCellDelayFlag:
                load_str = load_cap_match.group(1)
                load_str = load_str.replace('"', '')
                load_cap = load_str.split(',')

                continue
            cell_delay_closing_bracket = re.match(r'\s*}',line)
            if isCellDelayFlag and cell_delay_closing_bracket:
                isCellDelayFlag = False
                lut = LUT(cell_name,input_slews,load_cap,delays)
                lut_list.append(lut)
                cell_name = None
                input_slews = None
                load_cap = None
                delays = []
                continue
            # Extracting delays

            delays_match = re.match(r'\s*values \("(.*?)"', line)
            if delays_match and isCellDelayFlag:

                isCellDelayValueFlag = True
                delays.extend(delays_match.group(1).split(','))
                continue

            if isCellDelayFlag and isCellDelayValueFlag and not delays_match:

                line = line.strip()
                line = line.rstrip('\\').rstrip()
                line = line.replace("","")
                line = line.rstrip('')
                line = line.rstrip('");')
                line = line.rstrip('",')
                value_delays = line.strip('"').split(',')
                value_delays = [x for x in value_delays if x]
                delays += value_delays
                continue

            closing_bracket_delays_match = re.search(r'\);', line)
            if isCellDelayValueFlag and closing_bracket_delays_match:
                isCellDelayValueFlag = False
                continue


    writeToDelay_LUT(lut_list,'delay_LUT.txt','delays')


    return lut

def writeToDelay_LUT(lut_list,file_name,input):
    lines =[]
    count=0
    for lut in lut_list:
        line1 = "cell:"+lut.cellName+ "\n"
        lines.append(line1)
        line2 = "input slews: "
        for input_slew in lut.inputSlews:
            line2+=input_slew+","
        line2=line2[:-1]
        line2+="\n"
        lines.append(line2)
        line3 ="load cap: "
        for load in lut.loadCap:
            line3 += load + ","
        line3=line3[:-1]
        line3+= "\n"
        lines.append(line3)
        line4 = input+":\n"
        for delay in lut.delays:
            line4+=delay +","
            count+=1
            if count==7:
                line4 = line4[:-1] + ';'
                count=0
                line4+="\n"

        line4+="\n\n\n\n"
        lines.append(line4)

    with open(file_name, 'w') as file:
        file.writelines(lines)

def generate_slew_LUT(file_path):
    cell_name = None
    input_slews = None
    load_cap = None
    input_cap = None
    delays = []
    lut_list = []

    isCellDelayFlag = False
    isCellDelayValueFlag = False

    with open(file_path, 'r') as f:
        for line in f:
            # Extracting cell name
            cell_name_match = re.match(r'.*cell \((.*?)\)', line)
            if cell_name_match:
                cell_name = cell_name_match.group(1)
                continue
            # Extracting input slews
            cell_delay_match = re.match(r'\s*output_slew', line)
            if cell_delay_match:
                isCellDelayFlag = True
                continue

            input_slews_match = re.match(r'\s*index_1 \((.*?)\)', line)

            if input_slews_match and isCellDelayFlag:
                input_str = input_slews_match.group(1)
                input_str = input_str.replace('"', '')
                input_slews = input_str.split(',')
                continue
            # Extracting load cap
            load_cap_match = re.match(r'\s*index_2 \((.*?)\)', line)
            if load_cap_match and isCellDelayFlag:
                load_str = load_cap_match.group(1)
                load_str = load_str.replace('"', '')
                load_cap = load_str.split(',')
                continue
            cell_delay_closing_bracket = re.match(r'\s*}', line)
            if isCellDelayFlag and cell_delay_closing_bracket:
                isCellDelayFlag = False
                lut = LUT(cell_name, input_slews, load_cap, delays)
                lut_list.append(lut)
                cell_name = None
                input_slews = None
                load_cap = None
                delays = []
                continue
            # Extracting delays

            delays_match = re.match(r'\s*values \("(.*?)"', line)
            if delays_match and isCellDelayFlag:
                isCellDelayValueFlag = True
                delays.extend(delays_match.group(1).split(','))
                continue

            if isCellDelayFlag and isCellDelayValueFlag and not delays_match:
                # print(line)
                line = line.strip()
                line = line.rstrip('\\').rstrip()
                line = line.replace("", "")
                line = line.rstrip('')
                line = line.rstrip('");')
                line = line.rstrip('",')
                value_delays = line.strip('"').split(',')
                value_delays = [x for x in value_delays if x]
                delays += value_delays
                continue

            closing_bracket_delays_match = re.search(r'\);', line)
            if isCellDelayValueFlag and closing_bracket_delays_match:
                isCellDelayValueFlag = False
                continue


    writeToDelay_LUT(lut_list,'slew_LUT.txt','slews')

    return lut
def main():
    parser = argparse.ArgumentParser(description="Bench file parser")
    parser.add_argument("--delays",action='store_true', required=False)
    parser.add_argument("--slews", action='store_true', required=False)
    parser.add_argument("--read_nldm", type=str, required=False)
    parser.add_argument("--read_ckt", type=str, required=False)


    args = parser.parse_args()


    if args.read_ckt:
        read_ckt(args.read_ckt)
    elif args.delays:
        generate_delay_UT(args.read_nldm)
    elif args.slews:
        generate_slew_LUT(args.read_nldm)
    else:
        print("Invalid action.")

if __name__ == "__main__":
    main()
