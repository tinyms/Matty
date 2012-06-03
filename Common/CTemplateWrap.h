/* 
 * File:   CTemplateWrap.h
 * Author: tinyms
 *
 * Created on 2012年6月2日, 下午11:48
 */

#ifndef CTEMPLATEWRAP_H
#define	CTEMPLATEWRAP_H

#include <iostream>  
#include <string>
#include <ctemplate/template.h>
#include <v8.h>
using namespace v8;
using namespace std;
extern Handle<Value> CTemplateConstructor(const Arguments& args);
extern Handle<Value> CTemplateSetValue(const Arguments& args);
extern Handle<Value> CTemplateRender(const Arguments& args);
class CTemplateWrap {
public:
    CTemplateWrap();
    CTemplateWrap(const CTemplateWrap& orig);
    virtual ~CTemplateWrap();
};


#endif	/* CTEMPLATEWRAP_H */

