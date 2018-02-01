from X86MetaData import *
import ply.lex as lex

x86_reserved = [
(PF1List ,'PFX'),
(R8List  ,'Gb' ),
(R16List ,'Gw'),
(R32List ,'Gd'),
(SegList ,'Seg'),
(CntList ,'CNT'),
(DbgList ,'DBG'),
(FPUList ,'FPU'),
(MMXList ,'MMX'),
(XMMList ,'XMM'),
(MnemList,'Mnem'),
(MSList  ,'SIZE'),
]

reserved = dict()
inverse  = dict()
for list,tok in x86_reserved:
	for el in list:
		reserved[str(el)] = tok
		inverse[str(el)] = el
		
excess = [('ptr','PTR')]

for (k,v) in excess:
	reserved[str(k)] = v

class X86Lexer(object):

	tokens = ['LSQBR','RSQBR','COLON','COMMA','TIMES','PLUS','NUM'] + map(lambda (a,b): b,x86_reserved + excess)
	
	t_LSQBR = r'\['
	t_RSQBR = r'\]'
	t_COLON = r':'
	t_COMMA = r','
	t_TIMES = r'\*'
	t_PLUS  = r'\+'
	t_ignore_SEMI  = r';'
	t_ignore = ' \t'
	
	def t_NEWLINE(self,t):
		r'\n+'
		t.lexer.lineno += len(t.value)
		return t
	
	def t_ID(self,t):
		r'[a-zA-Z][a-zA-Z0-9]*'
		ttype = reserved.get(t.value,None)
		if ttype is not None:
			t.type  = ttype
			if t.value in inverse:
				t.value = inverse[t.value]
		else:
			raise RuntimeError("token %s sucks" % t.value)
		return t
	
	def t_HEXNUM(self,t):
		r'[0-9]+[0-9a-fA-F]*h'
		t.value = int("0x"+t.value[:-1],16)
		t.type  = 'NUM'
		return t
			
	def t_NUM(self,t):
		r'[0-9]+'
		t.value = int(t.value)
		t.type  = 'NUM'
		return t
	
	def t_error(self,t):
		raise SyntaxError("Illegal character '%s' at position %d:%d" % (t.value[0],t.lexer.lineno,t.lexer.lexpos))

	def __init__(self,**kwargs):
		self.lexer = lex.lex(module=self,**kwargs)
