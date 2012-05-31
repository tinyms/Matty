/* 
 * File:   IO.cpp
 * Author: tinyms
 * 
 * Created on 2012年6月1日, 上午1:51
 */

#include "IO.h"
void IO::ReadTextFile(std::string path, std::string& content){
    ifstream file;
    file.open(path.c_str());
    if(file.is_open()){
        std::string tmp;
        while(file.good()){
            getline(file,tmp);
            content+=tmp+"\n";
        }
        file.close();
        cout<<content<<endl;
    }
}
void IO::WriteTextFile(std::string path, std::string& content){
    ofstream file;
    file.open(path.c_str());
    if(file.is_open()){
        file<<content;
    }
    file.close();
}
IO::IO() {
}

IO::IO(const IO& orig) {
}

IO::~IO() {
}

