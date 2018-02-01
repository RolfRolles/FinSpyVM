.text:00402B74 VM__RelativeJump__Execute:
.text:00402B74     mov     eax, [ecx+1]                         ; Instruction data at DWORD +1 contains 
.text:00402B74                                                  ; a displacement for the VM EIP
.text:00402B77     test    eax, eax                             ; Was it non-zero?
.text:00402B79     jz      short jump_to_x86                    ; No -- branch to x86 code at [ecx+5]
.text:00402B7B     add     [ebx+VMContext.pCurrInsn], eax       ; Add the displacement to VM EIP
.text:00402B7D     mov     eax, [ebx+VMContext.fpVMEntry]       ; eax := state-in-registers VM entry
.text:00402B80     mov     esp, [ebx+VMContext.SavedESP1]       ; esp := restore host ESP
.text:00402B83     jmp     [ebx+VMContext.fpVMReEntryToFuncPtr] ; branch to state-on-stack re-entry
.text:00402B86 ; ---------------------------------------------------------------------------
.text:00402B86
.text:00402B86 jump_to_x86:                             ; CODE XREF: ...
.text:00402B86     mov     eax, [ecx+5]                         ; Otherwise, use [ecx+5] as x86 RVA
.text:00402B89     add     eax, [ebx+VMContext.dwBaseAddress]   ; Convert RVA to VA
.text:00402B8C     mov     esp, [ebx+VMContext.SavedESP1]       ; esp := restore host ESP
.text:00402B8F     jmp     [ebx+VMContext.fpVMReEntryToFuncPtr] ; branch to state-on-stack re-entry
