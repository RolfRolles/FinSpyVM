"""This module defines the classes for the Abstract Operand Type Description
Language, all of which derive from :class:`X86AOTDL`.  Additionally, the list
:data:`AOTtoAOTDL` contains one :class:`X86AOTDL` object for each 
:class:`.AOTElt` abstract operand type."""

from X86 import *
from X86InternalOperand import *

# AOTDL:  Abstract Operand Type Description Language
class X86AOTDL(object): 
	"""Base class for all AOTDL elements."""
	pass

class Exact(X86AOTDL):
	"""AOTDL element that specifies an :class:`.Operand` exactly.
	
	:ivar `.Operand` value: the precise operand specified
	"""
	def __init__(s,v): s.value = v

class ExactSeg(X86AOTDL): 
	"""AOTDL element that specifies a :class:`.Mem16` or :class:`.Mem32` exactly,
	where the segment is allowed to differ.
	
	:ivar `.MemExpr` value: the precise operand specified
	"""
	def __init__(s,v): s.value = v

class GPart(X86AOTDL):
	"""AOTDL element that specifies any :class:`.Register` within some family
	(i.e., some class derived from :class:`.Register`).
	
	:ivar `.Register` archetype: the register family specified
	"""
	def __init__(s,a): s.archetype = a

class RegOrMem(X86AOTDL):
	"""AOTDL element that specifies either any :class:`.Register` from some 
	family, or a memory expression specified by access size.  Either component
	may be illegal; in which case, the corresponding member is ``None``.
	
	:ivar `.Register` reg: the register family specified, or ``None``
	:ivar `.MSElt` mem: the memory access size, or ``None``
	"""
	def __init__(s,reg,mem): s.reg,s.mem = reg,mem

class ImmEnc(X86AOTDL): 
	"""AOTDL element that specifies an operand that is encoded as an immediate.
	Its *archetype* field may specify:
	
	* An :class:`.Immediate` operand
	* A :class:`.MemExpr`, which is not permitted to use base or index registers
	* A :class:`.JccTarget`
	* A :class:`.FarTarget`
	
	:ivar `.Operand` archetype: the type of operand described by this AOTDL
	"""
	def __init__(s,a): s.archetype = a

class SignedImm(X86AOTDL): 
	"""AOTDL element that specifies an operand that is encoded as an 8-bit 
	immediate, which is interpreted as a larger value.  Its *archetype* field may
	specify:
	
	* An :class:`.Immediate` operand
	* A :class:`.JccTarget`
	
	:ivar `.Operand` archetype: the type of operand described by this AOTDL
	"""
	def __init__(s,a): s.archetype = a

class SizePrefix(X86AOTDL):
	"""AOTDL element that differs depending upon the operand size prefix.
	
	:ivar `.X86AOTDL` yes: if the prefix is present
	:ivar `.X86AOTDL` no: if the prefix is absent
	"""
	def __init__(s,yes,no): s.yes,s.no = yes,no

class AddrPrefix(X86AOTDL): 
	"""AOTDL element that differs depending upon the address size prefix.
	
	:ivar `.X86AOTDL` yes: if the prefix is present
	:ivar `.X86AOTDL` no: if the prefix is absent
	"""
	def __init__(s,yes,no): s.yes,s.no = yes,no

AOTtoAOTDL = [None]*(X86_INTERNAL_OPERAND_LAST+1)

def v(o): return o.IntValue()

