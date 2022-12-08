# Vitality
Vitality is a compiled statically typed smart contract language used primarily for smart contracts on the LTZ-Chain.\
The engine which compiles vitality is called Vengine (Vitality Engine).
## Example
```python
import vengine
code=vengine.run("""
int x;
""")
print(code)
```
## Basics
To create a variable and assign a value to it
```python
int x;
str y;
float z;
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
```
To create an array
```c
# Syntax (type)[{length<=256}] (var_name);
int[1] alu;
```
To assign a value at index of an array
```c
alu[0]=8;
```
Lookup Method
```c
x=alu[0];
```
To create a dictionary
```c
# Syntax (key_type){}(value_type) (var_name);
str{}int book;
```
To assign a value in a dictionary
```c
book{'page 1'}=1;
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
    int x;
};
```
To execute Functions;
```python
func_name();
```
If Statements
```c
if (condition) (code)
```
Example
```c
if (1==1) {
int pew;
}
```