#include <stdio.h>
#include <math.h>
#include <time.h>

#define LIMITE 10

int primo(int numero) {
   int raiz, fator;
   raiz = (int) sqrt((double) numero);
   for (fator = 2; fator <= raiz; fator++)  
      if (numero % fator == 0)    
         return 0;
      return 1;
}

int main() {
   int quantidade = 0, numero;
   double dif; // tomada de tempo

   for (numero = 2; numero < LIMITE; numero ++) {  
      int p = primo(numero);
      quantidade += p;
   } 
   
   printf("Total de numeros primos ate %d: %d\n", 
      LIMITE, quantidade);
}