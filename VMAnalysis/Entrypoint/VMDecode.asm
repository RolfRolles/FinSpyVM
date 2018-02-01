; This executes after the code in VMFetch.asm

.text:004024F6         call    Decode                      ; Decode the instruction
                                                           ; See disassembly of Decode, immediately below
                                                           
Disassembly of Decode:

.text:0040246A         pusha
.text:004021C8         lea     edx, [ebx+40h]              ; Point EDX to Data portion of VMInstruction within VMContext
.text:004024B8         mov     ecx, [ebx+28h]              ; ECX := module image base
.text:0040225F         movzx   eax, byte ptr [ebx+3Eh]     ; EAX := Fixup1 from within VMInstruction
.text:0040226C         test    eax, eax                    ; Was Fixup1 non-zero? I.e. was a fixup specified?
.text:0040234C         jz      loc_402238                  ; If taken, no fixup specified

; JNZ path: a fixup was specified
	.text:0040210D     and     al, 7Fh                       ; Mask off Fixup1 to low 7 bits
	.text:00402118     add     [eax+edx], ecx                ; Add the imagebase to the DWORD in the Data portion at Fixup1

.text:00402238         movzx   eax, byte ptr [ebx+3Fh]     ; EAX := Fixup2 from within VMInstruction         
.text:0040219D         test    eax, eax                    ; Was Fixup2 non-zero? I.e. was a fixup specified?
.text:004022EE         jz      loc_4023C3                  ; If taken, no fixup specified                    

; JNZ path: a fixup was specified
	.text:0040221A     and     al, 7Fh                       ; Mask off Fixup2 to low 7 bits                               
	.text:00402222     add     [eax+edx], ecx                ; Add the imagebase to the DWORD in the Data portion at Fixup2

.text:004023C3         popa
.text:00402155         retn
