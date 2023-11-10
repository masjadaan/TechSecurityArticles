# ShellCodes
* * *
Shellcode is a set of machine code instructions typically written in assembly language such as x86, designed to be executed directly by a computer's processor. Because assembly's instructions are architecture-specific that restricts the portability of shellcodes among different processors. In general, shellcode focuses on direct manipulation of processor registers, configuring them for various system calls using opcodes. Once the assembly code is crafted to execute the desired operation, then it must be converted into machine code. However, this will not be enough, removing all null bytes is crucial. The reason is that many string operations, such as strcpy(), stop when encountering null bytes.

To better understand shellcodes, let's examine first System Calls (syscall)

## System Calls (syscall)

To invoke functions for tasks like opening system ports or modifying permissions, it's essential to utilize system calls, which serve as a means to manage communication with hardware and access kernel functionality that might not be present in the application's address space. On UNIX-based operating systems, each function is assigned a unique system call number. 

For instacne, when a user-level program needs to access a function beyond its address space, such as setuid(), it must first determine the system call number associated with setuid() function. Then, it triggers an interrupt which signals to the operating system that a request needs attention. The actual numbers assigned to each system call can vary between operating systems. In Linux, for instance, syscall numbers are defined in the kernel headers. One esay way to get the system call number is to use `ausyscall` tool
```sh
# Ubuntu
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