AOTtoAOTDL[v(OAL    )] = Exact(Gb(Al))
AOTtoAOTDL[v(OALR8L )] = Exact(Gb(Al))
AOTtoAOTDL[v(OCL    )] = Exact(Gb(Cl))
AOTtoAOTDL[v(OCLR9L )] = Exact(Gb(Cl))
AOTtoAOTDL[v(ODLR10L)] = Exact(Gb(Dl))
AOTtoAOTDL[v(OBLR11L)] = Exact(Gb(Bl))
AOTtoAOTDL[v(OAHR12L)] = Exact(Gb(Ah))
AOTtoAOTDL[v(OCHR13L)] = Exact(Gb(Ch))
AOTtoAOTDL[v(ODHR14L)] = Exact(Gb(Dh))
AOTtoAOTDL[v(OBHR15L)] = Exact(Gb(Bh))
AOTtoAOTDL[v(OAX    )] = Exact(Gw(Ax))
AOTtoAOTDL[v(ODX    )] = Exact(Gw(Dx))
AOTtoAOTDL[v(OCS    )] = Exact(SegReg(CS))
AOTtoAOTDL[v(ODS    )] = Exact(SegReg(DS))
AOTtoAOTDL[v(OES    )] = Exact(SegReg(ES))
AOTtoAOTDL[v(OGS    )] = Exact(SegReg(GS))
AOTtoAOTDL[v(OFS    )] = Exact(SegReg(FS))
AOTtoAOTDL[v(OSS    )] = Exact(SegReg(SS))
AOTtoAOTDL[v(O1     )] = Exact(Ib(1l))
AOTtoAOTDL[v(OSt0   )] = Exact(FPUReg(ST0))
AOTtoAOTDL[v(OeAX   )] = SizePrefix(Exact(Gw(Ax)),Exact(Gd(Eax)))
AOTtoAOTDL[v(OrAXr8 )] = SizePrefix(Exact(Gw(Ax)),Exact(Gd(Eax)))
AOTtoAOTDL[v(OrAX   )] = SizePrefix(Exact(Gw(Ax)),Exact(Gd(Eax)))
AOTtoAOTDL[v(OeCX   )] = SizePrefix(Exact(Gw(Cx)),Exact(Gd(Ecx)))
AOTtoAOTDL[v(OrCXr9 )] = SizePrefix(Exact(Gw(Cx)),Exact(Gd(Ecx)))
AOTtoAOTDL[v(OeDX   )] = SizePrefix(Exact(Gw(Dx)),Exact(Gd(Edx)))
AOTtoAOTDL[v(OrDXr10)] = SizePrefix(Exact(Gw(Dx)),Exact(Gd(Edx)))
AOTtoAOTDL[v(OeBX   )] = SizePrefix(Exact(Gw(Bx)),Exact(Gd(Ebx)))
AOTtoAOTDL[v(OrBXr11)] = SizePrefix(Exact(Gw(Bx)),Exact(Gd(Ebx)))
AOTtoAOTDL[v(OeSP   )] = SizePrefix(Exact(Gw(Sp)),Exact(Gd(Esp)))
AOTtoAOTDL[v(OrSPr12)] = SizePrefix(Exact(Gw(Sp)),Exact(Gd(Esp)))
AOTtoAOTDL[v(OeBP   )] = SizePrefix(Exact(Gw(Bp)),Exact(Gd(Ebp)))
AOTtoAOTDL[v(OrBPr13)] = SizePrefix(Exact(Gw(Bp)),Exact(Gd(Ebp)))
AOTtoAOTDL[v(OeSI   )] = SizePrefix(Exact(Gw(Si)),Exact(Gd(Esi)))
AOTtoAOTDL[v(OrSIr14)] = SizePrefix(Exact(Gw(Si)),Exact(Gd(Esi)))
AOTtoAOTDL[v(OeDI   )] = SizePrefix(Exact(Gw(Di)),Exact(Gd(Edi)))
AOTtoAOTDL[v(OrDIr15)] = SizePrefix(Exact(Gw(Di)),Exact(Gd(Edi)))

AOTtoAOTDL[v(OMbBx  )] = AddrPrefix(ExactSeg(Mem16(DS,Mb,Bx,None,None)),ExactSeg(Mem32(DS,Mb,Ebx,None,0,None)))
AOTtoAOTDL[v(OMbEbx )] = AddrPrefix(ExactSeg(Mem16(DS,Mb,Bx,None,None)),ExactSeg(Mem32(DS,Mb,Ebx,None,0,None)))

ayb = AddrPrefix(Exact(Mem16(ES,Mb,Di,None,None)),Exact(Mem32(ES,Mb,Edi,None,0,None)))
ayw = AddrPrefix(Exact(Mem16(ES,Mw,Di,None,None)),Exact(Mem32(ES,Mw,Edi,None,0,None)))
ayd = AddrPrefix(Exact(Mem16(ES,Md,Di,None,None)),Exact(Mem32(ES,Md,Edi,None,0,None)))

# Inflexible segments
AOTtoAOTDL[v(OYb    )] = ayb
AOTtoAOTDL[v(OYw    )] = ayw
AOTtoAOTDL[v(OYd    )] = ayd
AOTtoAOTDL[v(OYv    )] = SizePrefix(ayw,ayd)
AOTtoAOTDL[v(OYz    )] = SizePrefix(ayw,ayd)

