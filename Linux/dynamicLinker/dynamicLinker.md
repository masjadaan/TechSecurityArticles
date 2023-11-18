# Dynamic Linker
***


- It loads and links shared libraries at runtime when an executable program is executed

## Dynamic Linking
- When a program is compiled, it can use:
	- Static Linking
		- all exteral libraries are in one file
	- Dynamic Linking
		- allows multiple programs to share common libraries
		- reducing disk space usage and
		- making it easier to update libraries without recompiling program

* * *

## Global Offset Table
The Global Offset Table (GOT) is a data structure used in the ELF (Executable and Linking Format) binary file format. The primary function of the GOT is to store addresses of global symbols and facilitate the resolution of function and data references at runtime, particularly when using shared libraries. During program runtime, the dynamic linker populates the Global Offset Table. The dynamic linker acquires the absolute addresses of requested functions and updates the GOT as needed. The beauty of this approach is that files do not necessitate being relocatable, as the GOT handles location requests initiated from the Procedure Linkage Table (PLT). Furthermore, it's important to note that numerous functions may remain unresolved until the first invocation of the requested function. This practice, termed lazy linking, offers resource-saving benefits. When OS applies Address Space Layout Randomization ASLR, addresses are randomized when a program is loaded inot memory, so you cannot use a static address
***

## Procedure Linkage Table (PLT)
The Procedure Linkage Table (PLT) is a read-only data structure found in the ELF (Executable and Linking Format) binary file format. Its primary function is to facilitate the dynamic linking process, which occurs during and after program runtime, enabling the resolution of addresses for requested functions. This dynamic resolution is necessary because the addresses of functions from shared libraries are not known during compile time. Instead, the resolution is deferred until the first time a call to the requested function is made.

Each program possesses its own unique PLT, which is exclusively useful for that program. When a function's address needs to be resolved, the calling function makes a request to the PLT. This request results in the address of the Global Offset Table (GOT) being pushed into a processor register. To provide a high-level overview of the process:

- Step 1: The program initiates a function call to one residing within a shared library, necessitating the retrieval of the absolute memory address, as in the case of calling printf().

- Step 2: The calling program is required to load the address of the Global Offset Table (GOT) into a register. This step is essential because relocatable sections may exclusively contain Relative Virtual Addresses (RVAs).

-  Step 3: Building on step 1, the request is forwarded to the Procedure Linkage Table (PLT). The PLT then directs control to the corresponding entry in the Global Offset Table (GOT) associated with the requested symbol. If this marks the first instance of requesting the function, proceed to the following step; otherwise, skip ahead to step 5.

- Step 4: As this represents the initial request for the function, control transitions from the Global Offset Table (GOT) back to the Procedure Linkage Table (PLT). This transition is achieved by first loading the address of the relative entry within the relocation table, a critical piece of information utilized by the dynamic linker for symbol resolution. Subsequently, the PLT invokes the dynamic linker to resolve the symbol. Once the resolution is successfully completed, the address of the requested function is inserted into the corresponding GOT entry.

-  Step 5: If the Global Offset Table (GOT) already retains the address of the requested function, control can swiftly proceed without requiring the intervention of the dynamic linker.
***

## Example
- Create an ELF file
```C
#include <stdio.h>

void main() {
    printf("Hello, Dynamic Linker!\n");
}
```

- Compile
```sh
# compile linker.c
gcc linker.c -o linker

# check the created file
file linker
```


### Symbol Resolution At Runtime
