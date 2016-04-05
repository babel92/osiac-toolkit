#!/usr/bin/python

import sys
import os
import argparse

Instruction = [
    ["ADD",2,1],
    ["SUB",2,2],
    ["MOVE",2,3],
    ["EXG",2,4],
    ["OR",2,5],
    ["AND",2,6],
    ["CLR",1,1],
    ["INC",1,2],
    ["DEC",1,3],
    ["NEG",1,4],
    ["COMP",1,5],
    ["JMP",1,6],
    ["JSR",1,7],
    ["TST",1,8],
    ["RTS",0,'0080'],
    ["DBRA",1],
    ["HALT",0,'0000'],
    ['BEQ',3,'0092'],
    ['BNE',3,'0082'],
    ['BPL',3,'0081'],
    ['BMI',3,'0091'],
    ['BLS',3,'009A'],
    ['BHI',3,'00BA']
]

Register = [
    "AC",
    "X",
    "SP",
    "PC",
    "CVZN"
]

AC=0
X=0
SP=0
PC=0
CVZN=0

class Token_Type:
    INS=0
    SYMBOL=1
    NUMBER=2
    NAME=3
    REG=4
    NEWLINE=5
    EOF=6
    COMMENT=7
    DATA=8
    ERROR=99

class CodeComposer:
    def __init__(self):
        self.code=""
    def append(self,str):
        self.code=self.code+str
    def prepend(self,str):
        self.code=str+'\n'+self.code
    def newInstruction(self,ins_record,msrc,mdest,src,dest):
        if ins_record[1]==0:
            self.append(ins_record[2]+'\n')
        elif ins_record[1]==1:
            c=0
            c=c|(ins_record[2]<<8)
            c=c|(mdest<<4)
            c=c|dest
            self.append("%04X\n"%c)
        elif ins_record[1]==2:
            c=0
            c=c|(ins_record[2]<<12)
            c=c|(msrc<<8)
            c=c|(mdest<<4)
            c=c|(src<<2)
            c=c|dest
            self.append("%04X\n"%c)
        elif ins_record[1]==3:
            self.append(ins_record[2]+'\n')
    def getCode(self):
        global AC,X,SP,PC,CVZN
        return "%04X\tAC\n%04X\tX\n%04X\tSP\n%04X\tPC\n%04X\tCVZN\n%s"%(AC,X,SP,PC,CVZN,self.code)

