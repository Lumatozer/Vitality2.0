operators=["=","-","+","*","/","!","==","!=","not","in","or","and"]
protected=["function","int","float","str","and","or","in","not","if","Dict","List","typing","vars","fees"]

symbol_table={}
if_s={}
funcs={}
if_i=0
compiled=""

def isnum(check):
    try:
        int(check)
        return True
    except:
        return False

def getsystype(x):
    if x=="[" or x=="]":
        return "arr_bracket"
    if x=="(" or x==")":
        return "bracket"
    if x=="{" or x=="}":
        return "dict_bracket"
    if x in operators:
        return "operators"
    if x in protected:
        return "sys"
    if x==":":
        return "colon"
    if x==",":
        return "comma"
    if x==";":
        return "eol"
    return "sys"

def absolute_defaults(vartype):
    if vartype==type(1):
        return 1
    if vartype==type(1.0):
        return 1.0
    if vartype==type(""):
        return "''"
    if vartype==type({}):
        return {}
    if vartype==type([]):
        return []

def gettypedefaults(vartype):
    if vartype==type(1):
        return "1"
    if vartype==type(1.0):
        return "1.0"
    if vartype==type(""):
        return "''"
    if vartype==type([]):
        return "[0]"
    if vartype==type({}):
        return "{}"

def getdefaults(tkn):
    if tkn.type=="sys" and tkn.value=="(globals() | locals())":
        return "{}"
    if tkn.value in operators:
        return tkn.value
    if tkn.type=="sys":
        return ""
    if tkn.value in ["[","]",",",":","{","}","(",")"]:
        return tkn.value
    if tkn.type=="num":
        return "1"
    if tkn.type=="str":
        return "''"
    if tkn.type=="var":
        return gettypedefaults(symbol_table[tkn.value][0])
    if tkn.type=="len":
        return "1"
    if tkn.type=="arr_call":
        return gettypedefaults(str2type(symbol_table[tkn.value.split(",")[0]][1].split(",")[0]))
    if tkn.type=="dict_call":
        return gettypedefaults(str2type(symbol_table[tkn.value.split(",")[0]][1].split(",")[1]))

def str2type(x):
    if x=="str":
        return type("")
    if x=="int":
        return type(1)
    if x=="float":
        return type(1.0)
    if x=="dict":
        return type({})
    if x=="arr":
        return type([])

def evaluate_out_type(tokens):
    expr=""
    try:
        for x in tokens:
            expr+=getdefaults(x)+" "
    except:
        exit("----------------------ERROR-----------------------")
    return type(eval(expr))

def get_type_from_str(x: str):
    try:
        import json
        x_type=json.loads(x)
        return type(x_type)
    except:
        return type(x)

def bracket_type(x):
    if x in "()":
        return "bracket"
    if x in "{}":
        return "dict_bracket"
    if x in "[]":
        return "arr_bracket"

class token:
    def __init__(self,type,value):
        self.fees=0
        if type=="var" and value in ["fees","vars"]:
            exit("Cannot call or reference environment variables")
        elif type=="sys" and value=="vars":
            self.fees+=10
            value="(globals() | locals())"
        elif type=="sys" and value=="fees":
            self.fees+=1
            value=""
        elif type=="var" and "[" in value and "]" in value:
            self.fees+=3
            if value.split("[")[0] in ["str","int","float"]:
                self.fees+=2
                type="arr_init"
            else:
                self.fees+=1
                type="arr_call"
            value=f'{value.split("[")[0]},{value.split("[")[1].split("]")[0]}'
        elif type=="var" and "{}" in value and value.split("{}")[0] in ["str","int"] and value.split("{}")[1] in ["str","int"]:
            type="dict_init"
            self.fees+=5
            value=f'{value.split("{}")[0]},{value.split("{}")[1]}'
        elif type=="var" and "{" in value and "}" in value and "{}" not in value:
            type="dict_call"
            self.fees+=4
            value=f"{value.split('{')[0]},{value.split('{')[1][:-1]}"
        elif value[-2:]=="()":
            type="exec"
            self.fees+=3
            value=value[:-2]
        elif type=="var" and value[0]=="&":
            self.fees+=10
            type="len"
        self.type=type
        self.value=value
        self.fees+=len(self.type)+len(self.value)

