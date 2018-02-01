.text:00402C6F     mov     eax, [esp+24h] ; Get saved VMInstruction * from stack
.text:00402CB0     lea     esi, [esp+20h] ; esi = address of registers begin
.text:00402C4E     lea     edi, [esp+24h] ; edi = address of VMInstruction *
.text:00402C40     mov     ecx, 9 
.text:00402C66     std                    ; Move saved registers/flags up by
.text:00402C93     rep movsd              ; one DWORD, erasing the VMInstruction *
.text:00402CAA     cld
.text:00402C79     add     esp, 4         ; Adjust stack to remove superfluous DWORD
.text:00402C8B     mov     [ebx+VMContext.pCurrInsn], eax ; Set next instruction
.text:00402C58     sub     [ebx+VMContext.pScratch], 30h  ; Pop function stack
.text:00402C83     mov     eax, [ebx+VMContext.fpVMEntry] ; Get VM entry pointer
.text:00402C9F     jmp     [ebx+VMContext.fpVMReEntryToFuncPtr] ; Use state-on-stack return
