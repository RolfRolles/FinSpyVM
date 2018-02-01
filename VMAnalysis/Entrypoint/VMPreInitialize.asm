.text:00401BF6  push    eax ; PUSHFD sequence, in order, EBX in place of ESP
.text:00401D5C  push    ecx
.text:004019D2  push    edx
.text:004020A4  push    ebx
.text:00401CEC  push    ebx
.text:00401DA7  push    ebp
.text:00401F41  push    esi
.text:00401EFF  push    edi
.text:00401E9D  pushf       ; Push flags

.text:00401F60  call    $+5
.text:00401F65  pop     ebp ; Establish EBP=0x00401F65 as PIC base

.text:00401F2C  call    GetVMContextThreadArray ; Retrieves the value of dword_420398 into EAX
                                                ; See disassembly below (search for GetVMContextThreadArray)

.text:00401F31  test    eax, eax                ; Was the global VM context pointer array already allocated?
.text:00401EAD  jnz     loc_401B05

; JZ path: VM CONTEXT POINTER ARRAY DOES NOT EXIST
	.text:00401F83  cmp     dword ptr [ebp+0D85h], 2 ; [0x00402CEA]
	.text:00401D94  jnz     loc_402094               ; JNZ taken: executing in user mode

	; JZ path: KERNEL MODE
	; It's not entirely clear what this code is doing... I just ignored it since
	; it won't execute for my sample
		.text:004019FC         xor     edx, edx
		.text:00401960         mov     eax, [esp+0Ch]	 ; Get saved EBP
		.text:00401DB6         mov     edi, [eax+8]    ; Get first argument
		.text:00401A0C         mov     esi, [edi+14h]  ; Get structure element
		.text:00401DDA         cld
		@LODSD_AGAIN:
		.text:00401F18         lodsd                   ; First structure element is linked list pointer
		.text:00401C07         xchg    eax, esi        ; Move it into EAX
		.text:00401EE8         inc     edx             ; Increment EDX counter
		.text:00401ED5         cmp     esi, [edi+14h]  ; Did the first structure element, in [EDI+14h], match
		                                               ; the one we just loaded into ESI?
		.text:00401981         jnz     @LODSD_AGAIN    ; No, keep looking
		
		.text:00401B80         sub     edx, 0Ah        ; Was it found in more than 9 linked list entries?
		.text:004019E6         jns     loc_402094		   ; If so, take this jump

		; JS path: Found within first 10 elements
		; Return 0
			.text:00401B71         popf
			.text:00402076         pop     edi
			.text:00401D6E         pop     esi
			.text:00401BE2         pop     ebp			
			.text:00401A78         pop     ebx			
			.text:00401E65         pop     ebx			
			.text:00402056         pop     edx			
			.text:00401F97         pop     ecx			
			.text:004019C1         pop     eax			
			.text:00401A63         mov     esp, ebp			
			.text:00401F6D         pop     ebp			
			.text:00401FEA         xor     eax, eax			
			.text:004020B7         retn    8
			
	.text:00401CFA  push    100000h
	.text:00401CFF  call    AllocateMemory ; <- Allocate 100000h bytes worth of memory
	                                       ; See disassembly below (Search for AllocateMemory)

	.text:00401D04  mov     ecx, eax
	.text:00401AF5  call    SetVMContextThreadArray ; Store the pointer just allocated into the
	                                                ; global VM context pointer array pointer
	                                                ; See disassembly below (search for SetVMContextThreadArray)

; MERGE AFTER ALLOCATING VM DATA:
; I.e. we get here regardless of whether we allocated, or it already existed

.text:00401B05  call    GetVMContextThreadArray
.text:00401B0A  mov     ebx, eax
.text:00401D2B  call    GetThreadIdx ; Get the current thread ID, shifted right by 2
                                     ; See disassembly below (search for GetThreadIdx)

.text:00401D30  mov     ebx, [ebx+eax*4] ; Get VMContext * for this thread
.text:00401EEE  test    ebx, ebx         ; Was VMContext * already allocated?
.text:004019AC  jnz     loc_401BA5       ; Take jump if it was allocated