def tokeniser(script):
    global tokens,last_token,symbol_table
    tokens=[]
    last_token=token("","")
    cache=""
    state=""
    def append_token(tkn):
        global last_token,symbol_table,tokens
        last_token=tkn
        tokens.append(last_token)
    for x in script.replace("\n",""):
        if (state=="sys" and x in ["(",")","'"]+operators and cache in protected):
            state=""
            append_token(token(getsystype(cache),cache))
            if x in "(){}[]":
                append_token(token(bracket_type(x),x))
            cache=""
            continue
        if x==" " and state=="" and cache=="":
            continue
        if x in "(){}[]" and state in ["var","","num"]:
            if cache in protected:
                append_token(token("sys",cache))
                cache=""
                state=""
                continue
            elif cache!="":append_token(token("var",cache))
            append_token(token(bracket_type(x),x))
            continue
        if x=="," and ["sys","var","","num"]:
            if cache!="" and state in ["str","num"]:
                append_token(token(state,cache))
                cache=""
                state=""
            append_token(token("comma",x))
            continue
        if x==":" and["sys","var","","num"]:
            if cache!="" and state in ["str","num"]:
                append_token(token(state,cache))
                cache=""
                state=""
            append_token(token("colon",x))
            continue
        if x in operators and state in ["","sys"]:
            if cache!="":
                if cache in protected:
                    append_token(token("sys",cache))
                    cache=""
                    state=""
                    continue
                else:
                    append_token(token("var",cache))
                    cache=""
                    state=""
            if x=="=" and last_token.value=="=":
                del tokens[len(tokens)-1]
                append_token(token("operator","=="))
                continue
            if x=="=" and last_token.value=="!":
                del tokens[len(tokens)-1]
                append_token(token("operator","!="))
                continue
            append_token(token("operator",x))
            continue
        if x=="'" and state=="":
            state="str"
            continue
        if x=="'" and state=="str":
            state=""
            append_token(token("str","'"+cache+"'"))
            cache=""
            continue
        if state=="str":
            cache+=x
            continue
        if isnum(x) and state=="":
            state="num"
            cache+=x
            continue
        if (isnum(x) or x==".") and state=="num":
            cache+=x
            continue
        if state=="num" and not isnum(x):
            append_token(token("num",cache))
            append_token(token(getsystype(x),x))
            cache=""
            state=""
            continue
        if x==" " and state=="num":
            append_token(token("num",cache))
            cache=""
            state=""
            continue
        if x==" " and (state=="" or state=="sys"):
            if cache in protected:
                append_token(token("sys",cache))
                cache=""
                state=""
                continue
            append_token(token("var",cache))
            cache=""
            state=""
            continue
        if x==";" and state!="str":
            if cache!="":
                if cache in protected:
                    append_token(token("sys",cache))
                    cache=""
                    state=""
                    continue
                else:
                    append_token(token("var",cache))
                    cache=""
                    state=""
            append_token(token("eol",";"))
            continue
        cache+=x
        state="sys"
    return tokens+[token("eol",";")]

def type_error(var1,type1,type2):
    exit(f"Cannot assign variable '{var1}' of type {type1} a value of type {type2}")

def list_type_error(var,type):
    exit(f"Cannot insert a value of type {type} in list '{var}'")

def undefined_error(var):
    exit(f"'{var}' was not defined")

def not_support_assignment_error(var):
    exit(f"variable '{var}' does not support type assignment")

def validvar(var):
    if var in protected:
        return False
    whitelist="abcdefghijklmnopqrstuvwxyz"
    whitelist+=whitelist.upper()
    whitelist+="1234567890_"
    for x in var:
        if x not in whitelist: return False
    return True

