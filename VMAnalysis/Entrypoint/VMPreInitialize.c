// VM Instruction structure
struct VMInstruction
{
  DWORD Key;
  unsigned char Opcode;
  unsigned char DataLen;
  unsigned char RVAFixup1;
  unsigned char RVAFixup2;
  unsigned char Data[16];
};

// 8 saved registers on the stack
struct SavedRegs
{
  DWORD Regs[8];
};

// Initially set to 0
DWORD *gp_VMContext_Thread_Array = NULL;
DWORD **gpp_VMContext_Thread_Array = &gp_VMContext_Thread_Array;

DWORD GetVMContextThreadArray()
{
  return *gpp_VMContext_Thread_Array;
}

void SetVMContextThreadArray(DWORD *pNew)
{
  *gpp_VMContext_Thread_Array = pNew;
}

DWORD GetThreadIdx()
{
  // If we're executing in user-mode...
  if(g_Mode == X86_USERMODE)
    return GetCurrentThreadId() >> 2;
  
  // Kernel-mode code has not been decompiled here: it relies upon an RVA 
  // that has been set to 0 in my sample, so can't be analyzed
}

void XorDecrypt(DWORD *Where, DWORD nByteLen, DWORD Key)
{
  // Skip first DWORD
  ++Where;
  for(int i = 0; i < (nByteLen-4)>>2; ++i)
    Where[i] ^= Key;
}

VMInstruction *FindInstructionByKey(VMContext *vmc, DWORD Key)
{
  VMInstruction *insns = vmc->pInstructions;
  while(insns->Key != Key)
    insns++;
  return insns;
}

// Function pointer archetype for decompression function
typedef void (__stdcall *fpDecompress)(void *input, void *output);

void VMPreInitialize(DWORD encodedVMEip)
{
  if(GetVMContextThreadArray() == NULL)
    SetVMContextThreadArray(Allocate(0x100000));

  DWORD *dwGlobal   = GetVMContextThreadArray();
  DWORD dwThreadIdx = GetThreadIdx();
  VMContext *thContext = dwGlobal[dwThreadIdx];
  if(thContext == NULL)
  {
    thContext = Allocate(0x10000);
    dwGlobal[dwThreadIdx] = thContext;

    // Base address for currently-running executable
    thContext->dwBaseAddress = g_BaseAddress;
    
    // Last DWORD in VM Context structure
    thContext->dwEnd = (DWORD)thContext + 0xFFFC;
    
    // Initialize pointer to data section
    thContext->pData = &thContext->Data;
    
    // If dwInstructionsDecompressedSize was 0, then the instructions aren't
    // compressed, so just copy the raw pointer to the instructions to the
    // pointer to the decompressed instructions
    if(dwInstructionsDecompressedSize == 0)
      dwInstructionsDecompressed = dwInstructionsCompressed;

    // If the decompressed size is not zero, this signifies that the 
    // instructions are compressed. Allocate that much memory, decompress the 
    // instruction data there, and then cache the decompression result 
    else
    {
      // If we've already decompressed the instructions, don't do it again
      if(*dwInstructionsDecompressed == NULL)
      {
        // Allocate RWX memory for the obfuscated, encrypted APLib decompression 
        // code
        void *pDecompressionStub = Allocate(dwDecompressionStubSize);
        memcpy(pDecompressionStub, dwDecompressionStubSize, &x86DecompressionStub);
        
        // Decrypt the decompression code (which is still obfuscated)
        XorDecrypt(pDecompressionStub, dwDecompressionStubSize, dwXorKey);
        
        // Allocate memory for decompressed instructions; decompress
        VMInstructions *pDecInsns = Allocate(dwInstructionsDecompressedSize);
        fpDecompress Decompress = (fpDecompress)pDecompressionStub;
        Decompress(*dwInstructionsCompressed, pDecInsns);
        
        // Update global pointer to hold decompressed instructions
        *dwInstructionsDecompressed = pDecInsns;
      }
    }
    // Store the pointer to decompressed instructions in the context structure
    thContext->pInstructions = *dwInstructionsDecompressed;
  }
  thContext->pCurrInsn = FindInstructionByKey(thContext, encodedVMEip);
}

void *Allocate(DWORD Size)
{
  // If we're executing in user-mode...
  if(g_Mode == X86_USERMODE)
  {
    // Get pointer to VirtualAlloc function within Kernel32
    unsigned char *pVirtualAlloc = &VirtualAlloc;
    
    // Is the first instruction "mov eax, dword"?
    if(*pVirtualAlloc == 0xB8)
    {
      // Cause an exception, terminate the program
      label_anti_debug_die:
      __asm
      {
        popa     ; Restore registers from function entry
        rdtsc    ; Get (random) timestamp counter in edx:eax
        push eax ; Push the low 32 bits
        pop esp  ; Pop into ESP
        jmp eax  ; Jump there
      }
    }
    // Check the first 10 bytes for this x86 sequence:
    //   push dword
    //   push dword
    //   ret
    // If it exists, trigger the code above to terminate the program
    for(int i = 0; i != 10; ++i)
    {
      if(
          (pVirtualAlloc[i]    == 0x68) && // Instruction at position i    is "push dword"
          (pVirtualAlloc[i+5]  == 0x68) && // Instruction at position i+5  is "push dword"
          (pVirtualAlloc[i+10] == 0xC3)    // Instruction at position i+10 is "ret"
        )
      goto label_anti_debug_die;
    }
    
    // Finally, allocate the memory and return
    return VirtualAlloc(NULL, Size, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
  }
  
  // Else, if we're executing in kernel-mode...
  void *retVal = ExAllocatePoolWithTag(Size <= 0x10001 ? NonPagedPoolExecute : NonPagedPool, Size, 'enoN');
  memset(retVal, 0, Size);
  return retVal;
}

