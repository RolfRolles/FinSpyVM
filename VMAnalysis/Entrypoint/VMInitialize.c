void Initialize()
{
  DWORD *dwGlobal   = GetVMContextThreadArray();
  DWORD dwThreadIdx = GetThreadIdx();
  VMContext *thContext = dwGlobal[dwThreadIdx];

  // Initialize pointers in thContext. This is pretty wasteful -- these 
  // pointers shouldn't be changing across VM exits. It would be faster to 
  // initialize them once in PreInitialize().
  thContext->pPICBase = (void *)0x00402131;
  // This is "label_VMEntry_after_preinitialization" from void VM()
  thContext->fpFastReEntry = (fpReEntryNoState)0x0040247C;
  thContext->fpLookupInstruction = &FindInstructionByKey;
  
  if(g_Mode == X86_USERMODE)
    thContext->fpEnterFunctionPointer = (fpReEntryHasState)0x00402B92;
  else
    thContext->fpEnterFunctionPointer = (fpReEntryHasState)0x00402BC6;
  
  thContext->fpExecuteVMInstruction = (fpReEnterToInstruction)0x00402C39;
  thContext->fpRelativeJump = (fpReEntryHasState)0x00402B74;
  thContext->fpNext = (fpReEntryHasState)0x00402B68;
  
  // These three lines are the only thing that changes across runs. Everything
  // else in this function should be in PreInitialize() (and perhaps the 
  // setting of the current instruction should be moved from there to here).
  thContext->pSavedEsp1 = ESP;
  thContext->pSavedEsp2 = ESP;
  ESP = thContext->pDataEnd;

  return thContext;
}
