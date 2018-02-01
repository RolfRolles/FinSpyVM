import random
from Pandemic.X86.X86 import *
from Pandemic.X86.X86InternalOperand import *
from Pandemic.X86.X86InternalOperandDescriptions import *
from Pandemic.X86.X86EncodeTable import mnem_to_encodings
from Pandemic.Util.Visitor import Visitor2

# Random booleans, register numbers, scales, and constants.
def rnd_bool():  return random.getrandbits(1)  #: Random boolean
def rnd_regno(): return random.getrandbits(3)  #: Random register number
def rnd_scale(): return random.getrandbits(2)  #: Random scale factor
def rnd_byte():  return random.getrandbits(8)  #: Random byte
def rnd_word():  return random.getrandbits(16) #: Random word
def rnd_dword(): return random.getrandbits(32) #: Random dword

# Random segments and 32-bit registers (as enums, not X86 types).
def rnd_seg():         return random.choice(SegList) #: Random segment
def rnd_reg32():       return random.choice(R32List) #: Random 32-bit register
def rnd_reg32_noesp(): return random.choice([Eax,Ecx,Edx,Ebx,Ebp,Esi,Edi]) 
#: Random 32-bit register (no ``ESP``)

modrm_16 = [(Bx,Si),(Bx,Di),(Bp,Si),(Bp,Di),(Si,None),(Di,None),(Bp,None),(Bx,None)]

