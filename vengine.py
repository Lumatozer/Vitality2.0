cache=""
state=""

def valid_var_name(name):
    if len(name)<1:
        return False
    if name in reserved:return False
    if name in ["vars"]:return False
    whitelist="abcdefghijklmnopqrstuvwxyz"
    for x in name:
        if x not in whitelist:
            return False
    return True

def isnum(data):
    if data==".": return True
    else:
        try:
            float(data)
            return True
        except:
            return False

def error(errordata):
    exit(errordata)

special_data_types=["num[]","str[]","num{}str","str{}num","str{}str","num{}num"]
var_init_normal=["num","str"]
reserved=["num","str","struct","function","for","if","while","num[]","str[]","num{}str","str{}num","str{}str","num{}num","spawn","HALT","BREAK","true","false","append","remove"]
operators=["+","=","-","/","!","not","in",">","<","and"]
no_space_operators=["+","=","-","/","!",">","<"]
brackets="()[]{}"

class token:
    def __init__(self,type,value):
        self.type=type
        self.value=value
    def __repr__(self) -> str:
        return f"['{self.type}' : '{self.value}'] "

def get_type_from_str(typestr):
    if typestr=="num":
        return type(1.0)
    if typestr=="str":
        return type("")

def get_type_defaults(ttype,raw=False):
    if ttype==type(1.0):
        if raw:
            return 1.0
        return "1.0"
    if ttype==type(""):
        if raw:
            return ""
        return "''"

def bracket_type(data):
    if data in "()":
        return "round_bracket"
    if data in "[]":
        return "square_bracket"
    if data in "{}":
        return "curly_bracket"

def opp_bracket(bracket):
    exchange = {0: 1, 1:0}
    if bracket in "()":
        return "()"[exchange["()".index(bracket)]]
    if bracket in "{}":
        return "{}"[exchange["{}".index(bracket)]]
    if bracket in "[]":
        return "[]"[exchange["[]".index(bracket)]]

def get_type_from_literal(data):
        if data[0]=="'" and data[-1]=="'":
            return 'str'
        if isnum(data):
            return 'num'
        if valid_var_name(data):
            return 'var'

def cache_handler():
    global state,cache
    if cache!="" and state!="" and cache.replace(" ","")!="":
        if state=="sys":
            if cache not in reserved:
                if "." in cache:
                    state="nested_var"
                else:state="var"
            if cache in operators:
                state="operator"
            if cache in special_data_types:
                if cache[-2:]=="[]" and cache[:-2] in ["str","num"]:
                    state="arr_init"
                    cache=cache[:-2]
                elif "{}" in cache:
                    splitcheck=cache.split("{}")
                    if len(splitcheck)==2 and splitcheck[0] in ["str","num"] and splitcheck[1] in ["str","num"]:
                        state="dict_init"
                        cache=[cache.split("{}")[0],cache.split("{}")[1]]
        if state=="var":
            if cache=="vars":
                state="vars"
                cache="locals()|globals()"
            elif cache[-1:]=="]" and len(cache.split("["))==2 and len(cache.split("]"))==2 and get_type_from_literal(cache.split("[")[1].split("]")[0])!=None:
                state="lookup"
                cache=[cache.split("[")[0],cache.split("[")[1].split("]")[0]]
            elif cache[-2:]=="()":
                state="call"
                cache=cache.replace("()","")
        tokens.append(token(state,cache))
    state=""
    cache=""

def tokeniser(script):
    global state,cache,tokens
    tokens=[]
    for x in script.replace("\n"," ")+" ":
        if isnum(x) and state in [""]:
            cache_handler()
            state="num"
            cache+=x
        elif x=="," and state in ["","sys","num"]:
            cache_handler()
            tokens.append(token("comma",x))
        elif x==":" and state in ["","sys","num"]:
            cache_handler()
            tokens.append(token("colon",x))
        elif x==";" and state in ["","sys","num"]:
            cache_handler()
            tokens.append(token("eol",x))
        elif x in brackets and state in ["","num","sys"]:
            if x in "({[" and state=="sys":
                cache+=x
            elif x in ")}]" and state=="sys" and opp_bracket(x) in cache:
                cache+=x
            else:
                cache_handler()
                tokens.append(token(bracket_type(x),x))
        elif x in operators and state in ["","sys","num"]:
            cache_handler()
            tokens.append(token("operator",x))
        elif state=="num" and not isnum(x):
            state=""
            tokens.append(token("num",cache))
            cache=""
        elif x=="'" and state in [""]:
            cache_handler()
            cache+=x
            state="str"
        elif x=="'" and state=="str":
            cache+=x
            state=""
            tokens.append(token("str",cache))
            cache=""
        elif x==" " and cache!="" and state not in ["str"]:
            cache_handler()
        elif x==" " and cache=="" and state=="":
            pass
        elif not isnum(x) and state in [""] and cache=="":
            state="sys"
            cache+=x
        else:
            cache+=x
    cc_tokens=tokens
    tokens=[];cache="";state=""
    return cc_tokens

