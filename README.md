# osiac-toolkit
osiac-toolkit consists of an assembler and a frontend that allows you write OSIAC spec files in a human-friendly manner.
## Assembler
An assembler that convert OSIAC assembly to simulator-compatible test file.

    osiac-assembler.py input_file [-o output_file]
### Example Input File
    AC 1
    X 3
    SP 9
    PC 0
    CVZN 0
    
    SUB #3,X
    BEQ 1
    HALT
    INC -(X)
    
### Output
    0001	AC
    0003	X
    0009	SP
    0000	PC
    0000	CVZN
    2601
    0003
    0092
    0001
    0000
    0231


## Simulator Frontend
A simple simulator frontend that frees you from manually numbering the states.  

    osiac-readable.py input_file [-o output_file]
### Example Input File
    ***************************
    *          TEST           *
    ***************************
    ***  Start fetch cycle  ***
    	fetch:  rt='[pc]-> mar'	imar rac=1 rn=3
    	        rt='[[mar]]-> mdr'	read
    	        rt='[mdr] -> ir'	omdr iir
    	        rt='[pc]+1 -> q'	rac=1 rn=3 ib p1 oadder
    	        rt='[q] -> pc'		oq wac=1 wn=3
    	    	nst=fetch

### Output
    ***************************
    *          TEST           *
    ***************************
    ***  Start fetch cycle  ***
    	st=0	rt='[pc]-> mar'	imar rac=1 rn=3
    	st=1	rt='[[mar]]-> mdr'	read
    	st=2	rt='[mdr] -> ir'	omdr iir
    	st=3	rt='[pc]+1 -> q'	rac=1 rn=3 ib p1 oadder
    	st=4	rt='[q] -> pc'		oq wac=1 wn=3
    		nst=0
