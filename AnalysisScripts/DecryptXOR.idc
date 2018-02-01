static DecryptXOR(encAddr, encLen, xorVal)
{
  auto encNum;
  auto cursor;
  auto i;

  auto cursor;
  encNum = (encLen - 4) >> 2;
  cursor = encAddr + 4;
  
  
  for(i = 0; i < encNum; i = i + 1)
  {
    PatchDword(cursor,Dword(cursor)^xorVal);
    cursor = cursor + 4;
  }
}

// DecryptXor(0x40BE50, 0x67D, 0x2AAD591D);