def array_split(arr,elem):
    out=[]
    temp=[]
    for x in arr:
        if x.value!=elem.value and x.type!=elem.value:
            temp.append(x)
        elif x.value==elem.value and x.type==elem.type:
            out.append(temp)
            temp=[]
    if temp!=[]:
        out.append(temp)
    return out

def get_arg_tokens(tokens,ignorei,wrapper=[False,False],onchar=[False,False]):
    out=[]
    ignore=[]
    if wrapper[0]:
        brs=0
        for x in tokens:
            if x.value==wrapper[1]:
                brs+=1
            elif x.value==opp_bracket(wrapper[1]):
                brs-=1
            elif brs==0:
                out=out[1:-1]
                break
            ignorei+=1
            ignore.append(ignorei)
            out.append(x)
    elif onchar[0]:
        for x in tokens:
            ignorei+=1
            ignore.append(ignorei)
            if x.value==onchar[1]:
                break
            out.append(x)
    return out,ignore

def eval_out_type(tokens,expected):
    expr=""
    for x in tokens:
        if x.value in ["true","false"]:
            expr+=" True "
        elif x.type=="str":
            expr+=" '' "
        elif x.type=="num":
            expr+=" 1.0 "
        elif x.type=="operator":
            if x.value in no_space_operators:
                expr+=x.value
            else:
                expr+=f" {x.value} "
        elif x.type=="nested_var":
            x=x.value.split(".")
            try:
                expr+=f' {get_type_defaults(type(eval(f"symbol_table[x[0]].{x[1]}")))} '
            except:
                return False
        elif x.type=="lookup":
            x=x.value
            if x[0] not in symbol_table or symbol_table[x[0]][0] not in [type([]),type({})]:return False
            if symbol_table[x[0]][0]==type([]):
                if get_type_from_str(get_type_from_literal(x[1]))!=type(1.0):return False
                expr+=f" {get_type_defaults(symbol_table[x[0]][1])} "
            elif symbol_table[x[0]][0]==type({}):
                if get_type_from_str(get_type_from_literal(x[1]))!=symbol_table[x[0]][1]:return False
                expr+=f" {get_type_defaults(symbol_table[x[0]][2])} "
        elif x.type=="var":
            if x.value not in symbol_table:return False
            expr+=f" {get_type_defaults(symbol_table[x.value][0])} "
        elif "bracket" in x.type:
            expr+=f" {x.value} "
        elif "vars"==x.type:
            expr+=" {} "
        else:
            return False
    return type(eval(expr,{'__builtins__': {}}, {}))==expected