class Lexer:

    def __init__(self, src_code):
        self.line_no=1
        self.src=src_code
        self.ptr=0

    def isspace(self,ch):
        return ch=='\t' or ch==' '

    def isnamechar(self,ch):
        return ch.isalnum() or ch=='_'

    def isnum(self,ch):
        return ch.isdigit() or ch=='+' or ch=='-'

    def iseof(self):
        return self.ptr>=len(self.src)

    def deplete_space(self):
        while not self.iseof() and self.isspace(self.src[self.ptr]):
            self.ptr=self.ptr+1

    def findInInstructionTable(self,str):
        global Instruction
        for i in range(len(Instruction)):
            if Instruction[i][0]==str.upper():
                return i
        return -1

    def findInRegisterTable(self,str):
        global Register
        for i in range(len(Register)):
            if Register[i]==str.upper():
                return i
        return -1

    def getLineNo(self):
        return self.line_no

    def peekNextToken(self):
        self.deplete_space()
        token_len=0
        if self.ptr>=len(self.src):
            return [Token_Type.EOF,""]
        elif self.src[self.ptr]=='*':
            while self.src[self.ptr+token_len]=='\r' \
            or self.src[self.ptr+token_len]=='\n':
                token_len=token_len+1
                if self.iseof():
                    break
            return [Token_Type.COMMENT,self.src[self.ptr:self.ptr+token_len]]
        elif self.src[self.ptr]=='+' or self.src[self.ptr]=='-':
            if self.src[self.ptr+1].isdigit():
                while self.isnum(self.src[self.ptr+token_len]):
                    token_len=token_len+1
                    if self.ptr+token_len>=len(self.src):
                        break
                token=self.src[self.ptr:self.ptr+token_len]
                return [Token_Type.NUMBER,token]
            else:
                return [Token_Type.SYMBOL,self.src[self.ptr]]

        elif self.src[self.ptr].isalpha():
            while self.src[self.ptr+token_len].isalpha():
                token_len=token_len+1
                if self.ptr+token_len>=len(self.src):
                    break
            token=self.src[self.ptr:self.ptr+token_len]
            if self.findInInstructionTable(token)!=-1:
                return [Token_Type.INS,token]
            elif self.findInRegisterTable(token)!=-1:
                return [Token_Type.REG,token]
            elif token=='DATA':
                return [Token_Type.DATA,token]
            else:
                return [Token_Type.NAME,token]
        elif self.isnum(self.src[self.ptr]):
            while self.isnum(self.src[self.ptr+token_len]):
                token_len=token_len+1
                if self.ptr+token_len>=len(self.src):
                    break
            token=self.src[self.ptr:self.ptr+token_len]
            return [Token_Type.NUMBER,token]
        elif self.src[self.ptr]=='(' \
        or self.src[self.ptr]==')' \
        or self.src[self.ptr]==':' \
        or self.src[self.ptr]=='#' \
        or self.src[self.ptr]==',':
            return [Token_Type.SYMBOL,self.src[self.ptr]]
        elif self.src[self.ptr]=='\n':
            return [Token_Type.NEWLINE,self.src[self.ptr]]
        elif  self.src[self.ptr]=='\r':
            return [Token_Type.NEWLINE,'\r\n']
        else:
            return [Token_Type.ERROR,""]

    def getNextToken(self):
        tok=self.peekNextToken()
        self.ptr=self.ptr+len(tok[1])
        if tok[0]==Token_Type.NEWLINE:
            self.line_no=self.line_no+1
        return tok

    def match(self, ch):
        tok=self.peekNextToken()
        if tok[1]!=ch:
            return False
        self.ptr=self.ptr+len(tok[1])
        return True



def NewLine(l,out):
    tok=l.getNextToken()
    if tok[0]!=Token_Type.NEWLINE and tok[0]!=Token_Type.EOF:
        print("Syntax error: (%d): %s\n"%(l.getLineNo(),"new line expected"))
        print(tok)
        print(out.getCode())
        traceback.print_exc()
        sys.exit(1)

def RegName(l,out):
    tok = l.getNextToken()
    if tok[0]!=Token_Type.REG:
        print("Syntax error: (%d):\"%s\" %s\n"%(l.getLineNo(),token[1],"is not a register"))
        sys.exit(1)
    return tok[1]

def Ins(l):
    tok = l.getNextToken()
    if tok[0]!=Token_Type.INS:
        print("Syntax error: (%d):\"%s\" %s\n"%(l.getLineNo(),tok[1],"is not an instruction"))
        sys.exit(1)
    return Instruction[l.findInInstructionTable(tok[1])]

def Val(l,out):
    tok = l.getNextToken()
    if tok[0]!=Token_Type.NUMBER:
        print("Syntax error: (%d):\"%s\" %s\n"%(l.getLineNo(),tok[1],"is not a number"))
        sys.exit(1)
    return int(tok[1])

def Match(l,ch):
    if not l.match(ch):
        print("Syntax error: (%d): %s\n"%(l.getLineNo()," maybe a\'"+ch+"\' is missing?"))
        print(l.peekNextToken())
        traceback.print_exc()
        sys.exit(1)


