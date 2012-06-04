#include "CTemplateWrap.h"
#include "IO.h"

Handle<Value> CTemplateDictionaryConstructor(const Arguments& args){
    Handle<Object> obj = args.This();
    HandleScope handle_scope;
    String::Utf8Value name(args[0]);
    ctemplate::TemplateDictionary *dict = new ctemplate::TemplateDictionary(*name);
    obj->SetInternalField(0,External::New(dict));
    map<string,ctemplate::TemplateDictionary*>* sub_dict_map = new map<string,ctemplate::TemplateDictionary*>();
    obj->SetInternalField(1,External::New(sub_dict_map));
    return obj;
}

Handle<Value> CTemplateDictionarySetValue(const Arguments& args){
    if(args.Length()<2){return Undefined();}
    String::Utf8Value key(args[0]);
    Local<Object> self = args.Holder();
    Local<External> wrap = Local<External>::Cast(self->GetInternalField(0));
    void *ptr = wrap->Value();
    ctemplate::TemplateDictionary* td = static_cast<ctemplate::TemplateDictionary*>(ptr);
    if(args[1]->IsString()){
        String::Utf8Value value(args[1]);
        td->SetValue(*key,*value);
    }else if(args[1]->IsInt32()){
        td->SetIntValue(*key,args[1]->Int32Value());
    }else if(args[1]->IsNumber()){
        cout<<args.Length()<<endl;
        if(args.Length()==3){
            String::Utf8Value format(args[2]);
            td->SetFormattedValue(*key,*format,args[1]->NumberValue());
        }else{
            td->SetFormattedValue(*key,"%.2f",args[1]->NumberValue());
        }
    }
    return Undefined();
}

/* 
 * dict.addSectionDictionary("sub_dict",sub_dict);
 *  */
Handle<Value> CTemplateDictionaryAddSectionDictionary(const Arguments& args){
    String::Utf8Value section_name(args[0]);
    String::Utf8Value name(args[1]);
    //this
    Local<Object> self = args.Holder();
    //main
    Local<External> wrap = Local<External>::Cast(self->GetInternalField(0));
    ctemplate::TemplateDictionary* this_ = static_cast<ctemplate::TemplateDictionary*>(wrap->Value());
    
    //Sub
    Local<External> wrap_map = Local<External>::Cast(self->GetInternalField(1));
    map<string,ctemplate::TemplateDictionary*>* this_subs = static_cast<map<string,ctemplate::TemplateDictionary*>*>(wrap_map->Value());
    if(this_subs==NULL){
        cout<<"Map Empty."<<endl;
    }
    //Exists
    string key(*section_name);
    ctemplate::TemplateDictionary* sub = NULL;
    cout<<"Map Empty."<<endl;
    if(this_subs->find(*section_name)!=this_subs->end()){
        cout<<30000<<endl;
        sub = (*this_subs)[key];
    }else{
        cout<<40000<<endl;
        sub = this_->AddSectionDictionary(*section_name);
        (*this_subs)[key]=sub;
        
    }
    cout<<"3Map Empty."<<endl;
    if(sub!=NULL){
        cout<<20000<<endl;
        if(args[1]->IsString()){
            String::Utf8Value value(args[2]);
            sub->SetValue(*name,*value);
        }else if(args[1]->IsInt32()){
            sub->SetIntValue(*name,args[2]->Int32Value());
        }else if(args[1]->IsNumber()){
            cout<<args.Length()<<endl;
            if(args.Length()==3){
                String::Utf8Value format(args[3]);
                sub->SetFormattedValue(*name,*format,args[2]->NumberValue());
            }else{
                sub->SetFormattedValue(*name,"%.2f",args[2]->NumberValue());
            }
        }
    }
    return Undefined();
}

Handle<Value> CTemplateDictionaryShowSection(const Arguments& args){
    String::Utf8Value name(args[0]);
    Local<Object> self = args.Holder();
    Local<External> wrap = Local<External>::Cast(self->GetInternalField(0));
    void *ptr = wrap->Value();
    ctemplate::TemplateDictionary* td = static_cast<ctemplate::TemplateDictionary*>(ptr);
    td->ShowSection(*name);
    return Undefined();
}

Handle<Value> CTemplateRender(const Arguments& args){
    if(args.Length()!=3){return String::New("");}
    Handle<Object> dict_object = Handle<Object>::Cast(args[0]);
    String::Utf8Value fileName(args[1]);
    
    void *ptr = dict_object->GetPointerFromInternalField(0);
    if(ptr==NULL){
        cout<<"TemplateDictionary NULL!"<<endl;
        return Undefined();
    }
    ctemplate::TemplateDictionary* dict = static_cast<ctemplate::TemplateDictionary*>(ptr);
    string output;
    ctemplate::ExpandTemplate(*fileName, ctemplate::DO_NOT_STRIP, dict, &output);
    if(args.Length()==3){
        String::Utf8Value outFileName(args[2]);
        IO::WriteTextFile(*outFileName,output);
    }
    return String::New(output.c_str());
}

CTemplateWrap::CTemplateWrap() {
}

CTemplateWrap::CTemplateWrap(const CTemplateWrap& orig) {
}

CTemplateWrap::~CTemplateWrap() {
}