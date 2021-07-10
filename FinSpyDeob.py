import idaapi
import idc

input_md5 = '4A49135D2ECC07085A8B7C5925A36C0A'

class deobX86Hook(idaapi.IDP_Hooks):
	def __init__(self):
		idaapi.IDP_Hooks.__init__(self)

	def ev_ana_insn(self, insn):
		b1 = idaapi.get_byte(insn.ea)
		if b1 >= 0x70 and b1 <= 0x7F:
			d1 = idaapi.get_byte(insn.ea+1)
			b2 = idaapi.get_byte(insn.ea+2)
			d2 = idaapi.get_byte(insn.ea+3)
			if b2 == b1 ^ 0x01 and d1-2 == d2:
				idaapi.put_byte(insn.ea, 0xEB)
				idaapi.put_word(insn.ea+2, 0x9090)
		
		elif b1 == 0x0F:
			b1_1 = idaapi.get_byte(insn.ea+1)
			d1   = idaapi.get_dword(insn.ea+2)
			b2   = idaapi.get_byte(insn.ea+6)
			b2_1 = idaapi.get_byte(insn.ea+7)
			d2   = idaapi.get_dword(insn.ea+8)
			if b2 == 0x0F and b1_1 ^ 0x01 == b2_1 and d1-6 == d2:
				idaapi.put_byte(insn.ea, 0xE9)
				idaapi.put_dword(insn.ea+1, d1+1)
				idaapi.put_byte(insn.ea+5, 0x90)
				idaapi.put_word(insn.ea+6, 0x9090)
				idaapi.put_dword(insn.ea+8, 0x90909090)
			
		return False

class deobx86_t(idaapi.plugin_t):
	flags = idaapi.PLUGIN_PROC | idaapi.PLUGIN_HIDE
	comment = "Deobfuscator"
	wanted_hotkey = ""
	help = "Runs transparently"
	wanted_name = "deobx86"
	hook = None

	def init(self):
		self.hook = None
		file_md5 = ''.join(['{0:02x}'.format(i).upper() for i in idc.retrieve_input_file_md5()])
		if file_md5 != input_md5 or idaapi.ph_get_id() != idaapi.PLFM_386:
			return idaapi.PLUGIN_SKIP
				
		self.hook = deobX86Hook()
		self.hook.hook()
		return idaapi.PLUGIN_KEEP

	def run(self, arg):
		pass

	def term(self):
		if self.hook:
			self.hook.unhook()

def PLUGIN_ENTRY():
	return deobx86_t()