; JZ path: VMContext * not already allocated
	.text:00401B45  push    10000h
	.text:00401B4A  call    ALLOCATE_MEMORY ; Allocate a VMContext * object
	.text:00401B4F  xchg    eax, ebx
	.text:00401ABF  call    GetVMContextThreadArray
	.text:00401AC4  xchg    eax, ecx
	.text:00401DEC  call    GetThreadIdx
	.text:00401DF1  mov     [ecx+eax*4], ebx ; Store allocated VMContext * in global thread pointer array
	.text:00401B19  mov     ecx, [ebp+0D79h]

		.text:00402CDE     BASE_ADDRESS dd 400000h

	.text:00401FA9  mov     [ebx+28h], ecx   ; Set base address in VMContext *
	.text:00401A2F  mov     eax, ebx
	.text:00401BCC  add     eax, 0FFFCh
	.text:00401AAD  mov     [ebx+4], eax     ; Initialize stack pointer within VMContext *
	.text:00401EC2  lea     eax, [ebx+50h]
	.text:00401C56  add     eax, 4
	.text:00401998  mov     [ebx+50h], eax   ; Initialize dynamically generated code stack base
	.text:004020D7  mov     eax, [ebp+0D75h] ; Get RVA for instruction blob

		.text:00402CDA  dd 0C4CDh

	.text:00401E1A  add     eax, [ebp+0D79h] ; Turn instruction blob RVA into real address

		.text:00402CDE     BASE_ADDRESS dd 400000h

	.text:00401BB3  mov     ecx, [ebp+0D71h] ; Get size of instruction blob

		.text:00402CD6  dd 60798h

	.text:00401DC7  test    ecx, ecx         ; Was size of instruction blob 0? If so, uncompressed
	.text:00401F47  jnz     loc_401971       ; Jump taken: instructions were compressed

	; JZ path: instructions not compressed
		.text:00402033  mov     ecx, [ebp+0D5Dh] ; Fetch pointer to where decompressed instructions are stored

			.text:00402CC2  dd offset unk_42039C
	
		.text:00401C43  mov     [ecx], eax		   ; Store uncompressed instruction pointer from .text section
	
	; JNZ path: instructions were compressed
		.text:00401D17  mov     edx, [ebp+0D5Dh] ; Fetch pointer to where decompressed instructions are stored

			.text:00402CC2  dd offset unk_42039C
	
		.text:00401AE5  mov     edx, [edx]
		.text:00401C93  test    edx, edx         ; Did we already decompress the instructions?
		.text:00401A3E  jnz     loc_40201C       ; Take the jump if we did

		; JZ path: instructions not already decompressed.
			.text:00401A1F  push    eax              ; Save pointer to compressed instructions
			.text:00401CDE  push    ecx              ; Save decompressed instructions length
			.text:00401E8A  mov     eax, [ebp+0D6Dh] ; Get length of x86 decompression code

				.text:00402CD2         dd 67Dh

			.text:00401B94  push    eax
			.text:00401B95  call    ALLOCATE_MEMORY  ; Allocate RWX memory to store decompression code
			.text:00401B9A  mov     edi, eax         ; Save decompression code memory pointer in EDI
			.text:00401C18  push    edi              ; Save decompression code memory pointer
			.text:00401D45  mov     esi, [ebp+0D61h] ; ESI := pointer to APLib decompression code

				.text:00402CC6         dd offset dword_40BE50

			.text:00401CA5  cld                        
			.text:00401FF9  mov     ecx, [ebp+0D6Dh] ; Get length of x86 decompression code

				.text:00402CD2         dd 67Dh

			.text:00401E54  push    ecx              ; Save length of x86 decompression code
			.text:00402064  rep movsb                ; Copy decompression code to newly-allocated memory
			.text:00401E41  pop     ecx              ; ECX := length of x86 decompression code
			.text:00401A86  pop     edi              ; EDI := allocated memory with decompression code
			.text:00401C2C  mov     eax, [ebp+0D7Dh] ; Load XOR encryption value
			
				.text:00402CE2 XOR_VALUE dd 2AAD591Dh
			
			.text:00401D7C  push    eax              ; Arg 3: XOR key
			.text:00401D7D  push    ecx              ; Arg 2: length
			.text:00401D7E  push    edi              ; Arg 1: pointer to decompression code
			.text:00401D7F  call    XorDecrypt       ; Decrypt the x86 decompression code copied into memory
			                                         ; See disassembly below (search for XorDecrypt)

			.text:00401CB9  pop     ecx              ; ecx := size of uncompressed instructions
			.text:00402046  pop     eax              ; eax := pointer to compressed instructions
			.text:00401F79  mov     esi, eax         ; esi := pointer to compressed instructions
			.text:00401FBE  push    ecx             
			.text:00401FBF  call    ALLOCATE_MEMORY  ; Allocate memory for uncompressed instructions
			.text:00401FC4  mov     edx, edi 
			.text:00401AD6  mov     edi, eax 
			.text:00401A4C  push    edi              ; Arg 2: pointer to decompressed output
			.text:00401A4D  push    esi              ; Arg 1: pointer to compressed input
			.text:00401A4E  call    edx              ; Decompress via APLib
			.text:00401A50  mov     eax, edi         ; eax := decompressed instructions
			.text:00401E31  mov     ecx, [ebp+0D5Dh] ; ecx := pointer to decompressed instructions

				.text:00402CC2  dd offset unk_42039C
	
			.text:00401E06  mov     [ecx], eax       ; Save decompressed instructions to pointer

	; MERGE AFTER DECOMPRESSING INSTRUCTIONS
	.text:0040201C  mov     ecx, [ebp+0D5Dh]     ; ecx := pointer to decompressed instructions
	.text:004020C2  mov     eax, [ecx]           ; eax := decompressed instructions
	.text:00401C6C  mov     [ebx+20h], eax       ; Store decompressed instructions * in VM Context

