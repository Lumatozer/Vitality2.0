script="""
function main ();
alu = [];
"""
class token:
    def __init__(self,type,value):
        self.type=type
        self.value=value
operators=["=","-","+","*","/","!"]
protected=["function"]
tokens=[]
cache=""
state=""
last_token=token("","")
def append_token(tkn):
    global last_token,tokens
    if tkn.value=="":
        print(last_token.value)
    last_token=tkn
    tokens.append(last_token)

def isnum(check):
    try:
        int(check)
        return True
    except:
        return False

for x in script.replace("\n",""):
    if (state=="sys" and x in ["(",")","'"]+operators and cache in protected) or isnum(x):
        state=""
        append_token(token("sys",cache))
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
    if x in operators and state=="":
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
        append_token(token("string",cache))
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
    if x==" " and state=="num":
        append_token(token("num",cache))
        cache=""
        state=""
        continue
    if x==" " and (state=="" or state=="sys") :
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
            append_token(token(state,cache))
            cache=""
            state=""
        append_token(token("eol",";"))
        continue
    cache+=x
    state="sys"
print("-"*20)
for x in tokens:
    print(x.value,x.type)