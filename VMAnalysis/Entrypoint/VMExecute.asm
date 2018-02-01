.text:00402311         movzx   ecx, byte ptr [ebx+3Ch]      ; ECX := Opcode field from the VMInstruction in the VM Context *
.text:0040248D         mov     eax, [ebx+24h]               ; EAX := PIC base saved in VMContext *
.text:004023FC         add     eax, 9AFh                    ; EAX := VM handler array (code pointer table)
.text:0040218C         jmp     dword ptr [eax+ecx*4]        ; Jump to instruction begin
