import sys
import os

# Reverse dictionaries from the assembler to look up operations and registers
op_codes_rev = {
    "000000": {
        "100000": "CA",  # add
        "010000": "KS",  # mfhi
        "100010": "AZ",  # subtract
        "011010": "CT",  # divide
        "011000": "HI",  # multiply
        "001100": "UT",  # syscall
        "110000": "NY",  # power
        "110001": "DE"   # sqrt
    },
    "100011": "AL",  # load word
    "101011": "CO",  # store word
    "000100": "FL",  # branch on equal
    "000010": "WA",  # jump
    "111111": "IA",  # load immediate
    "111110": "SD",  # load address
    "101111": "GA",  # print
    "110010": "WY",  # rand
    "110011": "TN",  # fun fact
    "110100": "MN",  # state capital
    "110101": "MD",  # double
    "110110": "NV",  # state flower
    "110111": "NC",  # state bird
    "111100": "RI"   # state abbreviation
}

registers_rev = {
    "00000": "#nowhere",
    "00001": "#here",
    "00010": "#country0",
    "00011": "#country1",
    "00100": "#town0",
    "00101": "#town1",
    "00110": "#town2",
    "00111": "#town3",
    "01000": "#st0",
    "01001": "#st1",
    "01010": "#st2",
    "01011": "#st3",
    "01100": "#st4",
    "01101": "#st5",
    "01110": "#st6",
    "01111": "#st7",
    "10000": "#city0",
    "10001": "#city1",
    "10010": "#city2",
    "10011": "#city3",
    "10100": "#city4",
    "10101": "#city5",
    "10110": "#city6",
    "10111": "#city7",
    "11000": "#st8",
    "11001": "#st9",
    "11010": "#world0",
    "11011": "#world1",
    "11100": "#lake",
    "11101": "#mountain",
    "11110": "#river",
    "11111": "#pond"
}

def disassemble_file(binary_file, output_file=None):
    disassembled_instructions = []
    
    # Read binary instructions from the file
    with open(binary_file, "r") as input_file:
        binary_lines = [line.strip() for line in input_file if line.strip()]
    
    # Process each binary instruction
    for line_num, binary in enumerate(binary_lines, 0):
        try:
            # Skip empty lines
            if not binary:
                continue
                
            # Disassemble the instruction
            instruction = disassemble_instruction(binary, line_num)
            disassembled_instructions.append((binary, instruction))
            
        except Exception as e:
            print(f"Error disassembling line {line_num}: {binary}")
            print(f"  {str(e)}")
            
    # Write disassembled instructions to output file if specified
    if output_file:
        with open(output_file, "w") as out_file:
            for _, instruction in disassembled_instructions:
                out_file.write(instruction + "\n")
                
    return disassembled_instructions