# Given an abstract operand type and a triple of booleans describing desired
# operand generation behavior, this class' gen method shall return a legal
# operand allowed by the abstract operand type.
class X86RandomOperand(Visitor2):

	# This is the top-level interface.  Clients should call this function to 
	# create a random operand.
	# aop:  abstract operand type (X86InternalOperand.py)
	# m:  when an operand can be a register or memory, should we use memory?
	# s:  size-override flag
	# a:  address-override flag
	def gen(self,aop,(m,s,a)):
		return self.visit(AOTtoAOTDL[aop.IntValue()],(m,s,a))

	# This method examines the abstract operand encoding and routes the method
	# invokation to the proper location.
	def MakeMethodName(s,enc,op2):

		# We divide the ImmediateEncs by the types of their archetype objects.
		if isinstance(enc,ImmEnc):
			op = enc.archetype
			if isinstance(op,MemExpr):   return "visit_Immediate_MemExpr"
			if isinstance(op,FarTarget): return "visit_Immediate_FarTarget"
			return "visit_Immediate_%s" % op.__class__.__name__

		# Special-case SignExtImm with a JccTarget archetype to use the same logic
		# as ImmediateEnc's JccTarget.  Otherwise, use the archetype class name.
		elif isinstance(enc,SignedImm):
			op = enc.archetype
			if isinstance(op,JccTarget): return "visit_Immediate_JccTarget"
			return "visit_SignExtImm_%s" % op.__class__.__name__

		# We have to special-case SegReg, since there are only 6 segment registers.
		# We unify the logic for all other register types, as there are 8 possible
		# registers for each other register type.
		elif isinstance(enc,GPart):
			op = enc.archetype
			if isinstance(op,SegReg):    return "visit_GPart_SegReg"

		# Otherwise, use a generic name.
		return "visit_" + enc.__class__.__name__
	
	# Use the boolean "p" to decide whether to visit "yes" or "no".
	# Used to implement AddrPrefix and SizePrefix.
	def visit_Prefixed(s,yes,no,p,flags):
		return s.visit(yes,flags) if p else s.visit(no,flags)
	
	# Call visit_Prefixed using the address-override boolean a
	def visit_AddrPrefix(self,addr,(m,s,a)):
		return self.visit_Prefixed(addr.yes,addr.no,a,(m,s,a))

	# Call visit_Prefixed using the size-override boolean s
	def visit_SizePrefix(self,size,(m,s,a)):
		return self.visit_Prefixed(size.yes,size.no,s,(m,s,a))

	# To "randomly generate" implicit operands, return them directly.
	def visit_Exact(self,i,(m,s,a)):
		return i.value
	
	# For implicit operands that may have their segments overridden, make a copy
	# of the operand and put a random segment into it.
	def visit_ExactSeg(self,i,(m,s,a)):
		return i.value(rnd_seg())

	# Generate a random register of the same type as the archetype.
	def visit_GPart(self,g,(m,s,a)):
		return g.archetype(rnd_regno())
	
	# We have to special-case GPart segment registers, since there are only
	# six of them (whereas the previous method is for register families with
	# 8 elements in them).
	def visit_GPart_SegReg(self,g,(m,s,a)):
		return SegReg(rnd_seg())

	# Depending on the "m" flag and whether a memory location is permissible,
	# generate a Mem16 or Mem32 depending upon the address-override flag a.
	# Otherwise, generate a register randomly.
	def visit_RegOrMem(self,mrm,(m,s,a)):

		# If a memory is uncalled for, or impossible, return a register with the
		# same type as the ModRM's register archetype.
		if (not m or mrm.mem is None) and mrm.reg is not None:
			return mrm.reg(rnd_regno())

		# Otherwise, return a memory whose access size is 'size'.
		size = mrm.mem

		# Helper function to generate a random displacement (either None, an 
		# 8-bit signed value, or a 16/32-bit value).  choose_none determines
		# whether it is acceptable to return None.
		def rnd_displ(choose_none,mask):
			i = random.randint(0 if choose_none else 1,2)
			if i == 0: return None
			if i == 1: return mask&(127-random.randint(0,255))
			if i == 2: return random.randint(0,mask)

		# If a is True, generate a Mem16 object
		if a:
			# Randomly generate the Mem16's base, index, and displacement.
			b,i = random.choice(modrm_16) if rnd_bool() else (None,None)
			return Mem16(rnd_seg(),size,b,i,rnd_displ(b is not None,0xFFFF))

		# If a is False, generate a Mem32 object
		else:
			# Randomly generate the Mem32's base, index, and displacement, 
			# ensuring that at least one part is chosen.
			b     = rnd_reg32() if rnd_bool() else None
			sr,sf = (rnd_reg32_noesp(),rnd_scale()) if rnd_bool() else (None,0)
			d     = rnd_displ(not (b == None and sr == None),0xFFFFFFFF)
			return Mem32(rnd_seg(),size,b,sr,sf,d)
				
	# For Immediate memory expressions, generate a MemExpr with only a 
	# displacement, of the proper memory size depending upon the a flag.
	def visit_Immediate_MemExpr(self,i,(m,s,a)):
		rndseg = rnd_seg()
		if a: return Mem16(rndseg,i.archetype.size,None,None,rnd_word())
		else: return Mem32(rndseg,i.archetype.size,None,None,0,rnd_dword())

	# For Immediate far targets, generate a FarTarget with a random segment, and
	# and a random offset of the proper size (depending upon the a flag).
	def visit_Immediate_FarTarget(self,i,(m,s,a)):
		if a: return AP16(rnd_word(),rnd_word())
		else: return AP32(rnd_word(),rnd_dword())
	
	# For an Immediate JccTarget, generate a random address to target.
	def visit_Immediate_JccTarget(self,i,(m,s,a)):
		d = rnd_dword()
		return JccTarget(d & 0xFFFF if a else d,rnd_dword())

	# For Immediate constants, generate random constants.
	def visit_Immediate_Id(self,i,(m,s,a)): return Id(rnd_dword())
	def visit_Immediate_Iw(self,i,(m,s,a)): return Iw(rnd_word())
	def visit_Immediate_Ib(self,i,(m,s,a)): return Ib(rnd_byte())
	
	# For sign-extended immediates, generate a constant in the proper range.
	def visit_SignExtImm_Common(self,mask):
		x = random.randint(0,0x7F)
		return x if rnd_bool else ~x & mask
		
	# Return an Iw of a suitable constant.
	def visit_SignExtImm_Iw(self,i,(m,s,a)):
		return Iw(self.visit_SignExtImm_Common(0xFFFF))

	# Return an Id of a suitable constant.
	def visit_SignExtImm_Id(self,i,(m,s,a)):
		return Id(self.visit_SignExtImm_Common(0xFFFFFFFF))
	
