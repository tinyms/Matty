#include "CTemplateWrap.h"
#include "IO.h"

Handle<Value> CTemplateDictionaryConstructor(const Arguments& args) {
    Handle<Object> obj = args.This();
    HandleScope handle_scope;
    String::Utf8Value name(args[0]);
    ctemplate::TemplateDictionary *dict = new ctemplate::TemplateDictionary(*name);
    obj->SetInternalField(0, External::New(dict));
    map<string, ctemplate::TemplateDictionary*>* sub_dict_map = new map<string, ctemplate::TemplateDictionary*>();
    obj->SetInternalField(1, External::New(sub_dict_map));
    return obj;
}

Handle<Value> CTemplateDictionarySetValue(const Arguments& args) {
    if (args.Length() < 2) {
        return Undefined();
    }
    String::Utf8Value key(args[0]);
    Local<Object> self = args.Holder();
    Local<External> wrap = Local<External>::Cast(self->GetInternalField(0));
    void *ptr = wrap->Value();
    ctemplate::TemplateDictionary* td = static_cast<ctemplate::TemplateDictionary*> (ptr);
    if (args[1]->IsString()) {
        String::Utf8Value value(args[1]);
        td->SetValue(*key, *value);
    } else if (args[1]->IsInt32()) {
        td->SetIntValue(*key, args[1]->Int32Value());
    } else if (args[1]->IsNumber()) {
        cout << args.Length() << endl;
        if (args.Length() == 3) {
            String::Utf8Value format(args[2]);
            td->SetFormattedValue(*key, *format, args[1]->NumberValue());
        } else {
            td->SetFormattedValue(*key, "%.2f", args[1]->NumberValue());
        }
    }
    return Undefined();
}

/* 
 * dict.addSectionDictionary("sub_dict",sub_dict);
 *  */
Handle<Value> CTemplateDictionaryAddSectionDictionary(const Arguments& args) {
    String::Utf8Value section_name(args[0]);
    String::Utf8Value name(args[1]);
    //this
    Local<Object> self = args.Holder();
    //main
    Local<External> wrap = Local<External>::Cast(self->GetInternalField(0));
    ctemplate::TemplateDictionary* this_ = static_cast<ctemplate::TemplateDictionary*> (wrap->Value());

    //Sub
    Local<External> wrap_map = Local<External>::Cast(self->GetInternalField(1));
    map<string, ctemplate::TemplateDictionary*>* this_subs = static_cast<map<string, ctemplate::TemplateDictionary*>*> (wrap_map->Value());
    if (this_subs == NULL) {
        cout << "Map Empty." << endl;
    }
    //Exists
    string key(*section_name);
    ctemplate::TemplateDictionary* sub = NULL;
    if (this_subs->find(*section_name) != this_subs->end()) {
        sub = (*this_subs)[key];
    } else {
        sub = this_->AddSectionDictionary(*section_name);
        (*this_subs)[key] = sub;

    }
    if (sub != NULL) {
        if (args[1]->IsString()) {
            String::Utf8Value value(args[2]);
            sub->SetValue(*name, *value);
        } else if (args[1]->IsInt32()) {
            sub->SetIntValue(*name, args[2]->Int32Value());
        } else if (args[1]->IsNumber()) {
            if (args.Length() == 3) {
                String::Utf8Value format(args[3]);
                sub->SetFormattedValue(*name, *format, args[2]->NumberValue());
            } else {
                sub->SetFormattedValue(*name, "%.2f", args[2]->NumberValue());
            }
        }
    }
    return Undefined();
}

Handle<Value> CWrapConsoleGridViewConstructor(const Arguments& args){
    //parse gridvew local value external wrap
    Handle<Object> console = Handle<Object>::Cast(args[0]);
    Local<External> wrap = Local<External>::Cast(console->GetInternalField(0));
    fltk::Browser* gridview = static_cast<fltk::Browser*> (wrap->Value());
    //put this object as a inner prop
    Handle<Object> obj = args.This();
    HandleScope handle_scope;
    obj->SetInternalField(0, External::New(gridview));
    return obj;
}

