import sys
import os

op_codes = {
    "CA": "000000",  # add
    "KS": "000000",  # mfhi
    "AZ": "000000",  # subtract
    "CT": "000000",  # divide
    "HI": "000000",  # multiply
    "AL": "100011",  # load word
    "CO": "101011",  # store word
    "FL": "000100",  # branch on equal
    "WA": "000010",  # jump
    "UT": "000000",  # syscall
    "IA": "111111",  # load immediate
    "SD": "111110",  # load address
    "GA": "101111",  # print
    "NY": "000000",  # power
    "DE": "000000",  # sqrt
    "WY": "110010",  # rand
    "TN": "110011",  # fun fact
    "MN": "110100",  # state capital
    "MD": "110101",  # double
    "NV": "110110",  # state flower
    "NC": "110111",  # state bird
    "RI": "111100"   # state abbreviation
}

func_codes = {
    "CA": "100000",  # add
    "KS": "010000",  # mfhi
    "AZ": "100010",  # subtract
    "CT": "011010",  # divide
    "HI": "011000",  # multiply
    "UT": "001100",  # syscall
    "NY": "110000",  # power
    "DE": "110001"   # sqrt
}

registers = {
    "#nowhere": "00000",
    "#here": "00001",
    "#country0": "00010",
    "#country1": "00011",
    "#town0": "00100",
    "#town1": "00101",
    "#town2": "00110",
    "#town3": "00111",
    "#st0": "01000",
    "#st1": "01001",
    "#st2": "01010",
    "#st3": "01011",
    "#st4": "01100",
    "#st5": "01101",
    "#st6": "01110",
    "#st7": "01111",
    "#city0": "10000",
    "#city1": "10001",
    "#city2": "10010",
    "#city3": "10011",
    "#city4": "10100",
    "#city5": "10101",
    "#city6": "10110",
    "#city7": "10111",
    "#st8": "11000",
    "#st9": "11001",
    "#world0": "11010",
    "#world1": "11011",
    "#lake": "11100",
    "#mountain": "11101",
    "#river": "11110",
    "#pond": "11111"
}

def clean_instruction(line):
    # Remove comments and whitespace
    if "#" in line:
        parts = line.split("#", 1)
        if len(parts) > 1 and parts[0].strip() and parts[0][-1] != " ":
            pass  # This might be a register
        else:
            if not any(reg in line for reg in registers):
                line = parts[0]
    
    return line.strip()

