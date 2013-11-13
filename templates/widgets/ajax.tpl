namespace("{{ module_name }}.{{ class_name }}");
{% for method_name in methods %}
{{ module_name }}.{{ class_name }}.{{ method_name }} = function(params, callback, data_type){
if(typeof(params)=="undefined"){params={};}
params.__method_name__ = "{{ method_name }}";
if(typeof(callback)=="undefined"){callback=function(b,d){};}
if(typeof(data_type)=="undefined"){params.__data_type__ = "json";}else{params.__data_type__ = data_type;}
var req = $.ajax({
url: "/ajax/{{ key }}.js",type:"POST",data:params,dataType:data_type
});
req.done(function(data){callback(true,data);});
req.fail(function(jqXHR, textStatus) {
alert( "Request failed: " + textStatus );callback(false,textStatus);
})
}
{% end %}