Matty
=====
How to use:

test.js

var users = [{Name:"Mrs. W",Address:"Guangzhou"},{Name:"Mrs. L",Address:"ShenZhen"}];
var tplFileName = "test.tpl";
var outFileName = "test.txt";
var dict = {
	Name1:"Stand by you.",
	Int32:33,
	Float:Date.now(),
	Users:users
}
ctemplate.render(dict,tplFileName,outFileName);

ctemplate.write("json.txt",JSON.stringify({Name:323,Wiff:true}));
var txt = ctemplate.read("json.txt");
ctemplate.log(txt);
var obj = JSON.parse(txt);
ctemplate.log(obj.Name);

test.tpl

{{Name1}}:{{Int32}}
{{Float}}

{{#Users}}
{{Name}} - {{Address}}
{{/Users}}