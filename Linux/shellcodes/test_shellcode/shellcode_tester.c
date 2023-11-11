char shellcode[] = "";

void main(){
  //cast the shellcode array to a function pointer
  ((void (*)(void))shellcode)();
}