def jit(tokens,depth=False,infunc=False,inloop=False):
    global symbol_table
    if "symbol_table" not in globals():
        symbol_table={"if_i":-1,"if_s":{},"txsender":[type("")],"txamount":[type(1.0)],"txcurr":[type("")],"txmsg":[type([]),type("")],"whiles_":{},"whiles_i":-1,"funcs_":{},"txto":[type("")]}
    i=-1
    ignore=[]
    for x in tokens:
        i+=1
        if x.value!=";" and i not in ignore:
            if x.type=="sys" and x.value in var_init_normal:
                if x.value in symbol_table:error(f"Variable {x.value} has been already declared with type {symbol_table[x.value][0]}")
                if not valid_var_name(tokens[i+1].value):error(f"Invalid variable name {tokens[i+1].value}")
                symbol_table[tokens[i+1].value]=[get_type_from_str(x.value),get_type_defaults(get_type_from_str(x.value),raw=1)]
                ignore.append(i+1)
            elif x.type=="var" and tokens[i+1].value=="=":
                if x.value not in symbol_table:error(f"Variable {x.value} is not defined.")
                arg_res=get_arg_tokens(tokens[i+2:],i+1,onchar=[True,";"])
                ignore+=arg_res[1]
                if eval_out_type(arg_res[0],symbol_table[x.value][0]):
                    pass
                else:
                    error(f"Invalid type assignment to variable {x.value}")
                ignore.append(i+1)
            elif x.type=="arr_init":
                if x.value in symbol_table:error(f"Variable {x.value} has been already declared with type {symbol_table[x.value][0]}")
                if not valid_var_name(tokens[i+1].value):error(f"Invalid variable name {tokens[i+1].value}")
                symbol_table[tokens[i+1].value]=[type([]),get_type_from_str(x.value)]
                ignore.append(i+1)
            elif x.type=="dict_init":
                if tokens[i+1].value in symbol_table:error(f"Variable {tokens[i+1].value} has been already declared with type {symbol_table[x.value][0]}")
                if not valid_var_name(tokens[i+1].value):error(f"Invalid variable name {tokens[i+1].value}")
                symbol_table[tokens[i+1].value]=[type({}),get_type_from_str(x.value[0]),get_type_from_str(x.value[1])]
                ignore.append(i+1)
            elif x.value=="struct":
                if x.value in symbol_table:error(f"Variable {x.value} has been already declared with type {symbol_table[x.value][0]}")
                if not valid_var_name(tokens[i+1].value):error(f"Invalid variable name {tokens[i+1].value}")
                arg_res=get_arg_tokens(tokens[i+2:],i+1,wrapper=[True,"{"])
                ignore+=arg_res[1]
                struct_vars=array_split(arg_res[0],token("comma",","))
                struct_vars_define={}
                for x in struct_vars:
                    if len(x)!=3:error(f"Invalid struct declaration {' '.join([xy.value for xy in x])}")
                    if x[0].value not in ["num","str"]:error(f"Invalid variable type for class {tokens[i+1].value}")
                    if not valid_var_name(x[2].value):error(f"Invalid variable name {x[2].value}")
                    if x[1].value!=":":error(f"Invalid declaration method for class {tokens[i+1].value}")
                    struct_vars_define[x[2].value]=get_type_defaults(get_type_from_str(x[0].value))
                ex_locals={"__builtins__":{'__build_class__':__build_class__,"__name__":__name__}}
                ex_globals=ex_locals.copy()
                exec(f"class {tokens[i+1].value}:\n    def __init__(self):"+"".join([f"\n        self.{x}={struct_vars_define[x]}" for x in struct_vars_define.keys()]),ex_globals,ex_locals)
                symbol_table[tokens[i+1].value]=ex_locals[tokens[i+1].value]
                ignore.append(i+1)
            elif x.value=="spawn":
                if tokens[i+1].value[0] not in symbol_table:error(f"Class {tokens[i+1].value[0]} is not defined")
                if f"<class 'vengine.{tokens[i+1].value[0]}'>"!=str(symbol_table[tokens[i+1].value[0]]):error(f"Illegal object spawning of potential class {tokens[i+1].value[0]}")
                if not valid_var_name(tokens[i+1].value[1]):error(f"Invalid variable name {tokens[i+1].value[1]}")
                symbol_table[tokens[i+1].value[1]]=symbol_table[tokens[i+1].value[0]]()
                ignore.append(i+1)
            elif x.type=="nested_var" and len(x.value.split("."))==2:
                x=x.value.split(".")
                if x[0] not in symbol_table:error(f"Undefined object reference found '{x[0]}'")
                if not valid_var_name(x[1]):error(f"Invalid variable name {x[1]}")
                if x[1] not in dir(symbol_table[x[0]]):error(f"Invalid object variable '{x[1]}' of object '{x[0]}'")
                arg_res=get_arg_tokens(tokens[i+2:],i+1,onchar=[True,";"])
                ignore+=arg_res[1]
                print(type(eval(f"symbol_table[x[0]].{x[1]}")))
                if eval_out_type(arg_res[0],type(eval(f"symbol_table[x[0]].{x[1]}"))):
                    pass
                else:
                    error(f"Invalid type assignment to variable '{x[1]}'")
                ignore.append(i+1)
            elif x.type=="lookup":
                x=x.value
                ignore.append(i+1)
                if tokens[i+1].value!="=":error("Illegal operation on a lookup token was performed")
                if x[0] not in symbol_table:error(f"Undefined object reference found '{x[0]}'")
                if symbol_table[x[0]][0] == type([]):
                    if get_type_from_str(get_type_from_literal(x[1]))!=type(1.0):error(f"Invalid type assignment to array {x[0]}")
                    arg_res=get_arg_tokens(tokens[i+2:],i+1,onchar=[True,";"])
                    ignore+=arg_res[1]
                    if eval_out_type(arg_res[0],symbol_table[x[0]][1]):
                        pass
                    else:
                        error(f"Invalid type assignment to variable {x.value}")
                elif symbol_table[x[0]][0] == type({}):
                    if get_type_from_str(get_type_from_literal(x[1]))!=symbol_table[x[0]][1]:error(f"Invalid type assignment to dict {x[0]}")
                    arg_res=get_arg_tokens(tokens[i+2:],i+1,onchar=[True,";"])
                    ignore+=arg_res[1]
                    if eval_out_type(arg_res[0],symbol_table[x[0]][2]):
                        pass
                    else:
                        error(f"Invalid type assignment to variable {x.value}")
                else:
                    error("Invalid lookup performed on something that is not a list or a dict")
            elif x.value=="if":
                arg_res=get_arg_tokens(tokens[i+1:],i,wrapper=[True,"("])
                condition_tokens=arg_res[0]
                if not eval_out_type(arg_res[0],type(True)):error("A bool type value is expected for conditions in IF statements")
                ignore+=arg_res[1]
                arg_res=get_arg_tokens(tokens[ignore[-1]+1:],ignore[-1],wrapper=[True,"{"])
                ignore+=arg_res[1]
                jit(arg_res[0],depth=True)
                symbol_table["if_i"]+=1
                symbol_table["if_s"][symbol_table["if_i"]]={"condition":condition_tokens,"code":arg_res[0]}
            elif x.value=="while":
                if tokens[i+1].value!="{":error("Invalid syntax found while defining a while loop")
                arg_res=get_arg_tokens(tokens[i+1:],i,wrapper=[True,"{"])
                jit(arg_res[0],depth=True,inloop=True)
                symbol_table["whiles_i"]+=1
                symbol_table["whiles_"][symbol_table["whiles_i"]]=arg_res[0]
                ignore+=arg_res[1]
            elif x.value=="break":
                if not inloop:error("Break statements cannot be used outside loops")
            elif x.type=="call":
                if x.value not in symbol_table["funcs_"]:error(f"Function {x.value} is undefined")
            elif x.value=="function":
                if not valid_var_name(tokens[i+1].value):error(f"Invalid function name {tokens[i+1].value}")
                if tokens[i+1].value in symbol_table["funcs_"]:error(f"Function {tokens[1+1].value} has been predefined")
                arg_res=get_arg_tokens(tokens[i+2:],i+1,wrapper=[True,"{"])
                ignore+=arg_res[1]
                jit(arg_res[0],depth=True,infunc=True)
                symbol_table["funcs_"][tokens[i+1].value]=arg_res[0]
                ignore.append(i+1)
            else:
                error(f"Token {x} was not ignored")
    return symbol_table

