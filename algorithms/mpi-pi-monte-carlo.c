/* 

*/

#define _XOPEN_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>
#include <time.h>

int main(int argc, char ** argv) {

	int i;
	double x,y,quad;
	long local_num_ptos = 0.0;      /* num pontos gerados */
	long local_num_ptos_cir = 0.0;  /* num pontos no circulo */
	double local_pi, total_pi;
	long total_num_ptos = 0.0, total_num_ptos_cir = 0.0;
   int numint;               			/* recebe da linha de comando o num de pontos */
	numint = atoi(argv[1]);
	int my_rank, comm_sz, source;	  	/* variaveis do MPI */

	MPI_Init(NULL, NULL);
	MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);
	MPI_Comm_size(MPI_COMM_WORLD, &comm_sz);

	srand48(time(NULL) + my_rank);
	printf("Calculating from process %d of %d\n", my_rank, comm_sz);
	for (i = 0; i<numint; i++) {
      x = drand48();
      y = drand48();
		// printf("x = %f and y = %f\n", x, y);

		quad = ((x*x) + (y*y));
		if (quad <= 1) {
			local_num_ptos_cir ++;
		}
 
		local_num_ptos++;
	}

	if (my_rank != 0) {
		/* Send messages do process 0 */
		MPI_Send(&local_num_ptos, 1, MPI_LONG, 0, 0, MPI_COMM_WORLD);
		MPI_Send(&local_num_ptos_cir, 1, MPI_LONG, 0, 0, MPI_COMM_WORLD);
	} else {
		/* Receive messages */
		total_num_ptos = local_num_ptos;
		total_num_ptos_cir = local_num_ptos_cir;
		for (source = 1; source < comm_sz; source++) {
			MPI_Recv(&local_num_ptos, 1, MPI_LONG, source, 0,
				MPI_COMM_WORLD, MPI_STATUS_IGNORE);
			MPI_Recv(&local_num_ptos_cir, 1, MPI_LONG, source, 0,
				MPI_COMM_WORLD, MPI_STATUS_IGNORE);
			total_num_ptos += local_num_ptos;
			total_num_ptos_cir += local_num_ptos_cir;
		}

		total_pi = (4.0 * total_num_ptos_cir) / total_num_ptos;
	}

   if (my_rank == 0) {
      printf("With n = %d points in %d clusters, our estimate\n", numint, comm_sz);
      printf("of the number Pi is = %.15e\n", total_pi);
	}

	MPI_Finalize();
	return 0;
}