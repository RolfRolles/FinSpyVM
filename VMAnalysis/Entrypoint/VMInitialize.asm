; This code executes after the code in VMPreInitialize.asm

.text:0040247C  pusha                                      ; Save registers
.text:004022BB  pushf                                      ; Save flags

.text:0040212C  call    $+5
.text:00402131  pop     ebp                                ; EBP=0x00402131 (PIC base)
.text:0040213C  call    GetVMContextThreadArray            ; Get global VM Context * pointer array
                                                           ; See disassembly in VMPreInitialize.asm (search for GetVMContextThreadArray)
.text:00402141  mov     ebx, eax
.text:00402450  call    GetThreadIdx                       ; Get index of current thread
                                                           ; See disassembly in VMPreInitialize.asm (search for GetThreadIdx)
.text:00402455  mov     ebx, [ebx+eax*4]                   ; Fetch VMContext * for this thread
.text:004022CA  mov     [ebx+24h], ebp                     ; Store PIC base pointer into VM Context
.text:00402364  lea     eax, [ebp-47h]                     ; EAX points to the beginning of this code sequence (0x0040247C)
.text:004022A9  mov     [ebx+0Ch], eax                     ; Save VM Initialization pointer into VM Context
.text:00402177  lea     eax, [ebp+462h]                    ; EAX points to FindInstructionByKey
                                                           ; See disassembly in VMPreInitialize.asm (search for FindInstructionByKey)
.text:0040243E  mov     [ebx+34h], eax                     ; Save &FindInstructionByKey into VM Context *

.text:004021B2  cmp     dword ptr [ebp+0BB9h], 2           ; Are we executing in kernel mode?
.text:00402306  jnz     loc_4023EF                         ; If taken, user mode

; JNZ path: USER MODE
	.text:004021DC  lea     eax, [ebp+0A61h]                 ; EAX := pointer to user-mode ordinary VM re-entry sequence

; JZ path: KERNEL MODE
	.text:00402294         lea     eax, [ebp+0A95h]          ; EAX := pointer to kernel-mode ordinary VM re-entry sequence

.text:00402389         mov     [ebx+10h], eax              ; Save ordinary VM re-entry pointer into VM Context *
.text:004023AF         lea     eax, [ebp+0B08h]            ; EAX := pointer to re-entry sequence for conditional branch taken
.text:004023B5         mov     [ebx+14h], eax              ; Save conditional branch taken re-entry pointer to VM Context *
.text:004023D7         lea     eax, [ebp+0A43h]            ; EAX := pointer to re-entry sequence for conditional branch not taken
.text:00402280         mov     [ebx+18h], eax              ; Save conditional branch not taken re-entry pointer to VM Context *
.text:004024DE         lea     eax, [ebp+0A37h]            ; EAX := pointer to "call return" re-entry sequence
.text:00402375         mov     [ebx+1Ch], eax              ; Save "call return" re-entry sequence into VM Context *

.text:004024A2         mov     [ebx+2Ch], esp              ; Save host ESP into VM Context *
.text:004021F3         mov     [ebx+30h], esp              ; Save host ESP into VM Context * again
.text:004024CB         mov     esp, [ebx+4]                ; Set host ESP to VM x86 stack area

