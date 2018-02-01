void Decode(VMContext *thContext)
{
  VMInstruction *ins = &thContext->Instruction;
  if(ins->Fixup1)
    *(DWORD *)&ins->Data[ins->Fixup1 & 0x7F] += thContext->dwImageBase;
  if(ins->Fixup2)
    *(DWORD *)&ins->Data[ins->Fixup2 & 0x7F] += thContext->dwImageBase;
}
