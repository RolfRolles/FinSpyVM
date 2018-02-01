.text:00402B68 VM__NextInsn__Execute:
.text:00402B68     add     [ebx+VMContext.pCurrInsn], size VMInstruction ; Point VM EIP to next instruction
.text:00402B6B     mov     eax, [ebx+VMContext.fpVMEntry]                ; EAX := ordinary VM re-entry location
.text:00402B6E     mov     esp, [ebx+VMContext.SavedESP1]                ; Restore host ESP
.text:00402B71     jmp     [ebx+VMContext.fpVMReEntryToFuncPtr]          ; branch to state-on-stack re-entry