#!/usr/bin/python

import sys
import os
import argparse

text_ptr = 0
input_buffer = []
output_buffer = ''
syntax_structure = []
line_no = 0
stmt_counter = 0

class ExprType:
    Statement=0
    Comment=1
    Jump=2

def get_line_length():
    global text_ptr
    global input_buffer

    pos_of_next_newline = text_ptr
    while input_buffer[pos_of_next_newline]!='\n':
        pos_of_next_newline=pos_of_next_newline+1
    return pos_of_next_newline-text_ptr

def isspace(ch):
    return ch=='\t' or ch==' '

def point_to_next_nonspace():
    global text_ptr
    global input_buffer
    global line_no
    while isspace(input_buffer[line_no][text_ptr]):
        text_ptr=text_ptr+1

def point_to_next_line():
    global line_no
    global text_ptr
    text_ptr=0
    line_no=line_no+1

def getline_no_return():
    global text_ptr
    global input_buffer
    return input_buffer[text_ptr:text_ptr+get_line_length()]

def add_syntax_structure(etype, content, label):
    global syntax_structure
    global stmt_counter
    if etype == ExprType.Statement:
        syntax_structure.append([etype,content,label,stmt_counter]);
        stmt_counter=stmt_counter+1
    else:
        syntax_structure.append([etype,content,label]);

def find_jmp_target(label):
    for code in syntax_structure:
        if code[0]!=ExprType.Statement:
            continue
        if code[2]==label:
            return code[3]
    return -1

def syntax_structure_tocode():
    ret = '';
    for code in syntax_structure:
        if code[0] == ExprType.Statement:
            ret = ret + "\tst=%d\t%s\n"%(code[3],code[1])
        elif code[0] == ExprType.Jump:
            jmp_target = find_jmp_target(code[2])
            if jmp_target==-1:
                print("Error: label %s not found"%code[2])
                sys.exit(1)
            if len(code[1])>0:
                ret = ret + "\t\t%s nst=%d\n"%(code[1],jmp_target)
            else:
                ret = ret + "\t\tnst=%d\n"%(jmp_target)
        else:
            ret = ret + code[1] + '\n'
    return ret

def expr():
    global text_ptr
    global line_no
    global input_buffer
    global output_buffer
    if line_no >= len(input_buffer):
        return
    if input_buffer[line_no].strip(' \t\n\r') == '':
        # Empty line
        point_to_next_line()
        expr()
    elif input_buffer[line_no][0] == '*':
        add_syntax_structure(ExprType.Comment,input_buffer[line_no].strip(' \t\n\r'), None)
        point_to_next_line()
        expr()
    elif isspace(input_buffer[line_no][text_ptr]):
        point_to_next_nonspace()
        index_colon = input_buffer[line_no].find(':')
        if index_colon != -1:
            # A statement with a label
            index_label_end=index_colon-1
            while isspace(input_buffer[line_no][index_label_end]):
                index_label_end=index_label_end-1
            label_name = input_buffer[line_no][text_ptr:index_label_end+1]
            index_content_start=index_colon+1
            while isspace(input_buffer[line_no][index_content_start]):
                index_content_start=index_content_start+1
            add_syntax_structure(ExprType.Statement,input_buffer[line_no][index_content_start:].strip(' \t\n\r'),label_name)
            point_to_next_line()
            expr()
        else:
            index_jmp = input_buffer[line_no].find('nst=')
            if index_jmp != -1:
                # A direct jump
                label_name = input_buffer[line_no][index_jmp+4:].strip(' \t\n\r')
                add_syntax_structure(ExprType.Jump,input_buffer[line_no][text_ptr:index_jmp-1].strip(' \t\n\r'),label_name)
                point_to_next_line()
                expr()
            else:
                # A plain statement
                add_syntax_structure(ExprType.Statement,input_buffer[line_no].strip(' \t\n\r'),None)
                point_to_next_line()
                expr()
    else:
        print("Syntax error on line %d:%s"%(line_no,input_buffer[line_no]))
        sys.exit(1)



def main():
    global input_buffer
    if len(sys.argv) < 2:
        print("readable input_file [-o output_file]")
        sys.exit(2)
    path = os.path.split(sys.argv[1])
    read_file_name = path[1].split('.')
    write_file_name = read_file_name[0] + '.out'
    if len(read_file_name)>1:
        write_file_name = write_file_name + '.' +read_file_name[1]
    write_file_path = path[0] + '/' + write_file_name;
    if len(sys.argv) >= 4:
        if sys.argv[2] == '-o':
            write_file_path = sys.argv[3]
    input_file = open(sys.argv[1], 'r')
    for line in input_file:
        input_buffer.append(line)
    expr()
    output_file = open(write_file_path,'w')
    output_file.write(syntax_structure_tocode())
    print("Write successful\n")
    sys.exit(0)

if __name__ == '__main__':
    main()
