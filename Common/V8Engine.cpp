/* 
 * File:   V8Engine.cpp
 * Author: tinyms
 * 
 * Created on 2012年6月2日, 下午11:14
 */

#include "V8Engine.h"
#include "CTemplateWrap.h"
void V8Engine::Execute(const char* script_text){
    HandleScope handle_scope;
    //Reg
    Handle<ObjectTemplate> global = ObjectTemplate::New();
    Handle<FunctionTemplate> ctemplate_template = FunctionTemplate::New(CTemplateDictionaryConstructor);
    ctemplate_template->SetClassName(String::New("ctemplate_dictionary"));
    Handle<ObjectTemplate> ctemplate_prototype = ctemplate_template->PrototypeTemplate();
    ctemplate_prototype->Set("setValue",FunctionTemplate::New(CTemplateDictionarySetValue));
    Handle<ObjectTemplate> ctemplate_inst = ctemplate_template->InstanceTemplate(); 
    ctemplate_inst->SetInternalFieldCount(1);
    ///
    global->Set(String::New("ctemplate_dictionary"),ctemplate_template);
    global->Set(String::New("ctemplate_render"),FunctionTemplate::New(CTemplateRender));
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

