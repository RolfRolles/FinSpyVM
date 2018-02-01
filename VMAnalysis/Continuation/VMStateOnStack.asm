.text:00402BB2     mov     [esp-4], eax        ; Save VM initialization location from EAX onto stack
.text:00402BAB     popf                        ; Restore flags
.text:00402BBD     popa                        ; Restore registers
.text:00402B9C     jmp     dword ptr [esp-28h] ; Branch to VM initialization location
