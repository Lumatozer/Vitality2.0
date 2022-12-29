# Vitality
Vitality is a compiled statically typed smart contract language used primarily for smart contracts on the LTZ-Chain.\
The engine which compiles vitality is called Vengine (Vitality Engine).
## Example
```python
import vengine
code=vengine.run("""
num x;
""")
print(code)
```
## Basics
To create a variable and assign a value to it
```python
num x;
str y;
```
To create a class
```python
struct name {
    type : varname,
    type : varname,
};
```
Example
```py
struct test {
    num : a,
    str : b,
};
```
How to spawn an object
```python
spawn class[varname];
```
Example
```python
spawn test[x];
```
To change a variable's value.
```c
y=1234;
y='Hello, World';
z=1234.1234;
```
## Pre Assigned Variables
When a smart contract is invoked, 4 variables are injected into the code.
```python
1. txsender (Address of Invoker)
2. txamount (Amount sent to contract)
3. txmsg (Data provided along with transaction)
4. txcurr (Currency of transaction)
5. txto (Send a tx from the transaction to this address)
```
To create an array
```c
# Syntax (type)[{length<=256}] (var_name);
num[] alu;
```
To assign a value at index of an array
```c
alu[0]=8;
```
Lookup Method
```c
x=alu[0];
```
Nested lookup for objects
```c
object.var;
```
Example
```c
1. test.x=1;
2. y=test.x+7;
```
To create a dictionary
```c
# Syntax (key_type){}(value_type) (var_name);
str{}num book;
```
To assign a value in a dictionary
```c
book['page 1']=1;
```
Lookup Method
```c
y=book['page 1'];
```
To create a function
```python
function (function name) {(function_code)};
```
Example
```python
function main {
    num x;
};
```
To execute Functions;
```python
func_name();
```
If Statements
```c
if (condition) {code};
```
Example
```c
if (1==1) {
    num pew;
}
```

## Sending a Transaction
To send a transaction we can change the 'txto' env variable's value to a non empty string. After the execution the amount in the 'txamount' variable and the currency inside the 'txcurr' variable will be used to send money to the address in 'txto' variable.
```python
if (txamount > 1) {
    txto=txsender;
    txamount=1.0;
};
```
# Examples
1. Domain based tx forwarding
```python
if ('domains' not in vars) {
    str{}str domains;
};
if (txmsg not in domains) {
    domains{txsender}=txmsg;
    txto='';
};
if (tsmsg in domains) {
    txto=domains{txsender};
};
```