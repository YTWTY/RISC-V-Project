import os
import argparse

MemSize = 1000 # memory size, in reality, the memory size should be 2^32, but for this lab, for the space resaon, we keep it as this large number, but the memory is still 32-bit addressable.






class InsMem(object): # instruction memory指令内存
    def __init__(self, name, ioDir):
        self.id = name
        
        with open(ioDir + "\\imem.txt") as im:
            self.IMem = [data.replace("\n", "") for data in im.readlines()]

    def readInstr(self, ReadAddress): # 读取指令
        #read instruction memory
        #return 32 bit hex val
        return (self.IMem[ReadAddress] + self.IMem[ReadAddress+1]+self.IMem[ReadAddress+2] + self.IMem[ReadAddress+3])

          
class DataMem(object): # data memory 数据内存
    def __init__(self, name, ioDir):
        self.id = name
        self.ioDir = ioDir
        with open(ioDir + "\\dmem.txt") as dm:
            self.DMem = [data.replace("\n", "") for data in dm.readlines()]

    def readInstr(self, ReadAddress): # 读取数据
        #read data memory
        #return 32 bit hex val
        return (self.DMem[ReadAddress] + self.DMem[ReadAddress+1] + self.DMem[ReadAddress+2] + self.DMem[ReadAddress+3])
        
    
    def writeDataMem(self, Address, WriteData): # 将数据写入数据内存
        self.DMem[Address] = WriteData


    def outputDataMem(self): # 输出数据内存内容
        resPath = self.ioDir + "\\" + self.id + "_DMEMResult.txt"
        with open(resPath, "w") as rp:
            rp.writelines([str(data) + "\n" for data in self.DMem])

class RegisterFile(object):
    def __init__(self, ioDir):
        self.outputFile = ioDir + "RFResult.txt"
        self.Registers = [0x0 for i in range(32)] # 寄存器地址
    
    def readRF(self, Reg_addr): # 读取寄存器值
        # Fill in
        return(self.Registers[Reg_addr])
    
    def writeRF(self, Reg_addr, Wrt_reg_data): # 写入寄存器值
        # Fill in
        self.Registers[Reg_addr] = Wrt_reg_data
         
    def outputRF(self, cycle): # 输出每个循环的寄存器值
        op = ["-"*70+"\n", "State of RF after executing cycle:" + str(cycle) + "\n"]
        op.extend([str(val)+"\n" for val in self.Registers])
        if(cycle == 0): perm = "w"
        else: perm = "a"
        with open(self.outputFile, perm) as file:
            file.writelines(op)

class State(object):
    def __init__(self):
        self.IF = {"nop": False, "PC": 0}# nop 终止
        self.ID = {"nop": False, "Instr": 0}
        self.EX = {"nop": False, "Read_data1": 0, "Read_data2": 0, "Imm": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "is_I_type": False, "rd_mem": 0, 
                   "wrt_mem": 0, "alu_op": 0, "wrt_enable": 0}
        self.MEM = {"nop": False, "ALUresult": 0, "Store_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "rd_mem": 0, 
                   "wrt_mem": 0, "wrt_enable": 0}
        self.WB = {"nop": False, "Wrt_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "wrt_enable": 0}

class Core(object):
    def __init__(self, ioDir, imem, dmem):
        self.myRF = RegisterFile(ioDir) # 初始化·寄存器
        self.cycle = 0 # 初始化循环
        self.halted = False
        self.ioDir = ioDir
        self.state = State()
        self.nextState = State()
        self.ext_imem = imem
        self.ext_dmem = dmem

class SingleStageCore(Core): # 单循环核 single cycle
    def __init__(self, ioDir, imem, dmem):
        super(SingleStageCore, self).__init__(ioDir + "\\SS_", imem, dmem)
        self.opFilePath = ioDir + "\\StateResult_SS.txt"

    def step(self):
        '''
        指令提取 instruction fetch
                PC 给指令内存地址
                内存输出指令内容
                PC + 4

        '''
        PC_value = self.state.IF['PC']
        PC_next = PC_value + 4
        instruction = self.ext_imem.readInstr(PC_value)  # 从指令内存提取指令
        #print(instruction[:12])

        self.state.ID['Instr'] = instruction
        opcode = instruction[25:]
        

        if opcode == '0110011':  # R type
            funt3 = instruction[17:20]
            rs1_v = self.myRF.readRF(int(instruction[12:17], base=2))
            rs2_v = self.myRF.readRF(int(instruction[7:12], base=2))
            rd = instruction[20:25]

            if funt3 == '000':
                if instruction[0:7] == '0000000':  # ADD
                    self.myRF.writeRF(rd, rs1_v + rs2_v)
                else:  # SUB
                    self.myRF.writeRF(rd, rs1_v - rs2_v)

            elif funt3 == '100':  # XOR
                self.myRF.writeRF(rd, rs1_v ^ rs2_v)
            elif funt3 == '110':  # OR
                self.myRF.writeRF(rd, rs1_v | rs2_v)
            elif funt3 == '111':  # AND
                self.myRF.writeRF(rd, rs1_v & rs2_v)

        elif opcode == '0010011':  # I type
            funt3 = instruction[17:20]
            rs1_v = self.myRF.readRF(instruction[12:17])
            print(rs1_v)
            rd = instruction[20:25]
            imm = instruction[0:12]
            if funt3 == '000': # ADDI
                self.myRF.writeRF(rd, rs1_v + imm)
            elif funt3 == '100': # XORI
                self.myRF.writeRF(rd, rs1_v ^ imm)
            elif funt3 == '110': # ORI
                self.myRF.writeRF(rd, rs1_v | imm)
            elif funt3 == '111': # ANDI
                self.myRF.writeRF(rd, rs1_v & imm)

        elif opcode == '1101111':  # J typr
            rd = instruction[20:25]
            self.myRF.writeRF(rd, PC_next)
            PC_next = PC_value + \
                instruction[0]+instruction[12:20]+instruction[11]+instruction[1:10]

        elif opcode == '1100011':  # B type
            funt3 = instruction[17:20]
            rs1_v = self.myRF.readRF(int(instruction[12:17], base=2))
            rs2_v = self.myRF.readRF(int(instruction[7:12], base=2))
            imm = instruction[20:24] + instruction[1:7] + \
                instruction[24] + instruction[0]
            if funt3 == '000': # BEQ 
                if rs1_v == rs2_v:
                    PC_next = PC_value + imm
                else:
                    PC_next = PC_next
            else: # BNE
                if rs1_v != rs1_v:
                    PC_next = PC_value + imm
                else:
                    PC_next = PC_next

        elif opcode == '0000011':  # I type Load
            rd = instruction[20:25]
            rs1_v = self.myRF.readRF(int(instruction[12:17], base=2))
            imm = instruction[0:12]
            self.myRF.writeRF(int(rd, base=2), self.ext_dmem.readInstr(rs1_v + int(imm, base=2)))

        elif opcode == '0100011':  # S type
            rs1_v = self.myRF.readRF(int(instruction[12:17], base=2))
            rs2_v = self.myRF.readRF(int(instruction[7:12], base=2))
            imm = instruction[0:7]+instruction[20:25]
            self.ext_dmem.writeDataMem(rs1_v+imm, rs2_v)

        else:  # Halt and other option
            self.state.IF["nop"] = True



        self.halted = True

        if self.state.IF["nop"]:
            self.halted = True
            
        self.myRF.outputRF(self.cycle) # dump RF
        self.printState(self.nextState, self.cycle) # print states after executing cycle 0, cycle 1, cycle 2 ... 
            
        self.state = self.nextState #The end of the cycle and updates the current state with the values calculated in this cycle
        self.cycle += 1

    def printState(self, state, cycle):
        printstate = ["-"*70+"\n", "State after executing cycle: " + str(cycle) + "\n"]
        printstate.append("IF.PC: " + str(state.IF["PC"]) + "\n")
        printstate.append("IF.nop: " + str(state.IF["nop"]) + "\n")
        
        if(cycle == 0): perm = "w"
        else: perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)