def jit(tokens,depth=False,infunc=False):
    i=-1
    ignore=[]
    global symbol_table,if_s,funcs,if_i
    if "symbol_table" not in globals().keys():
        symbol_table={}
        if_s={}
        funcs={}
        if_i=0
    for x in tokens:
        i+=1
        if i not in ignore and x.value != ";":
            if x.type=="var" and tokens[i+1].value=="=":
                if x.value not in symbol_table:
                    undefined_error(x.value)
                expr=""
                ignorei=i+1
                expr_tokens=[]
                for tk in tokens[i+2:]:
                    if tk.value==";":
                        break
                    ignorei+=1
                    ignore.append(ignorei)
                    expr_tokens.append(tk)
                    expr+=(tk.value+" ")
                x_type=evaluate_out_type(expr_tokens)
                if symbol_table[x.value][0]!=x_type:
                    type_error(x.value,symbol_table[x.value][0],x_type)
                ignore.append(i+1)
            elif x.type=="sys" and x.value in ["str","float","int"] and validvar(tokens[i+1].value):
                if (tokens[i+1].value in symbol_table):
                    exit(f"'{tokens[i+1].value}' has already been declared")
                if (tokens[i+1].type!="var"):
                    exit(f"Cannot declare token '{tokens[i+1].value}' of type {tokens[i+1].type}")
                ignore.append(i+1)
                if "[]" not in x.value:
                    symbol_table[tokens[i+1].value]=[str2type(x.value),None]
            elif x.type=="arr_init" and tokens[i+1].type=="var" and tokens[i+2].value==";" and tokens[i+1].value not in symbol_table and validvar(tokens[i+1].value):
                if int(x.value.split(",")[1])>256:
                    exit("Array sizes cannot exceed 256")
                if int(x.value.split(",")[1])<1:
                    exit("Array sizes cannot be less than 1")
                symbol_table[tokens[i+1].value]=[type([]),f"{x.value}"]
                ignore.append(i+1)
            elif x.type=="dict_init" and tokens[i+1].value not in symbol_table and validvar(tokens[i+1].value):
                ignore.append(i+1)
                symbol_table[tokens[i+1].value]=[type({}),x.value]
            elif x.type=="dict_call":
                if x.value.split(",")[0] in symbol_table:
                    if symbol_table[x.value.split(",")[0]][0]!=type({}):
                        exit(f'Variable "{x.value.split(",")[0]}" is not a dictionary')
                    if str2type(symbol_table[x.value.split(",")[0]][1].split(",")[0])!=get_type_from_str(x.value.split(",")[1]):
                        exit(f'A type {get_type_from_str(x.value.split(",")[1])} lookup was performed on a dictionary "{x.value.split(",")[0]}" supporting lookup of only type  {symbol_table[x.value.split(",")[0]][1].split(",")[0]}')
                    if tokens[i+1].value=="=":
                        expr=""
                        ignorei=i+1
                        expr_tokens=[]
                        for tk in tokens[i+2:]:
                            if tk.value==";":
                                break
                            ignorei+=1
                            ignore.append(ignorei)
                            expr_tokens.append(tk)
                            expr+=(tk.value+" ")
                        if evaluate_out_type(expr_tokens)==str2type(symbol_table[x.value.split(",")[0]][1].split(",")[1]):
                            ignore.append(i+1)
                            continue
            elif x.type=="arr_call" and tokens[i+1].value=="=":
                ignore.append(i+1)
                if x.value.split(",")[0] not in symbol_table:
                    undefined_error(x.value.split(",")[0])
                if symbol_table[x.value.split(",")[0]][0]!=type([]):
                    not_support_assignment_error(x.value.split(",")[0])
                expr=""
                ignorei=i+1
                expr_tokens=[]
                for tk in tokens[i+2:]:
                    if tk.value==";":
                        break
                    ignorei+=1
                    ignore.append(ignorei)
                    expr_tokens.append(tk)
                    expr+=(tk.value+" ")
                x_type=evaluate_out_type(expr_tokens)
                if x_type!=str2type(symbol_table[x.value.split(",")[0]][1].split(",")[0]):
                    list_type_error(x.value.split(",")[0],x_type)
            elif x.value=="if":
                if tokens[i+1].value!="(":
                    exit("IF statements require conditions inside of round brackets")
                ignore.append(i+1)
                ignorei=i
                expr_tokens=[]
                brackets=0
                for tk in tokens[i+1:]:
                    if tk.value=="(":
                        ignorei+=1
                        ignore.append(ignorei)
                        expr_tokens.append(tk)
                        brackets+=1
                        continue
                    if tk.value==")":
                        ignorei+=1
                        ignore.append(ignorei)
                        expr_tokens.append(tk)
                        brackets-=1
                        continue
                    if brackets==0:
                        break
                    ignorei+=1
                    ignore.append(ignorei)
                    expr_tokens.append(tk)
                condition_tokens=expr_tokens
                x_type=evaluate_out_type(expr_tokens)
                if x_type!=type(True):
                    exit("IF statements require bool output as condition")
                if tokens[i+1+len(expr_tokens)].value!="{":
                    exit("Code wrapped inside of IF statements are required to be inside curly brackets")
                ignore.append(i+-1+len(expr_tokens))
                ignorei=i+len(expr_tokens)
                brackets=0
                code_tokens=[]
                for tkx in tokens[i+1+len(expr_tokens):]:
                    if tkx.value=="{":
                        ignorei+=1
                        ignore.append(ignorei)
                        brackets+=1
                        continue
                    if tkx.value=="}":
                        ignorei+=1
                        ignore.append(ignorei)
                        brackets-=1
                        continue
                    if brackets==0:
                        break
                    ignorei+=1
                    ignore.append(ignorei)
                    code_tokens.append(tkx)
                jit(code_tokens,depth=True)
                if_s[if_i]={"condition":condition_tokens,"code":code_tokens}
                if_i+=1
            elif x.value=="function" and x.type=="sys" and tokens[i+1].type=="var" and tokens[i+1].value not in symbol_table and tokens[i+1].value not in funcs:
                if tokens[i+2].value!="{":
                    exit("Code inside functions are required to be inside of curly brackets")
                ignore.append(i+1)
                ignorei=i+1
                expr_tokens=[]
                brackets=0
                for tku in tokens[i+2:]:
                    if tku.value=="{":
                        brackets+=1
                        ignorei+=1
                        ignore.append(ignorei)
                        expr_tokens.append(tku)
                        continue
                    if tku.value=="}":
                        brackets-=1
                        ignorei+=1
                        ignore.append(ignorei)
                        expr_tokens.append(tku)
                        continue
                    if brackets==0:
                        ignorei+=1
                        ignore.append(ignorei)
                        break
                    ignorei+=1
                    ignore.append(ignorei)
                    expr_tokens.append(tku)
                expr_tokens=expr_tokens[1:-1]
                jit(expr_tokens,depth=True,infunc=True)
                funcs[tokens[i+1].value]=expr_tokens
            elif x.type=="exec":
                if x.value not in funcs:
                    exit(f"function {x.value} has not been defined")
            else:
                exit(f"Token {x.value} of type {x.type} was not found to be ignored")
    if_i=0
    cc_funcs=funcs
    cc_if_s=if_s
    cc_symbol_table=symbol_table
    if not depth:
        symbol_table={}
        if_s,funcs,if_i=0,0,0
    return {"funcs":cc_funcs,"ifs":cc_if_s,"symbol_table":cc_symbol_table}

