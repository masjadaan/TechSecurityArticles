# What is the password
* * *

## Test Environment

**Target Machine**
- Ubuntu (16.04.7 LTS (Xenial Xerus), x86_64 GNU/Linux)
- gcc

**Attacker Machine**
- Kali x86_64 GNU/Linux Rolling
- gdb

## Introduction

When it comes to securing passwords, several industry standards and guidelines strongly advise against storing passwords in plain text. Instead, the emphasis is on employing strong, slow-to-compute hash functions for password hashing. The rationale behind this is quite significant; storing passwords directly in compiled binaries poses a serious security risk. This means that if someone gains access to the binary file, they potentially have access to the actual passwords. To demonstrate the real-world impact of this vulnerability, we've created a simple C program "letmein" purposely designed with vulnerabilities, storing passwords in plain text. We then compiled it using GCC without adding any extra layers of protection. Let's dive into the details and see how we can read the password.

## letmin Program
"letmein: A straightforward C program uses a basic password authentication. The program simply accepts a user-provided password via the command-line argument. Upon receiving the input, the main function invokes the authenticate function, which, in turn, compares the user-entered password with a predefined one obtained through the get_password() function. If the passwords match, a flag message is displayed through the flag() function; otherwise, an error message signals an incorrect password. In essence, this program serves as a practical demonstration of password authentication and serves as a demonstration for our objective in this article.
```C
#include <stdio.h>
#include <string.h>
#include "secret.h"

void flag(){
	printf("Here is your flag: Y0u 4r3 4w3$0m3 \n");
}
void authenticate(char* user_input){

	char buf[16];
	const char* password = get_password();
	strcpy(buf, user_input);
	if (strcmp(buf, password) == 0)
		flag(); // equal
	else
		printf("Incorrect Passowrd. Try again... \n"); // unequal
}


int main(int argc, char* argv[]){

	if (argc != 2) {
		printf("Usage: %s <password>\n", argv[0]);
		return 1;
	}
	
	authenticate(argv[1]);

	return 0;
}
```

Let's take a closer look at how this program works. When we run it without any arguments, a friendly usage message appears, telling us that the program expects a password as input. Now, when we provide a random password, the program replies with a message saying, 'Incorrect Password. Try again...'  which means that the password we supplied does not match the expected value."
```sh
./letmein
Usage: ./letmein <password>

./letmein mysecret
Incorrect Passowrd. Try again... 
```
![f861a761f5e80458d5b25f58daa517b9.png](:/6b8a1ca1e09845089fd0b22f951ced6c)

## Give me the password
"As reading the letmein.c source code, you might have noticed the absence of the get_password() function implementation. This omission is intentional; when you run the 'strings' command on the letmein binary, the password won't be revealed. However, a closer look reveals the inclusion of the "secret.h" header, suggesting that get_password() is defined in an external library dynamically linked to the letmein program during runtime.

Our goal here is to access the password during runtime. At this stage of execution, the password gets copied from its external source into a register. To uncover this process, let's turn to our friend the GDB.

### GDB Debugging
In this example, we have the source code for letmein program, however, even if we don't have, we could start by disassembling the main function. Alternatively, we could list all the functions and look for those we deem potentially relevant. Our primary objective is to pinpoint the moment when the password gets copied into any registers. I'll try to stick to the basic approach, so let's just disassemble the main function:
```sh
gdb -q letmein
pwndbg> disassemble main

```
![c086bf6c9d2acec03ba9cf1fefe51b4f.png](:/121d719de5d54838aafcb163b9a9b7f4)

As you can see in the image above, within the main function, there's a call to the authenticate() function located at address 0x400867. Let's trace this call and proceed to disassemble the authenticate() function for a closer examination.
```sh
pwndbg> disassemble authenticate
```
![956b16ed117545b2854b4efc90007455.png](:/a4fda75bfa8948fc862b96dcc12e8b94)

When examining the authenticate function code, interestingly, there are two methods to obtain the password. Can you take a guess before we delve into it?

At address 0x4007d8, there's a call to the get_password function, and judging by its name, it implies that it returns the password. Considering the "Calling Convention", where the return value is typically passed in the RAX register (without going into too many details), our initial method to extract the password involves setting a breakpoint immediately after the get_password function returns. We can then inspect the content of the RAX register. Let's set up this breakpoint and run the program with a random password, say 'AAAAAAAA'."

```sh
break *0x00000000004007dd
run AAAAAAAA
```
![706b00cd9b808ce9bd26ee49aef3280d.png](:/8f826a66271346fe956bbf29cd8d511c)

The execusion should be halted at the breakpoint and when examining RAX register, we can see the password
```sh
pwndbg> x/s $rax
0x7ffff7c00679: "p4ssw0rd"
```
![ab528e8e987351afaeae5f88f97ffff7.png](:/4f45cd7c59054625a167e9f41b1536e9)

The second approach involves recognizing that the strcmp function takes our provided password as its first argument and the stored password as its second argument. We also know form the "Calling Convention" that the first six arguments to a function are passed in registers in the following order:
|Register| Argument Number|
| -- | -- |
|RDI | First argument |
|RSI | Second argument|
|RDX | Third argument |
|RCX | Fourth argument|
|R8  | Fifth argument |
|R9  | Sixth argument |

This implies that we can set a breakpoint just before the call to strcmp. By adding a condition based on the value of register RDI, we can ensure that the execution pauses at strcmp only when the RDI value matches our input, thereby revealing the password stored in register RSI. To see this in action, let's set up the breakpoint. Examining the authentication assembly code, we identify that strcmp is located at address 0x400802. After setting the breakpoint, we can resume the execution, considering we previously paused at a different breakpoint—simply type 'continue' to proceed.
```sh
break *0x400802 if strcmp((char *)$rdi, "AAAAAAAA") == 0
continue
```
![74aee3099936644c8fefff5677593ead.png](:/605c1d665d184b889075386205250cdd)

You can also examin the value in register RSI itself by running the command
```sh
x/s $rsi
```
![100a1333933f89beb0cf07c33cbeffa7.png](:/689bb5f0175a494e892b45ebb0f6a9c9)

Now we know the password, so lets run our program and supply the correct password
```
./letmein p4ssw0rd
```
![db2dd59abbd2f2d863e0b9f91c210b44.png](:/7fb9527e06cf49c29e5316ce52da88c2)


Happy Learning...

### Apendix A
If you wish to follow along, we've included the secret.c file, which will be compiled as a library, along with the secret.h header file. You should already have the letmein.c file. With these files in place, you're all set for compilation. Just follow these commands:

#### secret.c
```C
char* get_password(){
	return "p4ssw0rd";
}
```

#### secret.h
```C
#ifndef SECRET_H
#define SECRET_H

char* get_password();

#endif
```

#### Compilation
```sh
gcc -fPIC -shared secret.c -o libsecret.so
gcc letmein.c -L. -lsecret -Wl,-rpath=. -z execstack -fno-stack-protector -o letmein
```

![edaa317db701fd4f954edd1011ae8fac.png](:/5c7fb4db2e09457090748461b45c5758)