class FiveStageCore(Core):
    def __init__(self, ioDir, imem, dmem):
        super(FiveStageCore, self).__init__(ioDir + "\\FS_", imem, dmem)
        self.opFilePath = ioDir + "\\StateResult_FS.txt"

    def step(self):
        # Your implementation
        # --------------------- WB stage ---------------------Writeback
        
        
        
        # --------------------- MEM stage --------------------Load/ Store
        
        
        
        # --------------------- EX stage ---------------------Execute
        
        
        
        # --------------------- ID stage ---------------------Instruction Decode/ Register Read
        
        
        
        # --------------------- IF stage ---------------------Instruction Fetch
        
        self.halted = True
        if self.state.IF["nop"] and self.state.ID["nop"] and self.state.EX["nop"] and self.state.MEM["nop"] and self.state.WB["nop"]:
            self.halted = True
        
        self.myRF.outputRF(self.cycle) # dump RF
        self.printState(self.nextState, self.cycle) # print states after executing cycle 0, cycle 1, cycle 2 ... 
        
        self.state = self.nextState #The end of the cycle and updates the current state with the values calculated in this cycle
        self.cycle += 1

    def printState(self, state, cycle):
        printstate = ["-"*70+"\n", "State after executing cycle: " + str(cycle) + "\n"]
        printstate.extend(["IF." + key + ": " + str(val) + "\n" for key, val in state.IF.items()])
        printstate.extend(["ID." + key + ": " + str(val) + "\n" for key, val in state.ID.items()])
        printstate.extend(["EX." + key + ": " + str(val) + "\n" for key, val in state.EX.items()])
        printstate.extend(["MEM." + key + ": " + str(val) + "\n" for key, val in state.MEM.items()])
        printstate.extend(["WB." + key + ": " + str(val) + "\n" for key, val in state.WB.items()])

        if(cycle == 0): perm = "w"
        else: perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)

if __name__ == "__main__":
     
    #parse arguments for input file location
    parser = argparse.ArgumentParser(description='RV32I processor')
    parser.add_argument('--iodir', default="", type=str, help='Directory containing the input files.')
    args = parser.parse_args()

    ioDir = os.path.abspath(args.iodir)
    print("IO Directory:", ioDir)

    imem = InsMem("Imem", ioDir)
    print('ioDirction is '+ str(ioDir))
    dmem_ss = DataMem("SS", ioDir)
    dmem_fs = DataMem("FS", ioDir)
    
    ssCore = SingleStageCore(ioDir, imem, dmem_ss)
    fsCore = FiveStageCore(ioDir, imem, dmem_fs)

    while(True):
        if not ssCore.halted:
            ssCore.step()
        
        if not fsCore.halted:
            fsCore.step()

        if ssCore.halted and fsCore.halted:
            break
    
    # dump SS and FS data mem.
    dmem_ss.outputDataMem()
    dmem_fs.outputDataMem()
