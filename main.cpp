/* 
 * File:   main.cpp
 * Author: tinyms
 *
 * Created on 2012年6月1日, 上午1:48
 */

#include <cstdlib>
#include <iostream>  
#include <string>
#include <ctemplate/template.h>
#include "Common/IO.h"
#include "Common/V8Engine.h"
using namespace std;
/*
 * 
 */
int main(int argc, char* argv[]) {
    if(argc>1){
        string script;
        IO::ReadTextFile(argv[1],script);
        V8Engine::Execute(script.c_str());
    }
    /**
    ctemplate::TemplateDictionary dict("example");
    int winnings = rand() % 100000;
    dict.SetValue("NAME", "John Smith");
    dict.SetIntValue("VALUE", winnings);
    dict.SetFormattedValue("TAXED_VALUE", "%.2f", winnings * 0.83);
    // For now, assume everyone lives in CA.
    // (Try running the program with a 0 here instead!)
    if (1) {
        dict.ShowSection("IN_CA");
    }
    string output;
    ctemplate::ExpandTemplate("example.tpl", ctemplate::DO_NOT_STRIP, &dict, &output);
     * */
    return 0;
}

