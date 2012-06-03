/* 
 * File:   V8Engine.h
 * Author: tinyms
 *
 * Created on 2012年6月2日, 下午11:14
 */

#ifndef V8ENGINE_H
#define	V8ENGINE_H
#include <string>
#include <v8.h>
using namespace std;
using namespace v8;
class V8Engine {
public:
    static void Execute(const char* script_text);
public:
    V8Engine();
    V8Engine(const V8Engine& orig);
    virtual ~V8Engine();
private:

};

#endif	/* V8ENGINE_H */

