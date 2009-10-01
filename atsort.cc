#include <cctype>
#include <map>
#include <vector>
#include <limits>
#include <string>
#include <cstdio>
using namespace std;

typedef vector<pair<string,long> > v_t;
struct tcomp {
  bool operator() (const v_t & a, const v_t & b) {
    v_t::const_iterator i = a.begin();
    v_t::const_iterator j = b.begin();
    for(; 
	i != a.end() && j != b.end(); ++i, ++j) {
      
      if(i->second != -1 && j->second != -1) {
	if(i->second < j->second) return true;
	if(i->second > j->second) return false;
      } else {
	if(i->first < j->first) return true;
	if(i->first > j->first) return true;
      }
    }
    return i == a.end() && !(j == b.end());
  }
};

int main(int argc, char ** argv) {
  char line[1024*1024];
  multimap< v_t, string, tcomp> lines;
  bool sep[256];
  bool skip[256];
  for(int i=0; i < 256; ++i) sep[i]=skip[i] = false;
  const char * s = "/-.,_[]{}()@#$\t \n";
  for(int i=0; s[i]; ++i) sep[s[i]] = true;
  skip[' '] = skip['\t'] = skip['\n'] = true;

  while(fgets(line,1024*1024-1,stdin)) {
    line[1024*1024-1] = '\0';
    v_t x;
    string tok;
    for(int i=0; line[i]; ++i) {
      char c=line[i];
      if(sep[c]) {
	if(tok.size()) x.push_back(make_pair(tok,-1));
	tok="";
	if(!skip[c]) x.push_back(make_pair(string(1, c),-1));
      } else if('0' <= c && c <= '9') {
	if(tok.size()) x.push_back(make_pair(tok,-1));
	tok="";
	long n=c - '0';
	for(; '0' <= line[i] && line[i] <= '9'; ++i) {
	  n = n * 10 + (line[i]-'0');
	  tok.push_back(line[i]);
	}
	x.push_back(make_pair(tok,n));
	tok="";
      } else 
	tok.push_back(tolower(c));
    }
    lines.insert( make_pair( x, string(line) ) );
  }
  for(multimap< v_t, string, tcomp>::iterator i=lines.begin(); 
      i != lines.end(); ++i) 
    fputs(i->second.c_str(), stdout);
  
}