axb = AddrPrefix(ExactSeg(Mem16(DS,Mb,Si,None,None)),ExactSeg(Mem32(DS,Mb,Esi,None,0,None)))
axw = AddrPrefix(ExactSeg(Mem16(DS,Mw,Si,None,None)),ExactSeg(Mem32(DS,Mw,Esi,None,0,None)))
axd = AddrPrefix(ExactSeg(Mem16(DS,Md,Si,None,None)),ExactSeg(Mem32(DS,Md,Esi,None,0,None)))

AOTtoAOTDL[v(OXb    )] = axb
AOTtoAOTDL[v(OXw    )] = axw
AOTtoAOTDL[v(OXd    )] = axd
AOTtoAOTDL[v(OXv    )] = SizePrefix(axw,axd)
AOTtoAOTDL[v(OXz    )] = SizePrefix(axw,axd)

AOTtoAOTDL[v(OIb    )] = ImmEnc(Ib(0l))
AOTtoAOTDL[v(OIw    )] = ImmEnc(Iw(0l))
AOTtoAOTDL[v(OOb    )] = ImmEnc(MemExpr(DS,Mb))
AOTtoAOTDL[v(OJz    )] = ImmEnc(JccTarget(0,0))
AOTtoAOTDL[v(OIv    )] = SizePrefix(ImmEnc(Iw(0l)),ImmEnc(Id(0l)))
AOTtoAOTDL[v(OIz    )] = SizePrefix(ImmEnc(Iw(0l)),ImmEnc(Id(0l)))
AOTtoAOTDL[v(OOv    )] = SizePrefix(ImmEnc(MemExpr(DS,Mw)),ImmEnc(MemExpr(DS,Md)))
AOTtoAOTDL[v(OAp    )] = AddrPrefix(ImmEnc(AP16(0,0)),ImmEnc(AP32(0,0)))

AOTtoAOTDL[v(OJb    )] = SignedImm(JccTarget(0,0))
AOTtoAOTDL[v(OIbv   )] = SizePrefix(SignedImm(Iw(0l)),SignedImm(Id(0l)))

AOTtoAOTDL[v(OGb    )] = GPart(Gb(Al))
AOTtoAOTDL[v(OGw    )] = GPart(Gw(Ax))
AOTtoAOTDL[v(OGd    )] = GPart(Gd(Eax))
AOTtoAOTDL[v(OGd_q  )] = GPart(Gd(Eax))
AOTtoAOTDL[v(OSw    )] = GPart(SegReg(CS))
AOTtoAOTDL[v(OCd    )] = GPart(ControlReg(CR0))
AOTtoAOTDL[v(ODd    )] = GPart(DebugReg  (DR0))
AOTtoAOTDL[v(OPd    )] = GPart(MMXReg(MM0))
AOTtoAOTDL[v(OPq    )] = GPart(MMXReg(MM0))
AOTtoAOTDL[v(OPpi   )] = GPart(MMXReg(MM0))
AOTtoAOTDL[v(OVdq   )] = GPart(XMMReg(XMM0))
AOTtoAOTDL[v(OVpd   )] = GPart(XMMReg(XMM0))
AOTtoAOTDL[v(OVps   )] = GPart(XMMReg(XMM0))
AOTtoAOTDL[v(OVsd   )] = GPart(XMMReg(XMM0))
AOTtoAOTDL[v(OVss   )] = GPart(XMMReg(XMM0))
AOTtoAOTDL[v(OVq    )] = GPart(XMMReg(XMM0))
AOTtoAOTDL[v(OGv    )] = SizePrefix(GPart(Gw(Ax)),GPart(Gd(Eax)))
AOTtoAOTDL[v(OGz    )] = SizePrefix(GPart(Gw(Ax)),GPart(Gd(Eax)))

