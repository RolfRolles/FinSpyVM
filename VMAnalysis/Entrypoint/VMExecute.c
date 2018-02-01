typedef void (__stdcall *fpInstruction)(VMContext *);

void VMExecute(VMContext *vmc)
{
  // Locate the handler table in the .text section
  fpInstruction *handlers = (fpInstruction *)vmc->pPICBase + 0x9AF;
  
  // Invoke the relevant function in the handler table
  handlers[i->Opcode](vmc);
}