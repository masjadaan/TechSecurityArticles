# ShellCodes
* * *
Shellcode is a set of machine code instructions typically written in assembly language such as x86, designed to be executed directly by a computer's processor. Assembly code's architecture-specific nature restricts its portability across different processor types. Shellcode primarily focuses on direct manipulation of processor registers, configuring them for various system calls using opcodes. Once the assembly code is crafted to execute the desired operation, it must undergo conversion into machine code while ensuring the removal of any null bytes. Eliminating null bytes is crucial because many string operations, such as strcpy(), halt when encountering them.

The versatility of shellcode allows it to perform a wide range of actions within the context of the compromised program. Common applications of shellcode include establishing a network shell on a listening port of a system, initiating a reverse shell connection to a remote system, and more.

## System Calls

To invoke functions for tasks like opening system ports or modifying permissions, it's essential to utilize system calls. On UNIX-based operating systems, each function is assigned a unique system call number. System calls serve as a means to manage communication with hardware and access kernel functionality that might not be present in the application's address space.

When a user-level program needs to access a function beyond its address space, such as setuid(), it must first determine the system call number associated with the desired function. Subsequently, it triggers an interrupt 0x80 (int 0x80). The instruction int 0x80 is an assembly instruction commonly used to invoke system calls in many UNIX-like operating systems. This interrupt serves as a signal to the operating system, informing it of an event or request.

In the case of most system calls, one or more arguments are necessary. The system call number is loaded into the EAX register, while the arguments intended for the desired function are typically loaded into EBX, ECX, and EDX, following a specific order. In 64-bit architecture, the arguments for system call are placed in rdi, rsi, rdx, rcx, r8 and r9 in that order.

A comprehensive list of system call numbers can be found in:
```sh
cat /usr/include/asm-generic/unistd.h
# OR
cat /usr/include/asm-i386/unistd.h
```

### Example: Calling exit() function with argument 0 (exit(0))
```
# Find the syscall number
cat /usr/include/asm-generic/unistd.h | grep -i exit
	#define __NR_exit 93
	__SYSCALL(__NR_exit, sys_exit)

mov eax, 93 # syscall number
mov ebx, 0  # argument
int 0x80    # interrupt
```