AOTtoAOTDL[v(OEb    )] = RegOrMem(Gb(Al), Mb)
AOTtoAOTDL[v(OEw    )] = RegOrMem(Gw(Ax), Mw)
AOTtoAOTDL[v(OEd    )] = RegOrMem(Gd(Eax),Md)
AOTtoAOTDL[v(OEd_q  )] = RegOrMem(Gd(Eax),Md)
AOTtoAOTDL[v(OEv    )] = SizePrefix(RegOrMem(Gw(Ax),Mw),RegOrMem(Gd(Eax),Md))
AOTtoAOTDL[v(ORd_Mb )] = RegOrMem(Gd(Eax),Mb)
AOTtoAOTDL[v(ORd_Mw )] = RegOrMem(Gd(Eax),Mw)
AOTtoAOTDL[v(OQpi   )] = RegOrMem(MMXReg(MM0),Mq)
AOTtoAOTDL[v(OQd    )] = RegOrMem(MMXReg(MM0),Mq)
AOTtoAOTDL[v(OQq    )] = RegOrMem(MMXReg(MM0),Mq)
AOTtoAOTDL[v(OWdq   )] = RegOrMem(XMMReg(XMM0),Mdq)
AOTtoAOTDL[v(OWps   )] = RegOrMem(XMMReg(XMM0),Mdq)
AOTtoAOTDL[v(OWpd   )] = RegOrMem(XMMReg(XMM0),Mdq)
AOTtoAOTDL[v(OWq    )] = RegOrMem(XMMReg(XMM0),Mdq)
AOTtoAOTDL[v(OWss   )] = RegOrMem(XMMReg(XMM0),Md)
AOTtoAOTDL[v(OWsd   )] = RegOrMem(XMMReg(XMM0),Mq)
AOTtoAOTDL[v(OUdq_Md)] = RegOrMem(XMMReg(XMM0),Md)
AOTtoAOTDL[v(OUdq_Mq)] = RegOrMem(XMMReg(XMM0),Mq)
AOTtoAOTDL[v(OUdq_Mw)] = RegOrMem(XMMReg(XMM0),Mw)

AOTtoAOTDL[v(ORw    )] = RegOrMem(Gw(Ax),None)
AOTtoAOTDL[v(ORd    )] = RegOrMem(Gd(Eax),None)
AOTtoAOTDL[v(ORv    )] = SizePrefix(RegOrMem(Gw(Ax),None),RegOrMem(Gd(Eax),None))
AOTtoAOTDL[v(OStN   )] = RegOrMem(FPUReg(ST0),None)
AOTtoAOTDL[v(ONq    )] = RegOrMem(MMXReg(MM0),None)
AOTtoAOTDL[v(OUps   )] = RegOrMem(XMMReg(XMM0),None)
AOTtoAOTDL[v(OUpd   )] = RegOrMem(XMMReg(XMM0),None)
AOTtoAOTDL[v(OUq    )] = RegOrMem(XMMReg(XMM0),None)
AOTtoAOTDL[v(OUdq   )] = RegOrMem(XMMReg(XMM0),None)

AOTtoAOTDL[v(OMpd   )] = RegOrMem(None,Mdq )
AOTtoAOTDL[v(OMps   )] = RegOrMem(None,Mdq )
AOTtoAOTDL[v(OReal4 )] = RegOrMem(None,Md  )
AOTtoAOTDL[v(OReal8 )] = RegOrMem(None,Mq  )
AOTtoAOTDL[v(OReal10)] = RegOrMem(None,Mt  )
AOTtoAOTDL[v(OMb    )] = RegOrMem(None,Mb  )
AOTtoAOTDL[v(OMw    )] = RegOrMem(None,Mw  )
AOTtoAOTDL[v(OMd    )] = RegOrMem(None,Md  )
AOTtoAOTDL[v(OMs    )] = RegOrMem(None,Mt  )
AOTtoAOTDL[v(OMq    )] = RegOrMem(None,Mq  )
AOTtoAOTDL[v(OMdq   )] = RegOrMem(None,Mdq )
AOTtoAOTDL[v(OMd_q  )] = RegOrMem(None,Md  )
AOTtoAOTDL[v(OMa    )] = SizePrefix(RegOrMem(None,Md),RegOrMem(None,Mf))
AOTtoAOTDL[v(OMp    )] = SizePrefix(RegOrMem(None,Md),RegOrMem(None,Mq))
AOTtoAOTDL[v(OM     )] = AddrPrefix(RegOrMem(None,Mw),RegOrMem(None,Md))

# These have flexible sizes: we don't check the size while type-checking.
AOTtoAOTDL[v(OFPEnv    )] = RegOrMem(None,Md)
AOTtoAOTDL[v(OFPEnvLow )] = RegOrMem(None,Md)
AOTtoAOTDL[v(OSimdState)] = RegOrMem(None,Md)