def Operand(l,out):
    tok = l.peekNextToken()
    if tok[0]==Token_Type.REG:

        return [0,l.findInRegisterTable(l.getNextToken()[1])]
    elif tok[0]==Token_Type.SYMBOL:
        if tok[1]=='(':
            Match(l,'(')
            rn=RegName(l,out)
            Match(l,')')
            if l.match('+'):
                # 2 Autoincrement
                return [2,l.findInRegisterTable(rn)]
            # 1 Reg Indirect
            return [1,l.findInRegisterTable(rn)]
        elif tok[1]=='-':
            Match(l,'-')
            Match(l,'(')
            rn=RegName(l,out)
            Match(l,')')
            # 3 Autodecrement
            return [3,l.findInRegisterTable(rn)]
        elif tok[1]=='#':
            Match(l,'#')
            v=Val(l,out)
            # 6 Immediate
            return [6,0,v]
        else:
            print("Syntax error: (%d):\"%s\" %s\n"%(l.getLineNo(),tok[1]," unexpected token"))
            sys.exit(1)
    elif tok[0]==Token_Type.NUMBER:
        v=Val(l,out)
        if l.match('('):
            rn=RegName(l,out)
            Match(l,')')

            return [4,l.findInRegisterTable(rn),v]
        # 5 Absolute
        return [5,0,v]
    else:
        print("Syntax error: (%d): %s\n"%(l.getLineNo(),"Illegal operand format"))
        sys.exit(1)



def Statement(l,out):
    ins = Ins(l)
    print(ins)
    if ins[1]==0:
        out.newInstruction(ins,None,None,None,None)

    elif ins[1]==1:
        dest=Operand(l,out)
        out.newInstruction(ins,None,dest[0],None,dest[1])
        if dest[0]>3:
            out.append("%04X\n"%dest[2])
    elif ins[1]==2:
        src=Operand(l,out)
        Match(l,',')
        dest=Operand(l,out)
        out.newInstruction(ins,src[0],dest[0],src[1],dest[1])
        if src[0]>0 and dest[0]>0:
            print("Syntax error: (%d): %s\n"%(l.getLineNo(),"One operand must be a register"))
            sys.exit(1)
        if src[0]>3:
            out.append("%04X\n"%src[2])
        if dest[0]>3:
            out.append("%04X\n"%dest[2])
    elif ins[1]==3:
        # Branching
        off=Val(l,out)
        out.newInstruction(ins,None,None,None,None)
        out.append("%04X\n"%off)
    NewLine(l,out)

def Initializer(l,out):
    global AC,X,SP,PC,CVZN
    name=RegName(l,out)
    val=Val(l,out)
    NewLine(l,out)
    if name=='AC':
        AC=val
    elif name=='X':
        X=val
    elif name=='SP':
        SP=val
    elif name=='PC':
        PC=val
    elif name=='CVZN':
        CVZN=val
    else:
        print("Syntax error: (%d):\"%s\" %s\n"%(l.getLineNo(),name," is not a register"))
        sys.exit(1)

def Data(l,out):
    l.getNextToken()
    val=Val(l,out)
    out.append("%04X\n"%val)


def Block(l,out):
    token = l.peekNextToken()
    if token[0]==Token_Type.EOF:
        Finish(l,out)
        return
    elif token[0]==Token_Type.NEWLINE:
        l.getNextToken()
    elif token[0]==Token_Type.INS:
        Statement(l,out)
    elif token[0]==Token_Type.REG:
        Initializer(l,out)
    elif token[0]==Token_Type.DATA:
        Data(l,out)
    else:
        print("Syntax error: (%d):\"%s\"\n"%(l.getLineNo(),token[1]))
        sys.exit(1)
    Block(l,out)

def Finish(l,out):
    pass

def main():
    if len(sys.argv) < 2:
        print("oas input_file [-o output_file]")
        sys.exit(2)
    path = os.path.split(sys.argv[1])
    read_file_name = path[1].split('.')
    write_file_name = read_file_name[0] + '.out'
    if len(read_file_name)>1:
        write_file_name = write_file_name + '.' +read_file_name[1]
    write_file_path = os.getcwd() + '/' + write_file_name;
    if len(sys.argv) >= 4:
        if sys.argv[2] == '-o':
            write_file_path = sys.argv[3]
    input_file = open(sys.argv[1], 'r')
    src=input_file.read()
    output=CodeComposer()
    lexer = Lexer(src)
    Block(lexer,output)
    output_file = open(write_file_path,'w')
    output_file.write(output.getCode())
    sys.exit(0)

if __name__ == '__main__':
    main()
