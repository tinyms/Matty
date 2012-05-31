/* 
 * File:   IO.h
 * Author: tinyms
 *
 * Created on 2012年6月1日, 上午1:51
 */

#ifndef IO_H
#define	IO_H
#include <string>
#include <iostream>
#include <fstream>
using namespace std;
class IO {
public:
    static void ReadTextFile(string path, string& content);
    static void WriteTextFile(string path, string& content);
public:
    IO();
    IO(const IO& orig);
    virtual ~IO();
};

#endif	/* IO_H */

