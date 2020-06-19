"""CPU functionality."""

import sys

LDI = 0b10000010
HLT = 0b00000001
PRN = 0b01000111
NOP = 0b00000000
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
SP = 0b00000111
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE =  0b01010110

class CPU:
    """Main CPU class."""
    # Initialize
    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.reg[SP] = 0xF4
        self.pc = 0
        self.ram = [0] * 256
        self.equal = 0
        self.running = True
        self.branch_table = {
            NOP : self.NOP,
            HLT : self.HLT,
            PRN : self.PRN,
            LDI : self.LDI,
            ADD : self.ADD,
            MUL : self.MUL,
            PUSH: self.PUSH,
            POP : self.POP,
            CALL : self.CALL,
            RET : self.RET,
            CMP : self.CMP,
            JMP : self.JMP,
            JEQ : self.JEQ,
            JNE : self.JNE
        }

    # Load the program
    def load(self):
        """Load a program into memory."""
        file = sys.argv[1]

        with open(file) as f:
            for address, line in enumerate(f):
                line = line.split("#")
                try:
                    v = int(line[0], 2)
                except ValueError:
                    continue
                self.ram_write(address, v)

    # Run the cpu
    def run(self):
        """Run the CPU."""
        while self.running:
            ir = self.ram_read(self.pc)
            self.call_function(ir)

    # Read ram
    def ram_read(self, address):
        return self.ram[address]
    # Write to ram
    def ram_write(self, address, value):
        self.ram[address] = value

    # Call our functions
    def call_function(self, n):
        f = self.branch_table[n]
        if self.branch_table.get(n) is not None:
            f()
        else:
            print(f'No instruction {ir} at address {self.pc}')
            self.HLT()

    # Arithmatic operations handler
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.equal = 1
            else:
                self.equal = 0
        else:
            raise Exception("Unsupported ALU operation")
    
    #### Begin operations available to emulator ####
    ## set register
    def LDI(self):
        reg_num = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        self.reg[reg_num] = value
        self.pc += 3

    ## stop
    def HLT(self):
        self.running = False
    ## no operation
    def NOP(self):
        self.pc += 1
    ## print
    def PRN(self):
        reg_num = self.ram_read(self.pc + 1)
        print(self.reg[reg_num])
        self.pc += 2

    ### Arithmatic Operations ###
    ## add
    def ADD(self):
        reg_num1 = self.ram_read(self.pc + 1)
        reg_num2 = self.ram_read(self.pc + 2)
        self.alu("ADD", reg_num1, reg_num2)
        self.pc += 3
    ## multiply
    def MUL(self):
        reg_num1 = self.ram_read(self.pc + 1)
        reg_num2 = self.ram_read(self.pc + 2)
        self.alu("MUL", reg_num1, reg_num2)
        self.pc += 3
    ## compare SPRINT
    def CMP(self):
        reg_num1 = self.ram_read(self.pc + 1)
        reg_num2 = self.ram_read(self.pc + 2)
        self.alu("CMP", reg_num1, reg_num2)
        self.pc += 3

    ### End Arithmatic ###

    ### Stack Operations ###
    def PUSH(self):
        reg_num = self.ram[self.pc + 1]
        value = self.reg[reg_num]
        self.reg[SP] -= 1
        tos = self.reg[SP]
        self.ram[tos] = value
        self.pc += 2

    def POP(self):
        tos = self.reg[SP]
        value = self.ram[tos]
        reg_num = self.ram[self.pc + 1]
        self.reg[reg_num] = value
        self.reg[SP] += 1
        self.pc += 2
    
    ### End stack operations ###
    
    ### Subroutine operations ###
    def CALL(self):
        return_address = self.pc + 2
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = return_address

        register_num = self.ram[self.pc + 1]
        subroutine_address = self.reg[register_num]

        self.pc = subroutine_address
    
    def RET(self):
        subroutine_address = self.ram[self.reg[SP]]
        self.reg[SP] += 1
        self.pc = subroutine_address
    
    ### End Subroutine operations ###

    ### Jump operations SPRINT ###
    # Jump to address
    def JMP(self):
        self.pc = self.reg[self.ram[self.pc+1]]
    
    # Jump to address if equal flag is true
    def JEQ(self):
        if self.equal == 1:
            self.pc = self.reg[self.ram[self.pc + 1]]
        else:
            self.pc += 2

    # Jump to address if equal flag is false
    def JNE(self):
        if self.equal == 0:
            self.pc = self.reg[self.ram[self.pc + 1]]
        else:
            self.pc += 2

    ### End jump operations ###

    ### End operations ###

    def trace(self):
            """
            Handy function to print out the CPU state. You might want to call this
            from run() if you need help debugging.
            """

            print(f"TRACE: %02X | %02X %02X %02X |" % (
                self.pc,
                #self.fl,
                #self.ie,
                self.ram_read(self.pc),
                self.ram_read(self.pc + 1),
                self.ram_read(self.pc + 2)
            ), end='')

            for i in range(8):
                print(" %02X" % self.reg[i], end='')

            print()