; MERGE AFTER INITIALIZING VM Context *
.text:00401FD7  mov     eax, [esp+24h]         ; Get the value pushed upon calling VM Entrypoint
.text:00401E74  call    FindInstructionByKey   ; Find the instruction with that key
                                               ; See decompilation below (Search for FindInstructionByKey)

.text:00401A98  mov     [ebx], eax             ; Save pointer to first instruction in VM Context
.text:00401B30  mov     eax, [esp]             ; eax := Get saved flags from stack
.text:00401C7D  mov     [esp+24h], eax         ; Overwrite VM entry key
.text:00402011  popf                           ; Restore flags
.text:00402084  popa                           ; Restore registers
.text:00401CCC  popf                           ; Restore flags again

; =======================================================
;                    HELPER FUNCTIONS
; =======================================================

Disassembly of GetVMContextThreadArray:

.text:00402A56  pusha
.text:00402A7B  call    $+5
.text:00402A80  pop     ebp
.text:00402A47  mov     eax, [ebp+23Eh] ; <- EBP is 00401F65

	.text:00402CBE  dd offset dword_420398 <- 

.text:00402A71  mov     eax, [eax]

	.data:00420398     dword_420398    dd 0			; DATA XREF: .text:00402CBEo

.text:00402A5E  mov     [esp+1Ch], eax ; <- replace EAX from -56 PUSHAD
.text:00402A87  popa
.text:00402A69  retn

Disassembly of SetVMContextThreadArray:

.text:00402ABB  pusha
.text:00402A98  call    $+5
.text:00402A9D  pop     ebp
.text:00402AC1  mov     eax, [ebp+221h] ; [0x00402CBE]

	.text:00402CBE  dd offset dword_420398

.text:00402AA5  mov     [eax], ecx
.text:00402AAF  popa
.text:00402AD2  retn

Disassembly of GetThreadIdx:

.text:00402601  pusha
.text:00402667  call    $+5
.text:0040266C  pop     ebp
.text:00402625  cmp     dword ptr [ebp+67Eh], 2	; [0x00402CEA]
.text:004025FA  jnz     short loc_40263B

; JNZ path: USER MODE
	.text:0040263B  mov     eax, large fs:24h ; thread ID
	@TRUNCATE_THREADID:
	.text:00402633  shr     eax, 2
	.text:00402652  mov     [esp+1Ch], eax
	.text:00402614  popa
	.text:0040265C  retn

; JZ path: KERNEL MODE
.text:0040261A  mov     ecx, [ebp+67Ah]

	.text:00402CE6  dd 0

.text:00402646  add     ecx, [ebp+672h]

	.text:00402CDE  dd 400000h ; BASE ADDRESS

.text:0040260A  call    dword ptr [ecx]
.text:0040260C  jmp     short loc_402633 ; @TRUNCATE_THREADID

Disassembly of XorDecrypt:

.text:00402530  pusha
.text:0040251C  mov     esi, [esp+24h]
.text:0040257B  mov     edx, [esp+2Ch]
.text:0040256C  mov     ecx, [esp+28h]
.text:0040255D  add     esi, 4
.text:0040253F  sub     ecx, 4
.text:00402548  shr     ecx, 2
@DECRYPT:
.text:00402565  xor     [esi], edx
.text:00402589  add     esi, 4 
.text:00402515  dec     ecx
.text:00402553  jnz     short loc_402565 ; @DECRYPT
.text:00402526  popa
.text:00402536  retn    0Ch