def disassemble_instruction(binary, address=0):
    if len(binary) != 32:
        raise ValueError(f"Invalid binary instruction length: {len(binary)}. Expected 32 bits.")
    
    # Extract operation code (first 6 bits)
    op_code_bin = binary[:6]
    
    # Process R-type instructions (func_code needed)
    if op_code_bin == "000000":
        # Extract function code (last 6 bits)
        func_code = binary[26:32]
        
        if func_code not in op_codes_rev["000000"]:
            raise ValueError(f"Unknown function code: {func_code}")
            
        op = op_codes_rev["000000"][func_code]
        
        # Extract register fields
        rs = binary[6:11]
        rt = binary[11:16]
        rd = binary[16:21]
        shamt = binary[21:26]
        
        # Special case for syscall (UT)
        if op == "UT":
            return "UT"
            
        # Special case for mfhi (KS)
        elif op == "KS":
            if rd not in registers_rev:
                raise ValueError(f"Invalid rd register: {rd}")
            return f"KS {registers_rev[rd]}"
            
        # Multiply and Divide (HI, CT)
        elif op in ["HI", "CT"]:
            if rs not in registers_rev or rt not in registers_rev:
                raise ValueError(f"Invalid register(s): rs={rs}, rt={rt}")
            return f"{op} {registers_rev[rs]}, {registers_rev[rt]}"
            
        # Special case for power (NY)
        elif op == "NY":
            if rs not in registers_rev or rt not in registers_rev:
                raise ValueError(f"Invalid register(s): rs={rs}, rt={rt}")
            return f"{op} {registers_rev[rs]}, {registers_rev[rt]}"
            
        # Special case for square root (DE)
        elif op == "DE":
            if rs not in registers_rev:
                raise ValueError(f"Invalid rs register: {rs}")
            return f"{op} {registers_rev[rs]}"
            
        # Regular R-type (CA, AZ)
        else:
            if rd not in registers_rev or rs not in registers_rev or rt not in registers_rev:
                raise ValueError(f"Invalid register(s): rd={rd}, rs={rs}, rt={rt}")
            return f"{op} {registers_rev[rd]}, {registers_rev[rs]}, {registers_rev[rt]}"
    
    # Process other instruction types
    elif op_code_bin in op_codes_rev:
        op = op_codes_rev[op_code_bin]
        
        # Extract register fields and immediate value
        rs = binary[6:11]
        rt = binary[11:16]
        immediate = binary[16:32]
        
        # I-type Load/Store instructions (AL, CO)
        if op in ["AL", "CO"]:
            if rs not in registers_rev or rt not in registers_rev:
                raise ValueError(f"Invalid register(s): rs={rs}, rt={rt}")
            imm_value = int(immediate, 2)
            if imm_value > 32767:
                imm_value -= 65536
                
            return f"{op} {registers_rev[rt]}, {imm_value}({registers_rev[rs]})"
            
        # Branch instruction (FL)
        elif op == "FL":
            if rs not in registers_rev or rt not in registers_rev:
                raise ValueError(f"Invalid register(s): rs={rs}, rt={rt}")
            imm_value = int(immediate, 2)
            if imm_value > 32767:
                imm_value -= 65536
            target_address = (address + 1) * 4 + (imm_value * 4)
            
            return f"{op} {registers_rev[rs]}, {registers_rev[rt]}, {imm_value}"
            
        # Jump instruction (WA)
        elif op == "WA":
            # Convert target address to decimal
            target_value = int(binary[6:32], 2)
            
            return f"{op} {target_value}"
            
        # Load immediate (IA)
        elif op == "IA":
            if rt not in registers_rev:
                raise ValueError(f"Invalid rt register: {rt}")
                
            # Convert immediate to decimal (can be signed or unsigned)
            imm_value = int(immediate, 2)
            if imm_value > 32767:
                imm_value -= 65536
                
            return f"{op} {registers_rev[rt]}, {imm_value}"
            
        # Load address (SD)
        elif op == "SD":
            if rt not in registers_rev:
                raise ValueError(f"Invalid rt register: {rt}")
                
            # Convert address to decimal (unsigned)
            addr_value = int(immediate, 2)
                
            return f"{op} {registers_rev[rt]}, {addr_value}"
            
        # Print instruction (GA)
        elif op == "GA":
            if rt not in registers_rev:
                raise ValueError(f"Invalid rt register: {rt}")
                
            return f"{op} {registers_rev[rt]}"
            
        # Instructions with one register operand (WY, TN, MN, NV, NC, RI)
        elif op in ["WY", "TN", "MN", "NV", "NC", "RI"]:
            if rt not in registers_rev:
                raise ValueError(f"Invalid rt register: {rt}")
                
            return f"{op} {registers_rev[rt]}"
            
        # Double instruction (MD)
        elif op == "MD":
            if rs not in registers_rev or rt not in registers_rev:
                raise ValueError(f"Invalid register(s): rs={rs}, rt={rt}")
                
            return f"{op} {registers_rev[rs]}, {registers_rev[rt]}"
            
        else:
            raise ValueError(f"Unimplemented operation code: {op}")
    else:
        raise ValueError(f"Unknown operation code: {op_code_bin}")

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) > 1:
        binary_file = sys.argv[1]
        output_file = None
        if len(sys.argv) > 2:
            output_file = sys.argv[2]
    else:
        binary_file = "program1.bin"
        output_file = "program1_disassembled.mips"
    
    if not os.path.exists(binary_file):
        print(f"Error: Input file '{binary_file}' not found.")
        return
    
    # Run the disassembler and get the disassembled instructions
    disassembled_instructions = disassemble_file(binary_file, output_file)
    
    if output_file:
        print(f"Disassembly completed. Output written to '{output_file}'.")
    
    # Print the disassembled instructions
    print("\nDisassembled Instructions:")
    for binary, instruction in disassembled_instructions:
        print(f"{binary} => {instruction}")

if __name__ == "__main__":
    main()
