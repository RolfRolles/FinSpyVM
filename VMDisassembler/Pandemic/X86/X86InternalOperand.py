""" This file contains an enumeration (in the style of :mod:`~.Enumerate`) for
abstract operand types in X86."""

from Pandemic.Util.Enumerate import enum_strfn

aote, AOTList = enum_strfn("AOT", (lambda o:o),
['OAL', 'OALR8L', 'OCL', 'OCLR9L', 'ODLR10L', 'OBLR11L', 'OAHR12L', 'OCHR13L',
'ODHR14L', 'OBHR15L', 'OAX', 'ODX', 'OeAX', 'OrAXr8', 'OrAX', 'OeCX', 'OrCXr9',
'OeDX', 'OrDXr10', 'OeBX', 'OrBXr11', 'OeSP', 'OrSPr12', 'OeBP', 'OrBPr13',
'OeSI', 'OrSIr14', 'OeDI', 'OrDIr15', 'OCS', 'ODS', 'OES', 'OGS', 'OFS', 'OSS',
'OSw', 'OCd', 'ODd', 'OIb', 'OIw', 'OIv', 'OIz', 'O1', 'OGb', 'OGw', 'OGd',
'OGv', 'OGd_q', 'OGz', 'ORw', 'ORd', 'ORv', 'OMb', 'OMw', 'OMd', 'OMs', 'OMq',
'OMdq', 'OMd_q', 'OMa', 'OMp', 'OMpd', 'OMps', 'OM', 'OEb', 'OEw', 'OEd', 'OEv',
'OEd_q', 'OOb', 'OOv', 'OAp', 'OJb', 'OJz', 'OXb', 'OXv', 'OXz', 'OYb', 'OYv',
'OYz', 'OSt0', 'OStN', 'OFPEnv', 'OFPEnvLow', 'OReal4', 'OReal8', 'OReal10',
'ONq', 'OPd', 'OPq', 'OPpi', 'OVdq', 'OVpd', 'OVps', 'OVsd', 'OVss', 'OVq',
'OUps', 'OUpd', 'OUq', 'OUdq', 'OQpi', 'OQd', 'OQq', 'OWdq', 'OWps', 'OWpd',
'OWq', 'OWss', 'OWsd', 'OSimdState', 'OUdq_Md', 'OUdq_Mq', 'OUdq_Mw', 'ORd_Mb',
'ORd_Mw', 'OXw', 'OXd', 'OYw', 'OYd', 'OIbv', 'OMbBx', 'OMbEbx'])

AOTElt = aote #: `type` object for abstract operand type enumeration elements

(OAL, OALR8L, OCL, OCLR9L, ODLR10L, OBLR11L, OAHR12L, OCHR13L, ODHR14L,
OBHR15L,OAX, ODX, OeAX, OrAXr8, OrAX, OeCX, OrCXr9, OeDX, OrDXr10, OeBX,
OrBXr11, OeSP,OrSPr12, OeBP, OrBPr13, OeSI, OrSIr14, OeDI, OrDIr15, OCS, ODS,
OES, OGS, OFS,OSS, OSw, OCd, ODd, OIb, OIw, OIv, OIz, O1, OGb, OGw, OGd, OGv,
OGd_q, OGz, ORw,ORd, ORv, OMb, OMw, OMd, OMs, OMq, OMdq, OMd_q, OMa, OMp, OMpd,
OMps, OM, OEb,OEw, OEd, OEv, OEd_q, OOb, OOv, OAp, OJb, OJz, OXb, OXv, OXz, OYb,
OYv, OYz,OSt0, OStN, OFPEnv, OFPEnvLow, OReal4, OReal8, OReal10, ONq, OPd, OPq,
OPpi,OVdq, OVpd, OVps, OVsd, OVss, OVq, OUps, OUpd, OUq, OUdq, OQpi, OQd, OQq,
OWdq,OWps, OWpd, OWq, OWss, OWsd, OSimdState, OUdq_Md, OUdq_Mq, OUdq_Mw,
ORd_Mb,ORd_Mw, OXw, OXd, OYw, OYd, OIbv, OMbBx, OMbEbx) = AOTList

X86_INTERNAL_OPERAND_LAST = OMbEbx.IntValue()

