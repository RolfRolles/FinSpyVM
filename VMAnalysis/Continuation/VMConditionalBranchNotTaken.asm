.text:00402B68 VM__NextInsn__Execute:
.text:00402B68     add     [ebx+VMContext.pCurrInsn], size VMInstruction ; Point VM EIP to next instruction
.text:00402B6B     mov     eax, [ebx+VMContext.fpVMEntry] ; 004022A9: pointer to post-VM-setup entrypoint (pusha/pushf) (0x004020EA for this sample)
.text:00402B6E     mov     esp, [ebx+VMContext.SavedESP1] ; 004024A2: saved ESP before VM entry
.text:00402B71     jmp     [ebx+VMContext.fpVMReEntryToFuncPtr] ; 00402389: pointer to VM "re-entry sequence" (takes eax = VM entry *) (0x00402B92 for this sample)
