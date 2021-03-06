#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <mpi.h>

int primo(int numero) {
   int raiz, fator;
   raiz = (int) sqrt((double) numero);

   if (numero == 0 || numero == 1) 
      return 0;

   for(fator = 2; fator <= raiz; fator++) {
      if (numero % fator == 0) {
         return 0;
      }
   }

   return 1;
}

int main(int argc, char **argv) {
   clock_t start, end;
   double cpu_time_used;

   start = clock();

   int LIMITE;
   int INICIO;
   int my_rank, comm_sz, source; /* MPI variables */
   int total_inspected, local_init, local_end;
   int local_qtde = 0, total_qtde = 0, numero;
   
   INICIO = atoi(argv[1]);
   LIMITE = atoi(argv[2]);

   MPI_Init(NULL, NULL);
   MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);
   MPI_Comm_size(MPI_COMM_WORLD, &comm_sz);

   total_inspected = (LIMITE-INICIO)/comm_sz;
   local_init = INICIO + total_inspected * my_rank;
   local_end = local_init + (total_inspected-1);
   
   if (my_rank == comm_sz-1) local_end = LIMITE;

	// printf("Calculating from process %d of %d\n", my_rank, comm_sz);
   for (numero = local_init; numero <= local_end; numero ++) {  
      int p = primo(numero);
      if (p == 1) printf("%d\n", numero);
      local_qtde += p;
   }

   if (my_rank != 0) {
      // printf("%d: local_init = %d, local_end = %d\n", my_rank, local_init, local_end);

      MPI_Send(&local_qtde, 1, MPI_INT, 0, 0, MPI_COMM_WORLD);
   }
   else {
      // printf("%d: local_init = %d, local_end = %d\n", my_rank, local_init, local_end);

      total_qtde += local_qtde;
      for (source = 1; source < comm_sz; source++) {
         MPI_Recv(&local_qtde, 1, MPI_INT, source, 0,
				MPI_COMM_WORLD, MPI_STATUS_IGNORE);
         total_qtde += local_qtde;
      }
   }
    
   if (my_rank == 0) {
      printf("Total de numeros primos de %d a %d: %d\n", 
         INICIO, LIMITE, total_qtde);

      end = clock();
      cpu_time_used = ((double) (end - start)) / CLOCKS_PER_SEC;
      printf("\nCPU time used = %f\n", cpu_time_used);
	}

   MPI_Finalize();
   return 0;
}