VMInstruction *Fetch(VMContext *thContext)
{
  memcpy(&thContext->Instruction,thContext->pCurrInsn, sizeof(VMInstruction));
  XorDecrypt(&thContext->Instruction, sizeof(VMInstruction), dwXorKey);
  return &thContext->Instruction;
}