def ignorerep(start,reps):
    out=[]
    for x in range(reps):
        out.append(start+x+1)
    return out

def token_to_expr(tokens):
    expr=""
    for x in tokens:
        expr+=(x.value+" ")
    return expr

def compiler(tokens,jitcode,depth=False):
    global indents,func_i,if_i,compiled
    if "indents" not in globals().keys():
        indents=0
        func_i=-1
        if_i=-1
        compiled=""
    def add_compile(code):
        global compiled
        compiled+=(("    "*indents)+code+"\n")
    if not depth:
        i=-1
        for x in tokens:
            i+=1
            if x.value[0]=="&":
                x.value=f"len({x.value[1:]})"
            elif x.type=="arr_call":
                if isnum(x.value.split(',')[1]) or (x.value.split(',')[1] in jitcode["symbol_table"] and jitcode["symbol_table"][x.value.split(',')[1]][0]==type(1)):
                    x.value=f"{x.value.split(',')[0]}[{x.value.split(',')[1]}]"
                else:
                    exit(f"Non Integer type property '{x.value.split(',')[1]}' was used to look up array")
            elif x.type=="dict_call":
                x.value=f"{x.value.split(',')[0]}[{x.value.split(',')[1]}]"
    ignore=[]
    i=-1
    for x in tokens:
        i+=1
        if i not in ignore and x.value!=";":
            if x.type=="sys" and x.value in ["str","int","float","arr","dict"]:
                add_compile(f"globals()['{tokens[i+1].value}']={absolute_defaults(str2type(x.value))}")
                ignore.append(i+1)
            elif x.type=="var" and tokens[i+1].value=="=":
                expr=""
                ignorei=i+1
                expr_tokens=[]
                for tk in tokens[i+2:]:
                    if tk.value==";":
                        break
                    ignorei+=1
                    ignore.append(ignorei)
                    expr_tokens.append(tk)
                    expr+=(tk.value+" ")
                ignore.append(i+1)
                add_compile(f"globals()['{x.value}']={expr}")
            elif x.type=="arr_init":
                add_compile(f"globals()['{tokens[i+1].value}']=[{absolute_defaults(str2type(x.value.split(',')[0]))}]*{x.value.split(',')[1]}")
            elif x.value=="if":
                if_i+=1
                add_compile("if "+token_to_expr(jitcode["ifs"][if_i]['condition'])+":")
                indents+=1
                compiler(jitcode["ifs"][if_i]['code'],jitcode,True)
                indents-=1
                ignore+=ignorerep(i,len(jitcode["ifs"][if_i]['code'])+len(jitcode["ifs"][if_i]['condition'])+4)
            elif x.value=="function":
                add_compile(f"def {tokens[i+1].value}():")
                indents+=1
                pre_compile=compiled
                compiler(jitcode["funcs"][tokens[i+1].value],jitcode,True)
                if compiled==pre_compile:
                    add_compile("pass")
                indents-=1
                add_compile(f"globals()['{tokens[i+1].value}']={tokens[i+1].value}")
                ignore+=ignorerep(i,len(jitcode["funcs"][tokens[i+1].value])+2)
            elif x.type=="arr_call":
                ignore.append(i+1)
                expr=""
                ignorei=i+1
                expr_tokens=[]
                for tk in tokens[i+2:]:
                    if tk.value==";":
                        break
                    ignorei+=1
                    ignore.append(ignorei)
                    expr_tokens.append(tk)
                    expr+=(tk.value+" ")
                add_compile(f"globals()['{x.value.split(',')[0]}'][{x.value.split(',')[1]}]={expr}")
            elif x.type=="dict_init":
                add_compile(f"globals()['{tokens[i+1].value}']="+"{}")
                ignore.append(i+1)
            elif x.type=="dict_call":
                expr=""
                ignorei=i+1
                for tk in tokens[i+2:]:
                    if tk.value==";":
                        break
                    ignorei+=1
                    ignore.append(ignorei)
                    expr+=(tk.value+" ")
                ignore.append(i+1)
                add_compile(f"{x.value}={expr}")
            elif x.type=="exec":
                add_compile(f"{x.value}()")
    cc_compiled=compiled
    if not depth:
        indents,func_i,if_i=0,0,0
        compiled=""
        return cc_compiled,sum([x.fees for x in tokens])
    return cc_compiled

def run(script,debug=True):
    script=("int txamount;str txcurr;str txrecvr;"+script).replace(";",";;")
    try:
        tokenz=tokeniser(script)
        return compiler(tokenz,jit(tokenz))
    except:
        if debug:
            import traceback
            traceback.print_exc()
        return False,False