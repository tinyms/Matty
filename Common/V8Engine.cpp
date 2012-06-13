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
    
    /*console object definition{*/
    Handle<ObjectTemplate> console_object = ObjectTemplate::New();
    console_object->Set(String::New("browser"),External::Wrap(console));
    console_object->Set(String::New("log"),FunctionTemplate::New(CWrapConsoleGridAppendRowFunction));
    /*}*/
    
    /*console object definition{*/
    Handle<ObjectTemplate> io_object = ObjectTemplate::New();
    io_object->Set(String::New("read"),FunctionTemplate::New(CTemplateReadText));
    io_object->Set(String::New("write"),FunctionTemplate::New(CTemplateWriteText));
    /*}*/
    
    /*ctemplate object definition{*/
    Handle<ObjectTemplate> ctemplate_object = ObjectTemplate::New();
    ctemplate_object->Set(String::New("render"),FunctionTemplate::New(CTemplateRender));
    
    /*}*/
    
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
    Handle<ObjectTemplate> global = ObjectTemplate::New();
    global->Set(String::New("io"),io_object);
    global->Set(String::New("console"),console_object);
    global->Set(String::New("ctemplate"),ctemplate_object);
    //End Reg
    Persistent<Context> context = Context::New(NULL,global);
    Context::Scope context_scope(context);
    Handle<String> source = String::New(script_text);
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

