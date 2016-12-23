
#include <stdio.h>
#include <stdlib.h>

#define White 0 
#define Black 1 
#define Empty 2 
#define BW 15

void main()
{
	FILE *fp1 = fopen("input.txt","w");
	FILE *fp2 = fopen("output.txt","w");
	FILE *fp3 = fopen("result.txt","w");
	FILE *fp4 = fopen("result_w.txt","w");

	int i;

	fprintf(fp1,"1\n"); // init input.txt
	for(i=0;i<BW*BW;i++)
	{
		fprintf(fp1,"2");
		fprintf(fp1,"\n");
	}

	i = BW*BW/2;
	fprintf(fp2,"1\n"); // init output.txt
	fprintf(fp2,"%d 1\n",i);
	fclose(fp1);
	fclose(fp2);
	fclose(fp3);
	fclose(fp4);
}