Disassembly of FindInstructionByKey:

.text:004025DB  pusha
.text:004025BC  mov     ebx, [ebx+20h]
.text:004025AE  sub     ebx, 18h
@ADD_CHECK:
.text:004025A5  add     ebx, 18h
.text:004025E2  cmp     [ebx], eax
.text:004025EB  jnz     short loc_4025A5 ; @ADD_CHECK

.text:004025D1  mov     [esp+1Ch], ebx
.text:00402599  popa
.text:004025C9  retn
	
Disassembly of AllocateMemory:

.text:004026DB  pusha
.text:0040292B  mov     edi, [esp+24h] ; 100000h
.text:0040283D  call    $+5
.text:00402842  pop     ebp
.text:0040272F  mov     esi, [ebp+49Ch] ; BASE ADDRESS

	.text:00402CDE  dd 400000h ; BASE ADDRESS

.text:00402773  cmp     dword ptr [ebp+4A8h], 2 ; [0x00402CEA]
.text:00402A2B  jnz     loc_40281D

; JNZ path: USER MODE
	.text:0040281D  add     esi, [ebp+4ACh]

		.text:00402CEE  dd 1050h

	.text:0040282C  mov     eax, [esi] ; VirtualAlloc
	.text:00402798  cmp     byte ptr [eax], 0B8h
	.text:0040295B  jz      short loc_40296E

	; JZ path -- goodbye sucker
		@ANTIDEBUG_DIE:
		.text:00402692  popa
		.text:00402880  rdtsc
		.text:0040278A  push    eax
		.text:00402A18  pop     esp
		.text:00402851  jmp     eax

	; JNZ path
		.text:004029F0  xor     ecx, ecx
		.text:0040273B  dec     ecx
		@INCREMENT_TRY_AGAIN:
		.text:004026EF  inc     ecx
		.text:004027BC  cmp     ecx, 0Ah
		.text:00402700  jz      loc_40294E
   	
		; JZ path
			.text:00402988  xor     eax, eax
			.text:004028D2  push    40h
			.text:004028D4  push    1000h
			.text:004028D9  push    edi
			.text:004028DA  push    eax
			.text:004028DB  call    dword ptr [esi]
			@RETURN_EAX:
			.text:004028FD  mov     [esp+1Ch], eax
			.text:0040293E  popa
			.text:004027AC  retn    4

		; JNZ path
		.text:00402752  mov     dl, [ecx+eax]
		.text:004029C0  xor     dl, 12h
		.text:0040290B  cmp     dl, 7Ah ; compare against 0x68
		.text:004028E6  jnz     loc_4026EF ; JNZ @INCREMENT_TRY_AGAIN
    	
		; JZ path
		.text:004027CE  mov     dh, [ecx+eax+5]
		.text:004027DA  xor     dh, 7Fh
		.text:004028AB  cmp     dh, 17h ; compare against 0x68
		.text:00402726  jnz     short loc_4026EF ; JNZ @INCREMENT_TRY_AGAIN
    	
		; JZ path
		.text:00402710  mov     dl, [ecx+eax+0Ah]
		.text:004028BF  xor     dl, 0BEh
		.text:0040297F  cmp     dl, 7Dh ; compare 0xc3
		.text:004029DF  jnz     loc_4026EF ; JNZ @INCREMENT_TRY_AGAIN
		.text:004029E5  jb      short j_ANTIDEBUG_DIE
		.text:004029E7  jnb     short j_ANTIDEBUG_DIE

; JZ path: KERNEL MODE
	.text:00402999  add     esi, [ebp+4ACh]

		.text:00402CEE  dd 1050h

	.text:0040286D  xor     ecx, ecx
	.text:00402A02  mov     edx, 656E6F4Eh ; 'None'
	.text:00402894  cmp     edi, 10001h
	.text:004029B1  sbb     eax, eax
	.text:004027FD  inc     eax
	.text:004026B6  push    edx
	.text:004026B7  push    edi
	.text:004026B8  push    eax
	.text:004026B9  call    dword ptr [esi]
	.text:004029D0  push    eax
	.text:00402764  mov     ecx, edi
	.text:00402864  shr     ecx, 2
	.text:004027EB  mov     edi, eax
	.text:004026A4  xor     eax, eax
	.text:0040280D  cld
	.text:00402681  rep stosd
	.text:00402744  pop     eax
	.text:00402919  jmp     short loc_4028FD ; @RETURN_EAX
