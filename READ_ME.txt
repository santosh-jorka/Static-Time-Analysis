EDA Project-1 Phase_2
Team name:Transistor Trendsetters

Libraries usedin the code:
argparse
re

Python 	Files Written for Project-1
1.sta_parser.py     : Implemented Phase_1 code for parsing data from bench file of the command. It also creates delay_LUT and slew_LUT files. 
2.traversal.py     : Written code for Forward & Backward traversal. 
3.capacitance.py   : Written logic for each gate Capacitance
4.delay.py      : Written Method for delay
5.LUT.py        : Written method to parse the LUT data from sample_NLDM.lib file for each gates.
6.gate_type.py   : Created gate class for gate types
7.STA.py           : Written method and storing data for STA analysis
8.di_tdi_values.py : This code calculates the di,tdi values of each gate.


Commands being used for the File Creation

1. python3.7 parser_sta.py --read_ckt c17.bench                            : Creating ckt_details.txt file with gates(Primary inputs, Primary Outputs, Gate types, fanin , Fanout) data
2. python3.7 parser_sta.py --dealys --read_nldm sample_NLDM.lib            : Creating delays_LUT.txt file 
3. python3.7 parser_sta.py --slews  --read_nldm sample_NLDM.lib            : Creating slews_LUT.txt file
4. python3.7 main_sta.py --read_ckt c17.bench --read_nldm sample_NLDM.lib  : Creating ckt_traversal.txt file with data of Crtical delay, Gate Slacks, Crtical Path.