def assemble(line, current_address, labels):
    if not line:
        return None
    
    parts = line.split(maxsplit=1)
    if not parts:
        return None
        
    op_code = parts[0].upper()
    operands_text = parts[1] if len(parts) > 1 else ""
    
    operand_list = []
    if operands_text:
        if op_code in ["AL", "CO"]:
            first_comma = operands_text.find(',')
            if first_comma != -1:
                rt = operands_text[:first_comma].strip()
                offset_rs = operands_text[first_comma+1:].strip()
                operand_list = [rt, offset_rs]
        else:
            operand_list = [op.strip() for op in operands_text.split(",") if op.strip()]
    
    # R-type instructions
    if op_code in func_codes:
        if op_code == "UT":  # syscall
            machine_code = op_codes[op_code] + "00000" + "00000" + "00000" + "00000" + func_codes[op_code]
            
        elif op_code == "KS":  # mfhi
            rd = operand_list[0]
            machine_code = op_codes[op_code] + "00000" + "00000" + registers[rd] + "00000" + func_codes[op_code]
            
        elif op_code in ["HI", "CT"]:  # multiply and divide
            rs, rt = operand_list[0], operand_list[1]
            machine_code = op_codes[op_code] + registers[rs] + registers[rt] + "00000" + "00000" + func_codes[op_code]
            
        elif op_code == "NY":  # power
            rs, rt = operand_list[0], operand_list[1]
            machine_code = op_codes[op_code] + registers[rs] + registers[rt] + "00000" + "00000" + func_codes[op_code]
            
        elif op_code == "DE":  # square root
            rs = operand_list[0]
            machine_code = op_codes[op_code] + registers[rs] + "00000" + "00000" + "00000" + func_codes[op_code]
            
        else:  # Regular R-type (CA, AZ)
            rd, rs, rt = operand_list[0], operand_list[1], operand_list[2]
            machine_code = op_codes[op_code] + registers[rs] + registers[rt] + registers[rd] + "00000" + func_codes[op_code]
            
    # I-type Load/Store instructions (AL, CO)
    elif op_code in ["AL", "CO"]:
        rt = operand_list[0]
        offset_rs = operand_list[1]
        
        left_paren = offset_rs.find("(")
        right_paren = offset_rs.find(")")
        
        offset = offset_rs[:left_paren] or "0"
        rs = offset_rs[left_paren+1:right_paren]
        
        offset_value = int(offset)
        if offset_value < 0:
            offset_value = offset_value & 0xFFFF
        
        offset_bin = format(offset_value, '016b')
        
        machine_code = op_codes[op_code] + registers[rs] + registers[rt] + offset_bin
        
    # Branch instruction (FL)
    elif op_code == "FL":
        rs, rt, offset_or_label = operand_list[0], operand_list[1], operand_list[2]
        
        if offset_or_label in labels:
            target_address = labels[offset_or_label] * 4
            current_pc = current_address + 4
            offset_value = (target_address - current_pc) // 4
        else:
            offset_value = int(offset_or_label) // 4
        
        if offset_value < 0:
            offset_value = offset_value & 0xFFFF
        
        offset_bin = format(offset_value, '016b')
        
        machine_code = op_codes[op_code] + registers[rs] + registers[rt] + offset_bin
        
    # Jump instruction (WA)
    elif op_code == "WA":
        target_or_label = operand_list[0]
        
        if target_or_label in labels:
            target_value = labels[target_or_label]
        else:
            target_value = int(target_or_label)
        
        target_bin = format(target_value, '026b')
        
        machine_code = op_codes[op_code] + target_bin
        
    # Load immediate (IA)
    elif op_code == "IA":
        rt, immediate = operand_list[0], operand_list[1]
        
        immediate_value = int(immediate)
        if immediate_value < 0:
            immediate_value = immediate_value & 0xFFFF
        
        immediate_bin = format(immediate_value, '016b')
        
        machine_code = op_codes[op_code] + "00000" + registers[rt] + immediate_bin
        
    # Load address (SD)
    elif op_code == "SD":
        rt, address_or_label = operand_list[0], operand_list[1]
        
        if address_or_label in labels:
            address_value = labels[address_or_label]
        else:
            address_value = int(address_or_label)
        
        address_bin = format(address_value, '016b')
        
        machine_code = op_codes[op_code] + "00000" + registers[rt] + address_bin
    
    # Single-register instructions
    elif op_code in ["GA", "WY", "TN", "MN", "NV", "NC", "RI"]:
        rt = operand_list[0]
        machine_code = op_codes[op_code] + "00000" + registers[rt] + "0000000000000000"
    
    # Double register instruction (MD)
    elif op_code == "MD":
        rs, rt = operand_list[0], operand_list[1]
        machine_code = op_codes[op_code] + registers[rs] + registers[rt] + "0000000000000000"
    
    return machine_code

def interpret_file(mips_file, output_file="program1.bin"):
    # First pass: collect labels
    labels = {}
    instruction_count = 0
    
    with open(mips_file, "r") as input_file:
        for line in input_file:
            line = clean_instruction(line)
            if not line:
                continue
                
            if ":" in line:
                label_parts = line.split(":", 1)
                label = label_parts[0].strip()
                labels[label] = instruction_count
                
                remaining = label_parts[1].strip()
                if remaining:
                    instruction_count += 1
            else:
                instruction_count += 1
    
    # Second pass: assemble
    with open(mips_file, "r") as input_file:
        with open(output_file, "w") as out_file:
            address = 0
            for line in input_file:
                clean_line = clean_instruction(line)
                if not clean_line:
                    continue
                
                if ":" in clean_line:
                    label_parts = clean_line.split(":", 1)
                    instruction = label_parts[1].strip()
                    if not instruction:
                        continue
                else:
                    instruction = clean_line
                
                bin_instruction = assemble(instruction, address, labels)
                if bin_instruction:
                    out_file.write(bin_instruction + "\n")
                    address += 4

def main():
    if len(sys.argv) > 1:
        mips_file = sys.argv[1]
        output_file = "program1.bin"
        if len(sys.argv) > 2:
            output_file = sys.argv[2]
    else:
        mips_file = "program1.mips"
        output_file = "program1.bin"
    
    interpret_file(mips_file, output_file)
    print(f"Assembly completed. Output written to '{output_file}'.")

if __name__ == "__main__":
    main()