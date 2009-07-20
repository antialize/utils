/*
 * Downtracker tracking file sizes
 * Copyright (C) 2008 Jakob Truelsen
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
#include <unistd.h>
#include <stdio.h>
#include <pthread.h>
#include <error.h>
#include <errno.h>
#include <stdlib.h>

#define RS 30
#define MAXFILES 50

FILE * f[MAXFILES];
volatile long ns[MAXFILES];
long os[MAXFILES];
int pt[MAXFILES];
long chunksize;

int file_reader(int file) {
  char * buffer = (char *)malloc(chunksize);
  while(1) {
    int read = fread(buffer,1,chunksize,f[file]);
    ns[file] += read;
    if(pt[file]) fwrite(buffer,1,read,stdout);
  }
}

void fsize(double * size,char ** name) {
  *name = "B"; 
  if(*size < 1024.0) return;
  *size /= 1024.0;
  *name = "KB";
  if(*size < 1024.0) return;
  *size /= 1024.0;
  *name = "MB";
  if(*size < 1024.0) return;
  *size /= 1024.0;
  *name = "GB";
}

int main(int argc, char ** argv ) {
  long ring[MAXFILES][RS];
  long ru = 0;
  int rp;
  int file;
  long sum[MAXFILES];
  pthread_t thread;
  double speed;
  char * postfix;
  char * sizefix;
  double size;
  chunksize = 1024;
  if(argc > 2 && !strcmp(argv[1],"--chunksize")) {
      chunksize = atol(argv[2]);
      argv = &argv[2];
      argc -= 2;
  }

  for(file =0; file < argc -1; file++) {
    fprintf(stderr,"%s: N/A\n",argv[file+1]);
    for(rp = 0; rp < RS; rp++) ring[file][rp] = 0;
    sum[file] = 0;
    pt[file] = 0;
    if(!strcmp(argv[file+1],"--")) {
      f[file] = stdin;
      pt[file] = 1;
    } else if(!strcmp(argv[file+1],"-"))
      f[file] = stdin;
    else
      f[file] = fopen(argv[file+1],"rw");
    
    if(fseek(f[file],0,2) != 0 ) {
      os[file] = 0;	
      pthread_create( &thread, NULL, &file_reader, (void*)file);
    } else 
      os[file] = ftell(f[file]);
  }
  rp = 0;
  while(1) {
    sleep(1);
    fprintf(stderr,"\033[%dA", argc -1);
    if(ru < RS) ++ru;
    rp = (rp + 1) % RS;
    for(file =0; file < argc -1; file++) {
      if(fseek(f[file],0,2) == 0 ) 
	ns[file] = ftell(f[file]);
      
      sum[file] -= ring[file][rp];
      ring[file][rp] = ns[file] - os[file];
      sum[file] += ring[file][rp];

      speed = (double)sum[file]/(double)ru;
      fsize(&speed,&postfix);

      size = ns[file];
      fsize(&size,&sizefix);
      
      fprintf(stderr,"\r%-30s %8.2f %s/s    %8.2f %s\n ",argv[file+1],speed,postfix,size,sizefix);
      os[file] = ns[file];
    }
    fflush(stdout);
  }
}