def args2expr(arg_tokens):
    expr=""
    for x in arg_tokens:
        if x.value in ["true","false"]:
            if x.value=="true":
                expr+=" True "
            else:
                expr+=" False "
        elif x.type in ["num","str"]:
            expr+=f" {x.value} "
        elif x.type=="operator":
            if x.value in no_space_operators:
                expr+=x.value
            else:
                expr+=f" {x.value} "
        elif x.type=="nested_var":
            try:
                expr+=f' {x.value} '
            except:
                return False
        elif x.type=="lookup":
            x=x.value
            if symbol_table[x[0]][0]==type([]):
                expr+=f" {x[0]}[{x[1]}] "
            elif symbol_table[x[0]][0]==type({}):
                if symbol_table[x[0]][1]==type(1.0):
                    expr+=f" {x[0]}[{x[1]}] "
                elif symbol_table[x[0]][1]==type(""):
                    expr+=f" {x[0]}['{x[1]}'] "
        elif x.type=="var":
            expr+=f" {x.value} "
        elif "bracket" in x.type:
            expr+=f" {x.value} "
        elif x.type=="vars":
            expr+=f" {x.value} "
    return expr

def compiler(tokens,jit,depth=False):
    global compiled,indents,if_s
    if not depth:
        compiled="fees_=0.0\n"
        indents=0
        if_s=-1
        whiles_s=-1
    def add_compile(data):
        global compiled
        compiled+="    "*indents+data+"\n"
    i=-1
    ignore=[]
    for x in tokens:
        i+=1
        if x.value!=";" and i not in ignore:
            if x.type=="sys" and x.value in var_init_normal:
                add_compile(f"globals()['{tokens[i+1].value}']={get_type_defaults(get_type_from_str(x.value))}")
                add_compile("fees_+=1")
                ignore.append(i+1)
            elif x.type=="var" and tokens[i+1].value=="=":
                ignore.append(i+1)
                arg_res=get_arg_tokens(tokens[i+2:],i+1,onchar=[True,";"])
                add_compile(f"fees_+={len(arg_res[0])}")
                ignore+=arg_res[1]
                add_compile(f"globals()['{x.value}']={args2expr(arg_res[0])}")
            elif x.type=="arr_init":
                add_compile(f"globals()['{tokens[i+1].value}']=[]")
                add_compile("fees_+=3")
                ignore.append(i+1)
            elif x.type=="dict_init":
                add_compile(f"globals()['{tokens[i+1].value}']="+"{}")
                add_compile("fees_+=1")
                ignore.append(i+1)
            elif x.value=="struct":
                add_compile(f"class {tokens[i+1].value}:")
                indents+=1
                add_compile("def __init__(self):")
                indents+=1
                arg_res=get_arg_tokens(tokens[i+2:],i+1,wrapper=[True,"{"])
                ignore+=arg_res[1]
                class_vars=vars(jit[tokens[i+1].value]())
                ignore.append(i+1)
                ignorei=i+1
                for x in class_vars:
                    ignorei+=1
                    ignore.append(ignorei)
                    if class_vars[x]=="":
                        add_compile(f"self.{x}=''")
                    if class_vars[x]==1.0:
                        add_compile(f"self.{x}={1.0}")
                add_compile(f"fees_+={len(class_vars.keys())}")
                indents-=2
            elif x.type=="call":
                add_compile(f"{x.value}()")
                add_compile(f"fees_+={3}")
            elif x.value=="spawn":
                add_compile(f"globals()['{tokens[i+1].value[1]}']={tokens[i+1].value[0]}()")
                add_compile(f"fees_+={3}")
                ignore.append(i+1)
            elif x.type=="nested_var":
                ignore.append(i+1)
                arg_res=get_arg_tokens(tokens[i+2:],i+1,onchar=[True,";"])
                add_compile(f"fees_+={len(arg_res[0])}")
                ignore+=arg_res[1]
                add_compile(f"globals()['{x.value}']={args2expr(arg_res[0])}")
            elif x.type=="lookup":
                ignore.append(i+1)
                x=x.value
                arg_res=get_arg_tokens(tokens[i+2:],i+1,onchar=[True,";"])
                add_compile(f"fees_+={len(arg_res[0])}")
                ignore+=arg_res[1]
                if symbol_table[x[0]][0] == type([]):
                    add_compile(f"globals()['{x[0]}'][{x[1]}]={args2expr(arg_res[0])}")
                elif symbol_table[x[0]][0] == type({}):
                    add_compile(f"globals()['{x[0]}'][{x[1]}]={args2expr(arg_res[0])}")
            elif x.value=="break":
                add_compile(f"fees_+=1")
                add_compile("break")
            elif x.value=="if":
                if_s+=1
                ignore.append(i+1)
                c_if=jit['if_s'][if_s]
                ignorei=i+1
                for x in c_if['condition']:ignorei+=1;ignore.append(ignorei)
                ignorei+=1;ignore.append(ignorei);ignorei+=1;ignore.append(ignorei)
                for x in c_if['code']:ignorei+=1;ignore.append(ignorei)
                ignorei+=1;ignore.append(ignorei)
                add_compile(f"fees_+={len(c_if['condition'])}")
                add_compile(f"if {args2expr(c_if['condition'])}:")
                indents+=1
                add_compile(f"fees_+={len(c_if['code'])}")
                compiler(c_if['code'],jit,depth=True)
                indents-=1
            elif x.value=="while":
                whiles_s+=1
                c_while=jit['whiles_'][whiles_s]
                ignore.append(i+1)
                ignorei=i+1
                for x in c_while:ignorei+=1;ignore.append(ignorei)
                ignorei+=1;ignore.append(ignorei)
                add_compile("while True:")
                indents+=1
                add_compile(f"fees_+=2")
                compiler(c_while,jit,depth=True)
                indents-=1
            elif x.value=="function":
                ignore.append(i+1)
                ignore.append(i+2)
                c_func=symbol_table["funcs_"][tokens[i+1].value]
                ignorei=i+2
                for x in c_func:ignorei+=1;ignore.append(ignorei)
                ignore.append(ignorei+1)
                add_compile(f"def {tokens[i+1].value}():")
                indents+=1
                add_compile(f"fees_+=1")
                compiler(c_func,jit,depth=True)
                indents-=1
                add_compile(f"globals()['{tokens[i+1].value}']={tokens[i+1].value}")
            else:
                error(f"Token {x} was not ignored while compiling")
    if not depth:
        return compiled

def run(script):
    try:
        tk=tokeniser(script)
        jitst=jit(tokeniser(script))
        return compiler(tk,jitst)
    except:
        import traceback
        traceback.print_exc()
        return False