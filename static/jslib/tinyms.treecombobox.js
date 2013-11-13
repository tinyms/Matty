/**
 * User: tinyms
 * Date: 13-10-7
 * Time: 下午5:16
 */
(function ($) {
    $.fn.DropDownTree=function(options){
        var settings = $.extend({
            id:"",
            taxonomy:"",
            placeholder:"",
            select_completed:function(id,vals){},//当树节点选择完成后
            beforeNodeClick:function(treeId, treeNode){}//在单击树节点时的交互
        }, options);
        settings.node_clicked = function(e, treeId, treeNode){
            var zTree = $.fn.zTree.getZTreeObj(settings.id+"_tree"),
                nodes = zTree.getSelectedNodes(),
                v = "",values="";
            nodes.sort(function compare(a, b) {
                return a.id - b.id;
            });
            for (var i = 0, l = nodes.length; i < l; i++) {
                v += nodes[i].name + ",";
                values += nodes[i].id + ",";
            }
            if (v.length > 0) v = v.substring(0, v.length - 1);
            if (values.length > 0) values = values.substring(0, values.length - 1);
            var name = $("#"+settings.id+"_category_name");
            name.attr("value", v);
            $("#"+settings.id).attr("value", values);
            settings.select_completed(settings.id,values);
        }
        this.data("settings", settings);
        $.fn.DropDownTree_Render(settings.id,settings.placeholder);
        var tree_setting = {
            view: {
                dblClickExpand: false
            },
            data: {
                simpleData: {
                    enable: true
                }
            },
            callback: {
                beforeClick: settings.beforeNodeClick,
                onClick: settings.node_clicked
            }
        };
        $("#"+settings.id).bind("change",function(){
            var v = $(this).val();
            tinyms.controller.org.OrgEdit.names({taxonomy:settings.taxonomy,idArray:v},function(b,data){
                if(b){
                    $("#"+settings.id+"_category_name").val(data);
                }
            });
        });
        tinyms.controller.org.OrgEdit.list({taxonomy:settings.taxonomy},function(b,data){
		    $.fn.zTree.init($("#"+settings.id+"_tree"), tree_setting, data);
            var zTree = $.fn.zTree.getZTreeObj(settings.id+"_tree");
            zTree.expandAll(true);
	    });
        return this;
    };

    $.fn.DropDownTree_Render=function(id,placeholder_text){
        var html = '<ul class="nav navbar-nav hidden-xs">';
        html += '<li>';
        html += '<div class="m-t m-b-small" id="'+id+'-panel-tree">';
        html += '<a href="#" class="dropdown-toggle" data-toggle="dropdown">';
        html += '<input type="text" class="form-control" id="'+id+'_category_name" placeholder="'+placeholder_text+'">';
        html += '<input type="hidden" id="'+id+'"/>';
        html += '</a>';
        html += '<section class="dropdown-menu m-l-small m-t-mini">';
        html += '<section class="panel panel-large arrow arrow-top">';
        html += '<header class="panel-heading bg-white"></header>';
        html += '<ul id="'+id+'_tree" class="ztree"></ul>';
        html += '<footer class="panel-footer text-small"></footer>';
        html += '</section>';
        html += '</section>';
        html += '</div>';
        html += '</li>';
        html += '</ul>';
        $(this.selector).html(html);
    };

    $.fn.DropDownTree_SetValue=function(options){
        var opt = $.extend({
            value:""
        }, options);
        var settings = this.data("settings");
        $("#"+settings.id).val(opt.value).trigger("change");
        if(opt.value.length>0){
            var ids = opt.value.split(",");
            var zTree = $.fn.zTree.getZTreeObj(settings.id+"_tree");
            for(var k=0;k<ids.length;k++){
                var node = zTree.getNodeByParam("id",new Number(ids[k]));
                zTree.selectNode(node);
            }
        }
    };
}(jQuery));
