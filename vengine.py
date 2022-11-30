class token:
    def __init__(self,type,value):
        if type=="var" and "[" in value and "]" in value:
            type="arr_call"
            value=f'{value.split("[")[0]},{value.split("[")[1].split("]")[0]}'
        if type=="var" and value[0]=="&":
            type="len"
        self.type=type
        self.value=value


operators=["=","-","+","*","/","!"]
protected=["function","int","float","str","int[]","float[]","str[]"]

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
        return "set_bracket"
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
    if tkn.value in ["[","]",",",":","{","}","(",")"]:
        return tkn.value
    if tkn.type=="num":
        return "1"
    if tkn.type=="str":
        return "''"
    if tkn.type=="var":
        return gettypedefaults(symbol_table[tkn.value][0])
    if tkn.type=="sys":
        return ""
    if tkn.value in operators:
        return tkn.value
    if tkn.type=="len":
        return "1"
    if tkn.type=="arr_call":
        return gettypedefaults(symbol_table[tkn.value.split(",")[0]][1])

def str2type(x):
    if x=="str":
        return type("")
    if x=="int":
        return type(1)
    if x=="float":
        return type(1.0)
    
def evaluate_out_type(tokens):
    expr=""
    for x in tokens:
        expr+=getdefaults(x)+" "
    return type(eval(expr))

def append_token(tkn):
    global last_token
    global tokens
    last_token=tkn
    tokens.append(last_token)

def tokeniser(script):
    global tokens
    tokens=[]
    last_token=token("","")
    cache=""
    state=""
    for x in script.replace("\n",""):
        if (state=="sys" and x in ["(",")","'"]+operators and cache in protected):
            print(x)
            state=""
            append_token(token(getsystype(cache),cache))
            cache=""
            continue
        if x==" " and state=="" and cache=="":
            continue
        if x=="(" and state=="":
            append_token(token("bracket",x))
            continue
        if x==")" and state=="":
            append_token(token("bracket",x))
            continue
        if x=="{" and state=="":
            append_token(token("set_bracket",x))
            continue
        if x=="}" and state=="":
            append_token(token("set_bracket",x))
            continue
        if x=="[" and state=="":
            append_token(token("arr_bracket",x))
            continue
        if x=="]" and state=="":
            append_token(token("arr_bracket",x))
            continue
        if x=="," and (state=="sys" or state=="" or state=="num"):
            if cache!="" and state in ["str","num"]:
                append_token(token(state,cache))
                cache=""
                state=""
            append_token(token("comma",x))
            continue
        if x==":" and (state=="sys" or state=="" or state=="num"):
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
            if x=="=" and last_token=="=":
                del tokens[len(tokens)-1]
                append_token(token("operator","=="))
                continue
            if x=="=" and last_token=="!":
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
            append_token(token("str",cache))
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
                    continue
                else:
                    append_token(token("var",cache))
                    cache=""
                    state=""
            append_token(token("eol",";"))
            continue
        cache+=x
        state="sys"
    return tokens

def typeerror(var1,type1,type2):
    print(f"Cannot assign variable {var1} of type {type1} a value of type {type2}")
    exit()

def undefinederror(var):
    print(f"'{var}' was not defined")
    exit()

def validvar(var):
    whitelist="abcdefghijklmnopqrstuvwxyz"
    whitelist+=whitelist.upper()
    whitelist+="1234567890_"
    for x in var:
        if x not in whitelist: return False
    return True

def compiler(tokens):
    i=-1
    ignore=[]
    global symbol_table
    if "symbol_table" not in globals().keys():
        symbol_table={}
    for x in tokens:
        i+=1
        if i not in ignore and x != ";":
            if x.type=="var" and tokens[i+1].value=="=":
                if x.value not in symbol_table:
                    undefinederror(x.value)
                expr=""
                expr_tokens=[]
                for tk in tokens[i+2:]:
                    if tk.value==";":
                        break
                    expr_tokens.append(tk)
                    expr+=(tk.value+" ")
                x_type=evaluate_out_type(expr_tokens)
                if x.value in symbol_table:
                    if symbol_table[x.value][0]!=x_type:
                        typeerror(x.value,symbol_table[x.value],x_type)
                ignore.append(i+1)
                continue
            if x.type=="sys" and x.value in ["str","float","int","str[]","float[]","int[]"] and validvar(tokens[i+1].value):
                if not (tokens[i+1].value not in symbol_table ):
                    print(f"'{tokens[i+1].value}' has already been declared")
                    exit()
                if not (tokens[i+1].type=="var"):
                    print(f"Cannot declare token '{tokens[i+1].value}' of type {tokens[i+1].type}")
                    exit()
                ignore.append(i+1)
                if "[]" not in x.value:
                    symbol_table[tokens[i+1].value]=[str2type(x.value),None]
                else:
                    symbol_table[tokens[i+1].value]=[type([]),str2type(x.value.split("[]")[0])]
                continue
tkz=tokeniser(open("alu.vtl").read())
if 1==0:
    for x in tkz:
        print(x.value,x.type)
else:
    compiler(tkz)
    print(symbol_table)