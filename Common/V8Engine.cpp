/* 
 * File:   V8Engine.cpp
 * Author: tinyms
 * 
 * Created on 2012年6月2日, 下午11:14
 */

#include "V8Engine.h"
#include "CTemplateWrap.h"
void V8Engine::Execute(const char* script_text,fltk::Browser* console){
    HandleScope handle_scope;
    //Reg
    Handle<ObjectTemplate> global = ObjectTemplate::New();
    Handle<ObjectTemplate> ctemplate_object = ObjectTemplate::New();
    ctemplate_object->Set(String::New("render"),FunctionTemplate::New(CTemplateRender));
    ctemplate_object->Set(String::New("read"),FunctionTemplate::New(CTemplateReadText));
    ctemplate_object->Set(String::New("write"),FunctionTemplate::New(CTemplateWriteText));
    ctemplate_object->Set(String::New("log"),FunctionTemplate::New(CTemplateLog));
    Local<Value> console_gridview = External::Wrap(console);
    Handle<FunctionTemplate> console_gridview_constructor = FunctionTemplate::New(CWrapConsoleGridViewConstructor);
    console_gridview_constructor->SetClassName(String::New("console_win"));
    Handle<ObjectTemplate> console_gridview_prototype = console_gridview_constructor->PrototypeTemplate();
    console_gridview_prototype->Set("log",FunctionTemplate::New(CWrapConsoleGridAppendRowFunction));
    /*
    Handle<FunctionTemplate> ctemplate_template = FunctionTemplate::New(CTemplateDictionaryConstructor);
    ctemplate_template->SetClassName(String::New("ctemplate_dictionary"));
    Handle<ObjectTemplate> ctemplate_prototype = ctemplate_template->PrototypeTemplate();
    ctemplate_prototype->Set("setValue",FunctionTemplate::New(CTemplateDictionarySetValue));
    ctemplate_prototype->Set("addSectionDictionary",FunctionTemplate::New(CTemplateDictionaryAddSectionDictionary));
    ctemplate_prototype->Set("showSection",FunctionTemplate::New(CTemplateDictionaryShowSection));
    Handle<ObjectTemplate> ctemplate_inst = ctemplate_template->InstanceTemplate(); 
    ctemplate_inst->SetInternalFieldCount(2);
    */
    global->Set(String::New("ctemplate"),ctemplate_object);
    global->Set(String::New("console_gridview"),console_gridview);
    global->Set(String::New("console_win"),console_gridview_constructor);
    //global->Set(String::New("ctemplate_render"),FunctionTemplate::New(CTemplateRender));
    //End Reg
    Persistent<Context> context = Context::New(NULL,global);
    Context::Scope context_scope(context);
    string script_block(script_text);
    script_block = ""+script_block;
    Handle<String> source = String::New(script_block.c_str());
    Handle<Script> script = Script::Compile(source);
    script->Run();
    context.Dispose();
}
V8Engine::V8Engine() {
}

V8Engine::V8Engine(const V8Engine& orig) {
}

V8Engine::~V8Engine() {
}

