"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JEQ = 0b01010101
JNE = 0b01010110
JMP = 0b01010100

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0]*256
        self.reg = [0]*8
        self.pc = 0
        self.inst_reg = list()
        self.fl = [0]*8 # flags register

        # Initialize stack pointer
        self.reg[7] = 0xF4

    def load(self):

        # Address location in RAM
        address = 0

        # If length of args is less than 2 then return print statement
        if len(sys.argv) < 2:
            print(f"Please enter an additional argument\nCurrent Args: {sys.argv[0]}")
        
        # Open file and filter out lack and commented lines
        else:
            with open(sys.argv[1], "r") as f:
                for x in f:
                    # Skip the line if it starts with "#" or length of stripped line == 0
                    if x[0] == "#" or len(x.rstrip()) == 0:
                        continue

                    # Add line to RAM at current address
                    else:
                        val = bin(int(x.split()[0], 2))
                        # Save to ram and increment address
                        self.ram[address] = val
                        address+=1
            f.close()

    def ram_read(self, address):
        # Return the value stored at the address
        return self.ram[address]

    def ram_write(self, address, value):
        # Write the value to the inputted address
        for x in range(len(self.ram)):
            if self.ram[x] == address:
                self.ram[x] = value
                print(f"Value: {value}\nSaved at {address} in ram")

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            # Add
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "MUL": 
            # Multiply
            self.reg[reg_a] *= self.reg[reg_b]
        
        elif op == "CMP":
            # Create temp variables and compare values
            val1 = self.reg[reg_a]
            val2 = self.reg[reg_b]

            # Equal check
            if val1 == val2:
                self.fl[0] = 1
            else:
                self.fl[0] = 0

            # Greater than check
            if  val1 > val2:
                self.fl[1] = 1
            else:
                self.fl[1] = 0

            # Less than check
            if val1 < val2:
                self.fl[2] = 1
            else:
                self.fl[2] = 0

        else:
            raise Exception("Unsupported ALU operation")

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

    def use_LDI(self):
        # register address location
        opperand_a = int(self.ram[self.pc+1], 2)

        # value to be saved
        opperand_b = int(self.ram[self.pc+2], 2)

        # Assign value to address in register
        self.reg[opperand_a] = opperand_b

        # store result in instruction register
        self.inst_reg.append(opperand_b)

        # Increment pc by 3
        self.pc+=3

    def use_PRN(self):
        # Store idx location
        reg_idx = int(self.ram[self.pc+1], 2)

        #print the value
        print(self.reg[reg_idx])

        # append the result to instruction register
        self.inst_reg.append(self.reg[reg_idx])

        # Increment pc by 2
        self.pc+=2
    
    def use_MUL(self):
        # Find index location of numbers to be multiplied
        reg1 = int(self.ram[self.pc+1],2)
        reg2 = int(self.ram[self.pc+2],2)

        # Pass into alu for processing
        self.alu("MUL", reg1, reg2)

        # Increment pc by 3
        self.pc+=3
    
    def use_ADD(self):
        # Find index location of numbers to be multiplied
        reg1 = int(self.ram[self.pc+1],2)
        reg2 = int(self.ram[self.pc+2], 2)

        # Pass into alu for processing
        self.alu("ADD", reg1, reg2)

        # Increment pc by 3
        self.pc+=3

    def use_PUSH(self):
        # decrement the stakc pointer
        self.reg[7] -= 1

        # find index and save vale into the register
        reg_idx = int(self.ram[self.pc +1],2)
        value = self.reg[reg_idx]

        # Copy value to the correct address
        SP = self.reg[7]
        self.ram[SP] = value

        self.pc+=2

    def use_POP(self):
        # stack ponter location
        SP = self.reg[7]

        # find value of SP in ram
        value = self.ram[SP]

        # find the index value where the vale should be saved
        reg_idx = int(self.ram[self.pc+1], 2)

        # Save value to the register
        self.reg[reg_idx] = value

        # Increment the stack index
        self.reg[7] +=1

        # Increment pc
        self.pc+=2

    def use_CALL(self):
        # Save program location
        return_address = self.pc+2

        # Decrement register
        self.reg[7] -= 1

        # Stack pointer
        SP = self.reg[7]

        self.ram[SP] = return_address

        reg_idx = self.ram[self.pc + 1]

        subroutine_address = self.reg[int(reg_idx, 2)]

        self.pc = subroutine_address

    def use_RET(self):

        #stack pointer
        SP = self.reg[7]

        return_address = self.ram[SP]

        self.pc = return_address

        self.reg[7] += 1
    
    def use_JMP(self, reg_idx):
        "Set pc to the address to jump too"
        self.pc = reg_idx

    def use_CMP(self):
        "Compare the two values and adjust flags"
        reg1 = int(self.ram[self.pc+1],2)
        reg2 = int(self.ram[self.pc+2],2)

        # Pass into alu for processing
        self.alu("CMP", reg1, reg2)

        # Increment pc by 3
        self.pc+=3
    
    def use_JEQ(self):
        "If equal jump to address else increment pc"
        if self.fl[0] == 1:
            self.use_JMP(self.reg[int(self.ram_read(self.pc+1),2)])
        else:
            self.pc += 2
    
    def use_JNE(self):
        "If not equal then jump to address, else increment pc"
        if self.fl[0] == 0:
            self.use_JMP(self.reg[int(self.ram_read(self.pc+1),2)])
        else:
            self.pc+=2

    def run(self):
        """Run the CPU."""

        while self.ram[self.pc] != 0:

            # Internal register
            ir = int(self.ram_read(self.pc), 2)

            # If ram_read returns the LDI command then save the results to the appropriate register
            if ir == LDI:
                self.use_LDI()
            
            # print the value
            elif ir == PRN:
                self.use_PRN()
            
            # Multiply 
            elif ir == MUL:
                self.use_MUL()
            
            # Add
            elif ir == ADD:
                self.use_ADD()
           
           # Push to stack
            elif ir == PUSH:
                self.use_PUSH()

            # Pop off stack  
            elif ir == POP:
                self.use_POP()

            # Call
            elif ir == CALL:
                self.use_CALL()

            # Return
            elif ir == RET:
                self.use_RET()

            # Compare the two values
            elif ir == CMP:
                self.use_CMP()

            # CHeck if Equal
            elif ir == JEQ:
                self.use_JEQ()

            # Check is not equal
            elif ir == JNE:
                self.use_JNE()

            # Jump to address
            elif ir == JMP:
                self.use_JMP(self.reg[int(self.ram_read(self.pc+1),2)])

            # Exit the program if HLT byte code appears
            elif ir == HLT:
                break
