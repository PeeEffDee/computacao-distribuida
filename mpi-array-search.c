#define MAXSIZE 20

#include "mpi.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void found(int element, int line, int myid) {
   char hostname[30];
   gethostname(hostname, 30);
   printf("I found %d at line %d from %d-%s\n", element, line, myid, hostname);
}

int main(int argc, char **argv)
{
	int myid, numprocs, element;
	int data[MAXSIZE], i, x, low, high, my_position=0, position=0;
	FILE *fp;
	element = atoi(argv[1]);

	MPI_Init(&argc,&argv);
	MPI_Comm_size(MPI_COMM_WORLD,&numprocs);
	MPI_Comm_rank(MPI_COMM_WORLD,&myid);

	if (myid == 0) { /* Open input file and initialize data */
		if ((fp = fopen("data/rand.txt","r")) == NULL) {
			printf("Can't open the input file: rand.txt\n\n");
			exit(1);
		}
		for (i = 0; i < MAXSIZE; i++) fscanf(fp,"%d\n", &data[i]);
	}
	
   MPI_Bcast(data, MAXSIZE, MPI_INT, 0, MPI_COMM_WORLD); /* broadcast data */
	x = MAXSIZE/numprocs; /* Add my portion Of data */
	low = myid * x;
	high = low + x;

   my_position = -1;
	for(i = low; i < high; i++)
		if (element == data[i]) {
         found(element, i+1, myid);
         my_position = i+1; /* count start at 0 */
      }

   if (myid == 0) {
      int buffer[numprocs];
      MPI_Gather(&my_position, 1, MPI_INT, buffer, 1, MPI_INT, 0, MPI_COMM_WORLD);

      position = -1;
      for (i = 0; i < numprocs; i++)
         if (buffer[i] != -1)  {
            position = buffer[i];
            break;
         }
      
      printf("Position: %d\n", position);
   }
   else {
      MPI_Gather(&my_position, 1, MPI_INT, NULL, 0, MPI_INT, 0, MPI_COMM_WORLD);
   }

	MPI_Finalize();
	return 0;
}
