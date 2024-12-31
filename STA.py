class STA:
    def __init__(self, input_gate_name, gate_name, ai, ti, cl, di, tdi,rat,slack):
        self.input_gate_name = input_gate_name
        self.gate_name = gate_name
        self.ai = ai
        self.ti = ti
        self.cl = cl
        self.di = di
        self.tdi = tdi
        self.rat = rat
        self.slack = slack

    def __str__(self):
        return f"STA(input_gate_name={self.input_gate_name}, gate_name={self.gate_name}, ai={self.ai}, ti={self.ti}, cl={self.cl}, di={self.di}, tdi={self.tdi}), rat={self.rat})"
