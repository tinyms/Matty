#include "CTemplateWrap.h"
#include "IO.h"

Handle<Value> CTemplateConstructor(const Arguments& args){
    Handle<Object> obj = args.This();
    HandleScope handle_scope;
    String::Utf8Value name(args[0]);
    ctemplate::TemplateDictionary *dict = new ctemplate::TemplateDictionary(*name);
    obj->SetInternalField(0,External::New(dict));
    return obj;
}

Handle<Value> CTemplateSetValue(const Arguments& args){
    String::Utf8Value name(args[0]);
    String::Utf8Value value(args[1]);
    Local<Object> self = args.Holder();
    Local<External> wrap = Local<External>::Cast(self->GetInternalField(0));
    void *ptr = wrap->Value();
    static_cast<ctemplate::TemplateDictionary*>(ptr)->SetValue(*name,*value);
    return Undefined();
}

Handle<Value> CTemplateRender(const Arguments& args){
    String::Utf8Value fileName(args[0]);
    if(args[1]->IsObject()){
        cout<<"IsObject"<<endl;
    }
    Handle<Object> dict_object = Handle<Object>::Cast(args[1]);    
    void *ptr = dict_object->GetPointerFromInternalField(0);
    if(ptr==NULL){
        cout<<"TemplateDictionary NULL!"<<endl;
        return Undefined();
    }
    ctemplate::TemplateDictionary* dict = static_cast<ctemplate::TemplateDictionary*>(ptr);
    string output;
    ctemplate::ExpandTemplate(*fileName, ctemplate::DO_NOT_STRIP, dict, &output);
    cout<<output<<endl;
    if(args.Length()==3){
        String::Utf8Value outFileName(args[2]);
        IO::WriteTextFile(*outFileName,output);
    }
    return Undefined();
}

CTemplateWrap::CTemplateWrap() {
}

CTemplateWrap::CTemplateWrap(const CTemplateWrap& orig) {
}

CTemplateWrap::~CTemplateWrap() {
}