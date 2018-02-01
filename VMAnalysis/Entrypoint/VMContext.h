struct VMInstruction;
struct VMContext;

// Function pointer archetypes
typedef void (__stdcall *fpReEntryNoState)(void);
typedef void (__stdcall *fpReEntryHasState)(DWORD, SavedRegs);
typedef void (__stdcall *fpReEntryToInstruction)(DWORD, SavedRegs, VMInstruction *);
typedef VMInstruction *(__stdcall *fpLookupInstruction)(VMContext *, DWORD);

struct VMContext
{
  // Current instruction pointer
  VMInstruction *pCurrInsn;
  
  // Pointer to VMContext data area
  DWORD *pX86Stack;
  
  // An extra DWORD (register) available to the VM instructions
  DWORD dwScratch;

  //
  // VM RE-ENTRY MECHANISMS
  //
  
  // This VM entrypoint takes no stack or register arguments
  fpReEntryNoState  fpFastReEntry; 
  
  // This VM entrypoint assumes that:
  // * The saved flags and registers are at the bottom of the stack
  // * EAX has a function pointer
  // It restores the flags/registers and jumps to the function pointer
  fpReEntryHasState fpEnterFunctionPointer;
  
  // This VM entrypoint assumes that:
  // * The saved flags and registers are at the bottom of the stack
  // * Above that on the stack is a VMInstruction * (next insn to execute)
  // * EBX contains a pointer to the VMContext *
  // It executes by:
  // * Copying the VMInstruction * into VMContext->pCurrInsn 
  // * Jumping to fpEnterFunctionPointer
  fpReEntryToInstruction fpExecuteVMInstruction;

  // This VM entrypoint assumes that:
  // * The saved flags and registers are at the bottom of the stack
  // * EBX contains a pointer to the VMContext *
  // * ECX points to the data area of a VMInstruction *
  // It executes by:
  // * If DWORD insnData[1] is non-zero, add it to VMContext->pCurrInsn
  // * Else, treat insnData[5] as an RVA and jump there
  fpReEntryHasState fpRelativeJump;
  
  // This VM entrypoint assumes that:
  // * The saved flags and registers are at the bottom of the stack
  // * EBX contains a pointer to the VMContext *
  // It executes by:
  // * Adding sizeof(VMInstruction) to VMContext->pCurrInsn
  // * Else, treat insnData[5] as an RVA and jump there
  fpReEntryHasState fpNext;
  
  //
  // VM State
  //
  
  // Pointer to decompressed instruction array.
  VMInstructions *pInstructions;
  
  // A pointer somewhere in the .text section
  // (Used to locate the handler function pointer table via displacement)
  void *pPICBase;
  
  // Base address of the parent executable in memory
  DWORD dwBaseAddress;
  
  // Two copies of the value of ESP from VM entry
  DWORD *pSavedEsp1;
  DWORD *pSavedEsp2;
  
  // Points to FindInstructionByKey function
  fpLookupInstruction fpLookupInsn;
  
  // Copy of current instruction (not a pointer)
  VMInstruction Instruction;
  
  // Pointer to beginning of data area, used as dynamically-generated code stack
  DWORD *pDynamicCodeStack;
  
  // An array of data, used as both an X86 and a VM stack
  DWORD Data[0x3FEB];
};