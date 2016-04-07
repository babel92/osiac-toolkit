# osiac-toolkit
osiac-toolkit consists of an assembler and a frontend that allows you write OSIAC spec files in a human-friendly manner.
## Assembler
An assembler that convert OSIAC assembly to simulator-compatible test file.

    osiac-assembler.py input_file [-o output_file]
### Example Input File

		AC 0
		X 3
		SP 9
		PC 4
		CVZN 0

		DATA 1
		DATA 2
		DATA 3
		DATA 4
		ADD #6,X
		ADD X,(AC)
		ADD (AC)+,X
		ADD X,-(AC)
		MOVE #2,AC
		ADD -(AC),X
		ADD (AC)+,X
		ADD 3(AC),X
		ADD 3,AC
		MOVE #2,2
		ADD X,(X)+


### Output

		0000	AC
		0003	X
		0009	SP
		0004	PC
		0000	CVZN
		0001
		0002
		0003
		0004
		1601
		0006
		1014
		1201
		1034
		3600
		0002
		1301
		1201
		1401
		0003
		1500
		0003
		3650
		0002
		0002
		1025
    
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
