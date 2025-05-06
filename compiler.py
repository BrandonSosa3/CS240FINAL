memoryAddress = 5000
tRegister = 0
vars = dict()
ifStatement1 = 0
ifStatement2 = 3
ifElseSet = -1
elseBracket = False
innerIfStatement = False
aRegister = 0
textNum = 0

def getInstructionLine(varName):
    global memoryAddress, tRegister
    tRegisterName = f"#st{tRegister}"
    setVariableRegister(varName, tRegisterName)
    returnText = f"IA {tRegisterName}, {memoryAddress}"
    tRegister += 1
    memoryAddress += 4
    return returnText

def setVariableRegister(varName, tRegister):
    global vars
    vars[varName] = tRegister

def getVariableRegister(varName):
    global vars
    if varName in vars:
        return vars[varName]
    else:
        return "ERROR"

def getAssignmentLinesImmediateValue(val, varName):
    global tRegister
    outputText = f"""IA #st{tRegister}, {val}
CO #st{tRegister}, 0({getVariableRegister(varName)})"""
    tRegister += 1
    return outputText


def getAssignmentLinesVariable(varSource, varDest):
    global tRegister
    outputText = ""
    registerSource = getVariableRegister(varSource)
    outputText += f"AL #st{tRegister}, 0({registerSource})" + "\n"

    tRegister += 1

    registerDest = getVariableRegister(varDest)

    outputText += f"CO #st{tRegister-1}, 0({registerDest})"
    # tRegister += 1
    return outputText

def getIfStatement(expr):
    global vars
    global ifStatement1
    global ifStatement2
    global innerIfStatement
    global ifElseSet
    global tRegister
    ifElseSet += 1
    var1, _, var2 = expr.split()
    reg1 = vars.get(var1)
    reg2 = vars.get(var2)
    tReg1 = f"#st{tRegister}"
    tRegister += 1
    tReg2 = f"#st{tRegister}"
    tRegister += 1
    outputText = f"AL {tReg1}, 0({reg1})\nAL {tReg2}, 0({reg2})\n"
    if not innerIfStatement:
        ifStatement1 += 1
        outputText += f"FL {tReg1}, {tReg2}, TRUE{ifStatement1}\nWA AFTER{ifStatement1}\nTRUE{ifStatement1}:"
        innerIfStatement = True
    else:
        ifStatement2 += 1
        outputText += f"FL {tReg1}, {tReg2}, TRUE{ifStatement2}\nWA AFTER{ifStatement2}\nTRUE{ifStatement2}:"
    return outputText

def getLoop(expr):
    global tRegister
    var1, _, var2 = expr.split()
    reg1 = vars.get(var1)
    reg2 = vars.get(var2)
    tReg1 = f"#st{tRegister}"
    tRegister += 1
    tReg2 = f"#st{tRegister}"
    tRegister += 1
    outputText = (f"LOOP:\nAL {tReg1}, 0({reg1})\nAL {tReg2}, 0({reg2})\n"
                  f"FL {tReg1}, {tReg2}, FINISH")
    return outputText


def getElseIfStatement(expr):
    global vars
    global innerIfStatement
    global ifStatement1
    global tRegister
    ifStatement1 += 1
    var1, _, var2 = expr.split()
    reg1 = vars.get(var1)
    reg2 = vars.get(var2)
    tReg1 = f"#st{tRegister}"
    tRegister += 1
    tReg2 = f"#st{tRegister}"
    tRegister += 1
    outputText = (f"AL {tReg1}, 0({reg1})\nAL {tReg2}, 0({reg2})\n"
                  f"FL {tReg1}, {tReg2}, AFTER{ifStatement1}\nWA AFTER{ifStatement1}\nTRUE{ifStatement1}:")
    return outputText

def getEndBracket():
    global elseBracket
    global innerIfStatement
    global ifStatement1
    global ifStatement2
    global ifElseSet
    if ifElseSet == -1:
        return ""
    if elseBracket:
        outputText = f"ENDIF{ifElseSet}"
        ifElseSet -= 1
        elseBracket = False
    else:
        if innerIfStatement:
            outputText = f"WA ENDIF1:\nAFTER{ifStatement2}:"
        else:
            outputText = f"WA ENDIF0:\nAFTER{ifStatement1}:"
    return outputText

f = open(".venv/fizzbuzz.c", "r")

lines = f.readlines()

outputText = ".text\n"

for line in lines:
    if tRegister > 8:
        tRegister = len(vars)
    if line.startswith("while "):
        _, expr = line.split("while ")
        expr = expr.replace("(", "").replace(")", "").replace("{", "")
        outputText += getLoop(expr) + "\n"
    elif "+" in line:
        outputText += "FIX ADD\n"
        destVar, _, addVar, _, addNum = line.split()
        if destVar == addVar:
            randReg = f"#st{tRegister}"
            outputText += (f"AL {randReg}, 0({vars.get(addVar)})\nCA {randReg}, {randReg}, {addNum}\n"
                           f"CO {randReg}, 0({vars.get(addVar)})")
    elif line.startswith("printf"):
        if "%d" in line:
            _, intVar = line.split()
            intVar = intVar.replace(")", "").replace(";", "")
            outputText += f"la, #town{aRegister}, 0({vars.get(intVar)})\nGA #town{aRegister}\n"
            aRegister += 1
        else:
            _, text, _ = line.split("\"")
            outputText = f"text{textNum}: .asciiz \"{text}\"\n" + outputText
            outputText += f"SD #town{aRegister}, text{textNum}\nGA #town{aRegister}\n"
            textNum += 1
            aRegister += 1
    elif "%" in line:
        destVar, _, divVar, _, divNum = line.split()
        divReg = f"#st{tRegister}"
        tRegister += 1
        randReg = f"#st{tRegister}"
        tRegister += 1
        outputText += (f"AL {divReg}, 0({vars.get(divVar)})\nCT {randReg}, {divReg}, {divNum}\n"
                       f"KS {vars.get(destVar)}\n")
    elif line.startswith("else if "):
        _, expr = line.split("else if ")
        expr = expr.replace("(", "").replace(")", "").replace("{", "")
        outputText += getElseIfStatement(expr) + "\n"
    elif line.startswith("else {"):
        elseBracket = True
        innerIfStatement = False
    elif line.startswith("if "):
        _, expr = line.split("if ")
        expr = expr.replace("(","").replace(")","").replace("{","")
        outputText += getIfStatement(expr) + "\n"
    elif line.startswith("}"):
        outputText += getEndBracket() + "\n"
    # int declarations
    elif line.startswith("int "):
        _, var = line.split()
        var = var.strip(";")
        outputText += getInstructionLine(var) + "\n"
    # assignments
    elif " = " in line:
        varName, _, val = line.split()
        val = val.strip(";")
        if val.isdigit():
            # immediately value assignments
            outputText += getAssignmentLinesImmediateValue(val, varName) + "\n"
        else:
            # variable assignments
            outputText += getAssignmentLinesVariable(val, varName) + "\n"
    else:
        pass

outputText = ".data\n" + outputText
outputText += "WA LOOP\nFINISH:"
outputFile = open("fizzbuzz.asm", "w")

outputFile.write(outputText)
