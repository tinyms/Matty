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
#include <map>
#include <fltk/run.h>
#include <fltk/Threads.h>
#include <fltk/Browser.h>
#include <ctemplate/template.h>
#include <v8.h>
#include "DataType.h"
using namespace v8;
using namespace std;
extern Handle<Value> CConsoleConstructor(const Arguments& args);
//
extern Handle<Value> CTemplateDictionaryConstructor(const Arguments& args);
extern Handle<Value> CTemplateDictionarySetValue(const Arguments& args);
extern Handle<Value> CTemplateDictionaryAddSectionDictionary(const Arguments& args);
extern Handle<Value> CTemplateDictionaryShowSection(const Arguments& args);
extern Handle<Value> CTemplateLog(const Arguments& args);
extern Handle<Value> CTemplateReadText(const Arguments& args);
extern Handle<Value> CTemplateWriteText(const Arguments& args);
extern Handle<Value> CTemplateRender(const Arguments& args);
extern Handle<Value> CWrapConsoleGridViewConstructor(const Arguments& args);
extern Handle<Value> CWrapConsoleGridAppendRowFunction(const Arguments& args);
extern void IteratorJsObject(ctemplate::TemplateDictionary* dict,Local<Object> items);
class CTemplateWrap {
public:
    CTemplateWrap();
    CTemplateWrap(const CTemplateWrap& orig);
    virtual ~CTemplateWrap();
};


#endif	/* CTEMPLATEWRAP_H */

