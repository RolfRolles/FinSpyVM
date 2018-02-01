from kbp.comp.aplib import decompress

with open("compressed.bin", "rb") as g:
	dec,decSize = decompress(g.read()).do()
	print decSize
with open("decompressed.bin", "wb") as f:
	f.write(dec)
