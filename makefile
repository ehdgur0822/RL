all : xlai xlhuman init_file

xlai : xlai.cpp xlai.h
	g++ xlai.cpp -o xlai

xlhuman : xlhuman.cpp xlhuman.h
	g++ xlhuman.cpp -o xlhuman

init_file : init.c
	gcc init.c -o init_file

clean: 
	rm -rf xlai init_file xlhuman *.pyc