Handle<Value> CWrapConsoleGridAppendRowFunction(const Arguments& args){
    Local<Object> self = args.Holder();
    Local<External> wrap = Local<External>::Cast(self->GetInternalField(0));
    fltk::Browser* gridview = static_cast<fltk::Browser*> (wrap->Value());
    if(gridview==NULL){
        cout<<"gridview==NULL"<<endl;
        return Undefined();
    }
    fltk::lock();
    if(args.Length()==0){
        gridview->add("Normal\t ",gridview);
    }else if(args.Length()==1){
        String::Utf8Value message(args[0]);
        string msg(*message);
        msg="Normal\t"+msg;
        gridview->add(msg.c_str(),gridview);
    }
    else if(args.Length()==2){
        String::Utf8Value tag(args[0]);
        String::Utf8Value message(args[1]);
        string tag_(*tag);
        string msg(*message);
        gridview->add((tag_+"\t"+msg).c_str(),gridview);
    }
    fltk::unlock();
    return Undefined();
}

Handle<Value> CTemplateDictionaryShowSection(const Arguments& args) {
    String::Utf8Value name(args[0]);
    Local<Object> self = args.Holder();
    Local<External> wrap = Local<External>::Cast(self->GetInternalField(0));
    void *ptr = wrap->Value();
    ctemplate::TemplateDictionary* td = static_cast<ctemplate::TemplateDictionary*> (ptr);
    td->ShowSection(*name);
    return Undefined();
}

Handle<Value> CTemplateLog(const Arguments& args){
    if (args.Length() < 1) {
        cout<<""<<endl;
        return Undefined();
    }
    String::Utf8Value msg(args[0]);
    cout<<*msg<<endl;
    MessageX* msg_ = new MessageX();
    msg_->category="Normal";
    msg_->message = *msg;
    //fltk::lock();
    fltk::awake(msg_);
    //fltk::unlock();
    return Undefined();
}
Handle<Value> CTemplateReadText(const Arguments& args){
    if (args.Length() < 1) {
        return String::New("");
    }
    String::Utf8Value fileName(args[0]);
    string content;
    IO::ReadTextFile(*fileName,content);
    return String::New(content.c_str());
}
Handle<Value> CTemplateWriteText(const Arguments& args){
    if (args.Length() < 2) {
        return String::New("");
    }
    String::Utf8Value fileName(args[0]);
    String::Utf8Value content(args[1]);
    string text(*content);
    IO::WriteTextFile(*fileName,text);
    return Undefined();
}
Handle<Value> CTemplateRender(const Arguments& args) {
    if (args.Length() != 3) {
        return String::New("");
    }
    Handle<Object> dict_object = Handle<Object>::Cast(args[0]);
    String::Utf8Value fileName(args[1]);
    ctemplate::TemplateDictionary dict("Default");
    IteratorJsObject(&dict, dict_object->ToObject());
    string output;
    ctemplate::ExpandTemplate(*fileName, ctemplate::DO_NOT_STRIP, &dict, &output);
    if (args.Length() == 3) {
        String::Utf8Value outFileName(args[2]);
        IO::WriteTextFile(*outFileName, output);
    }
    return String::New(output.c_str());
}

void IteratorJsObject(ctemplate::TemplateDictionary* dict, Local<Object> dict_object) {
    Local<Array> names = dict_object->GetOwnPropertyNames();
    for (int index = 0; index < names->Length(); index++) {
        Local<Value> key = names->Get(index);
        String::Utf8Value item(key);
        Local<Value> val = dict_object->Get(key);
        if (val->IsString()) {
            String::Utf8Value txt(val);
            dict->SetValue(*item, *txt);
        } else if (val->IsInt32()) {
            dict->SetIntValue(*item, val->Int32Value());
        } else if (val->IsNumber()) {
            dict->SetFormattedValue(*item, "%.8f", val->NumberValue());
        } else if (val->IsArray()) {
            Local<Array> arr = Local<Array>::Cast(val);
            for (int k = 0; k < arr->Length(); k++) {
                if (!arr->Get(k)->IsObject()) {
                    continue;
                }
                ctemplate::TemplateDictionary* sub = dict->AddSectionDictionary(*item);
                IteratorJsObject(sub, arr->Get(k)->ToObject());
            }
        }
    }
}

CTemplateWrap::CTemplateWrap() {
}

CTemplateWrap::CTemplateWrap(const CTemplateWrap& orig) {
}

CTemplateWrap::~CTemplateWrap() {
}