# X86 mnemonics
x86_mnem_arr = [Aaa,Aad,Aam,Aas,Adc,Add,Addpd,Addps,Addsd ,Addss,Addsubpd ,
Addsubps,And,Andnpd,Andnps,Andpd,Andps,Arpl ,Blendpd,Blendps,Blendvpd,Blendvps ,
Bound,Bsf,Bsr,Bswap,Bt,Btc ,Btr,Bts,CallF,Cbw,Cdq,Clc,Cld,Clflush,Cli ,
Clts,Cmc,Cmova ,Cmovae,Cmovb,Cmovbe,Cmovg,Cmovge,Cmovl,Cmovle,Cmovno,Cmovnp,
Cmovns,Cmovnz,Cmovo,Cmovp,Cmovs,Cmovz,Cmp,Cmppd,Cmpps,Cmpsb ,Cmpsd,Cmpss ,
Cmpsw,Cmpxchg,Cmpxchg8b,Comisd,Comiss,Cpuid,Crc32 ,Cvtdq2pd,Cvtdq2ps,Cvtpd2dq ,
Cvtpd2pi,Cvtpd2ps,Cvtpi2pd,Cvtpi2ps ,Cvtps2dq,Cvtps2pd,Cvtps2pi,Cvtsd2si,Cvtsd2ss ,
Cvtsi2sd,Cvtsi2ss ,Cvtss2sd,Cvtss2si,Cvttpd2dq,Cvttpd2pi,Cvttps2dq,Cvttps2pi ,
Cvttsd2si, Cvttss2si,Cwd,Cwde,Daa,Das,Dec,Div,Divpd,Divps,Divsd,Divss, Dppd ,
Dpps,Emms,Enter,Extractps,F2xm1,Fabs,Fadd,Faddp,Fbld ,Fbstp,Fchs,Fclex,Fcmovb,
Fcmovbe,Fcmove,Fcmovnb,Fcmovnbe,Fcmovne, Fcmovnu,Fcmovu,Fcom,Fcomi,Fcomip,Fcomp,
Fcompp,Fcos,Fdecstp ,Fdiv,Fdivp,Fdivr,Fdivrp,Ffree,Fiadd,Ficom,Ficomp,Fidiv ,
Fidivr, Fild,Fimul,Fincstp,Finit,Fist,Fistp,Fisttp,Fisub,Fisubr,Fld, Fld1,Fldcw,
Fldenv,Fldl2e,Fldl2t,Fldlg2,Fldln2,Fldpi,Fldz ,Fmul,Fmulp,Fnop,Fpatan,Fprem ,
Fprem1,Fptan,Frndint,Frstor,Fsave, Fscale,Fsin,Fsincos,Fsqrt,Fst,Fstcw,Fstenv ,
Fstp,Fstsw,Fsub ,Fsubp,Fsubr,Fsubrp,Ftst,Fucom,Fucomi,Fucomip,Fucomp,Fucompp,
Fxam,Fxch,Fxrstor,Fxsave,Fxtract,Fyl2x,Fyl2xp1,Getsec,Haddpd ,Haddps,Hlt,Hsubpd,
Hsubps,Icebp,Idiv,Imul,In,Inc,Insb,Insd ,Insertps,Insw,Int,Int3,Into,Invd,
Invlpg,Iretd,Iretw,JmpF ,Lahf,Lar,Lddqu,Ldmxcsr,Lds,Lea,
Leave,Les,Lfence ,Lfs,Lgdt ,Lgs,Lidt,Lldt,Lmsw,Lodsb,Lodsd,Lodsw,Lsl,Lss,Ltr,Maskmovdqu,
Maskmovq,Maxpd,Maxps,Maxsd,Maxss,Mfence,Minpd,Minps,Minsd ,Minss,Monitor,Mov ,
Movapd,Movaps,Movd,Movddup,Movdq2q,Movdqa ,Movdqu,Movhlps,Movhpd,Movhps,Movlhps ,
Movlpd,Movlps,Movmskpd ,Movmskps,Movntdq,Movntdqa,Movnti,Movntpd,Movntps,Movntq ,
Movq ,Movq2dq,Movsb,Movsd,Movshdup,Movsldup,Movss,Movsw,Movsx,Movupd ,Movups,Movzx, 
Mpsadbw,Mul,Mulpd,Mulps,Mulsd,Mulss,Mwait,Neg ,Nop,Not,Or,Orpd,Orps,Out ,
Outsb,Outsd,Outsw,Pabsb,Pabsd ,Pabsw,Packssdw,Packsswb,Packusdw,Packuswb,Paddb ,
Paddd,Paddq ,Paddsb,Paddsw,Paddusb,Paddusw,Paddw,Palignr,Pand,Pandn,Pause ,Pavgb ,
Pavgw,Pblendvb,Pblendw,Pcmpeqb,Pcmpeqd,Pcmpeqq,Pcmpeqw ,Pcmpestri,Pcmpestrm,Pcmpgtb, 
Pcmpgtd,Pcmpgtq,Pcmpgtw,Pcmpistri ,Pcmpistrm,Pextrb,Pextrd,Pextrw,Phaddd,Phaddsw ,
Phaddw,Phminposuw ,Phsubd,Phsubsw,Phsubw,Pinsrb,Pinsrd,Pinsrw,Pmaddubsw,Pmaddwd,
Pmaxsb,Pmaxsd,Pmaxsw,Pmaxub,Pmaxud,Pmaxuw,Pminsb,Pminsd,Pminsw ,Pminub,Pminud ,
Pminuw,Pmovmskb,Pmovsxbd,Pmovsxbq,Pmovsxbw,Pmovsxdq, Pmovsxwd,Pmovsxwq,Pmovzxbd ,
Pmovzxbq,Pmovzxbw,Pmovzxdq,Pmovzxwd ,Pmovzxwq,Pmuldq,Pmulhrsw,Pmulhuw,Pmulhw,Pmulld, 
Pmullw,Pmuludq ,Pop,Popad,Popaw,Popcnt,Popfd,Popfw,Por,Prefetchnta,Prefetcht0,
Prefetcht1,Prefetcht2,Psadbw,Pshufb,Pshufd,Pshufhw,Pshuflw,Pshufw, Psignb,Psignd ,
Psignw,Pslld,Pslldq,Psllq,Psllw,Psrad,Psraw ,Psrld,Psrldq,Psrlq,Psrlw,Psubb ,
Psubd,Psubq,Psubsb,Psubsw ,Psubusb,Psubusw,Psubw,Ptest,Punpckhbw,Punpckhdq ,
Punpckhqdq ,Punpckhwd,Punpcklbw,Punpckldq,Punpcklqdq,Punpcklwd,Push,Pushad ,Pushaw ,
Pushfd,Pushfw,Pxor,Rcl,Rcpps,Rcpss,Rcr,Rdmsr,Rdpmc ,Rdtsc,Ret,Retf,Rol,Ror ,
Roundpd,Roundps,Roundsd,Roundss,Rsm ,Rsqrtps,Rsqrtss,Sahf,Sal,Salc,Sar,Sbb ,
Scasb,Scasd,Scasw,Seta, Setae,Setb,Setbe,Setg,Setge,Setl,Setle,Setno,Setnp ,
Setns ,Setnz,Seto,Setp,Sets,Setz,Sfence,Sgdt,Shl,Shld,Shr,Shrd ,Shufpd,Shufps, 
Sidt,Sldt,Smsw,Sqrtpd,Sqrtps,Sqrtsd,Sqrtss,Stc ,Std,Sti,Stmxcsr,Stosb,Stosd, 
Stosw,Str,Sub,Subpd,Subps,Subsd, Subss,Syscall,Sysenter,Sysexit,Sysret,Test ,
Ucomisd,Ucomiss,Ud2, Unpckhpd,Unpckhps,Unpcklpd,Unpcklps,Verr,Verw,Vmcall,Vmclear,
Vmlaunch,Vmptrld,Vmptrst,Vmread,Vmresume,Vmwrite,Vmxoff,Vmxon ,Wait,Wbinvd,Wrmsr,Xadd,Xlat,
Xchg,Xor,Xorpd,Xorps]  

# 1) Get a random mnemonic. 
# 2) Look it up in the encoding table.  
# 3) Get a random encoding.
# 4) Make random operands of those types.
# 5) Return the instruction.
def generate_random_instruction(excl=(lambda x: False)):	
	mnem = random.choice(x86_mnem_arr)
	while excl(mnem):
		mnem = random.choice(x86_mnem_arr)
	
	encs = mnem_to_encodings[mnem.IntValue()]
	enc = random.choice(encs)
	mem,so,ao = rnd_bool(),rnd_bool(),rnd_bool()
	rog = X86RandomOperand()
	reified_ops = map(lambda o: rog.gen(o,(mem,so,ao)),enc.ops)
	return Instruction([],mnem,*tuple(reified_ops)) 
