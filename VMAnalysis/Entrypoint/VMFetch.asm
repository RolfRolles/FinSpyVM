; This executes after the code in VMInitialize.asm

.text:004020FB         mov     esi, [ebx]                  ; ESI := pCurrInsn from VM Context
.text:00402412         lea     edi, [ebx+38h]              ; EDI := Instruction within VMContext
.text:00402164         cld
.text:00402323         mov     ecx, 18h                    ; ECX := sizeof(VMInstruction)
.text:00402206         rep movsb                           ; Copy raw instruction from pointer into VM Context structure
.text:004022DD         lea     eax, [ebx+38h]              ; EAX := Instruction within VMContext
.text:00402428         mov     ecx, 18h                    ; ECX := sizeof(VMInstruction)
.text:0040224C         mov     edx, [ebp+0BB1h]            ; Fetch XOR key from .text section
.text:00402396         push    edx                         ; Arg #3: XOR key
.text:00402397         push    ecx                         ; Arg #2: size (sizeof(VMInstruction))
.text:00402398         push    eax                         ; Arg #1: VMInstruction within VMContext
.text:00402399         call    XorDecrypt                  ; Decrypt VMInstruction by XORing with key
                                                           ; See disassembly in VMPreInitialize.asm (search for XorDecrypt)
