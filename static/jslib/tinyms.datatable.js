/**
 * User: tinyms
 * Date: 13-9-2
 * @config:
 * function datatable_sortable(id){}
 * function datatable_server_params(id,aoData){} //aoData is list(dict)
 * function datatable_server_data(id, data, textStatus, jqXHR){}
 * function datatable_form_fill(id,row){}
 * function datatable_form_init(id){}
 * function datatable_render(id,k,v,row){}
 * function datatable_render_actionbar(id,k,v,row){}
 * function datatable_data_before_add(id){}
 * function datatable_data_add(id,form_data){}
 * function datatable_data_update(id,pk,form_data){}
 * function datatable_data_delete(id,pk){}
 * function datatable_data_delete_confirm_label(id);
 * function datatable_select_mode(id,values){}
 */
function DataTableX(id_, entityName_, cols_, actionbar_render_) {
    var self = this;
    this.id = id_;
    this.__dataTable = null;
    this.actionbar_render = actionbar_render_;
    this.entityName = entityName_;
    this.cols = cols_;
    this.config = {};
    this.request_url = "/datatable/" + self.entityName + "/";
    this.is_add = true;
    this.select_mode = ""
    this.search_tip = "";
    this.Create = function () {
        var len = this.cols.length;
        for (var k = 0; k < len; k++) {
            var item = this.cols[k];
            if(k==0&&item["mData"]=="id"){
                continue;
            }
            if (typeof(datatable_render) != "undefined") {
                var func = function (col, v, type, row) {
                    return datatable_render(self.id, col, v, row);
                };
                item["mRender"] = func;
            }
        }
        self.cols.push({"mData": "id", "sTitle": "#", "mRender": function (col, v, type, row) {
            return self.actionbar_render(col,v,type,row);
        }});

        var bSorting = true;
        if (typeof(datatable_sortable) != "undefined") {
            bSorting = datatable_sortable(self.id);
        }
        self.config = {
            "bServerSide": true,
            "bProcessing": true,
            "asSorting": bSorting,
            "sDom": "<'row'<'col-sm-6'l><'col-sm-6'f>r>t<'row'<'col-sm-6'i><'col col-sm-6'p>>",
            //"sDom": '<"#' + self.id + '_NewRowBtnWrap">T<"clear">lfrtip',
            //"oTableTools": {"sSwfPath": "/static/jslib/datatable/extras/tabletools/swf/copy_csv_xls.swf"},
            "sAjaxSource": self.request_url + "list",
            "fnServerParams": function (aoData) {
                if (typeof(datatable_server_params) != "undefined") {
                    datatable_server_params(self.id, aoData);
                }
            },
            "fnServerData": function (sSource, aoData, fnCallback, oSettings) {
                oSettings.jqXHR = $.ajax({
                    "dataType": "json",
                    "type": "POST",
                    "url": sSource,
                    "data": aoData,
                    "success": function (data, textStatus, jqXHR) {
                        $('#' + self.id).data("DataSet", data);
                        fnCallback(data, textStatus, jqXHR);
                        if (typeof(datatable_server_data) != "undefined") {
                            datatable_server_data(self.id, data, textStatus, jqXHR);
                        }
                    }
                });
            },
            "aoColumns": self.cols,
            "sPaginationType": "full_numbers",
            "oLanguage": {
                "sLengthMenu": "每页显示 _MENU_ 条记录",
                "sZeroRecords": "抱歉， 没有找到",
                "sInfo": "从_START_到_END_ / 共<span style='color: #ff5f5f;'>_TOTAL_</span>条数据",
                "sInfoEmpty": "没有数据",
                "sInfoFiltered": "(从 _MAX_ 条数据中检索)",
                "sZeroRecords": "没有检索到数据",
                "sSearch": "快速搜索:",
                "oPaginate": {
                    "sFirst": "首页",
                    "sPrevious": "前页",
                    "sNext": "后页",
                    "sLast": "尾页"
                }

            }
        };
        self.__dataTable = $('#' + self.id).dataTable(self.config);
        if(self.is_add){
            $('#' + self.id + '_length label').append(" <button class='btn btn-sm btn-white' id='" + self.id + "_NewRowBtn'><i class='icon-plus'></i>新增</button>");
            $("#" + self.id + "_NewRowBtn").click(function () {
                self.switchTableAndEditFormPanel(true);
            });
        }
        if(self.search_tip.length>0){
            $("#"+self.id+"_filter input").each(function(){
                $(this).attr("data-toggle","popover");
                $(this).attr("data-placement","auto");
                $(this).attr("data-container","body");
                $(this).attr("data-content",self.search_tip);
            });
        }
        return self.__dataTable;
    };
    this.dataTable = function () {
        return self.__dataTable;
    };
    this.switchTableAndEditFormPanel = function (is_panel) {
        $("#" + self.id + "_form").resetForm();
        $("#" + self.id + "_form input[type='hidden']").val("");
        if (is_panel) {
            //var form_html = "<input type='hidden' id='id' name='id'/>";
            //form_html += $("#" + self.id + "_EditFormTemplate").html();
            //here
            //$("#" + self.id + "_form").html(form_html);
            if(typeof(datatable_form_init)!="undefined"){
                datatable_form_init(self.id);
            }
            $("#" + self.id + "_wrap").hide();
            $("#" + self.id + "_panel").show();
        } else {
            $("#" + self.id + "_wrap").show();
            $("#" + self.id + "_panel").hide();
        }
    }
    this.Refresh = function () {
        $('#' + self.id).dataTable();
        self.__dataTable.fnClearTable();
    };
    this.DataSet = function () {
        return $('#' + self.id).data("DataSet");
    };
    this.GetRow = function (id) {
        var ds = $('#' + self.id).data("DataSet");
        if (ds != undefined) {
            for (var k = 0; k < ds.aaData.length; k++) {
                if (ds.aaData[k].id == id) {
                    return ds.aaData[k];
                }
            }
        }
        return null;
    };

    this.CheckAll = function(chk){
        var sel = $(chk).prop("checked");
        if(sel){
            $("#"+self.id+" td.datatable_col_sel :checkbox.checkable").each(function(){
                $(this).prop("checked",true);
            });
        }else{
            $("#"+self.id+" td.datatable_col_sel :checkbox.checkable").each(function(){
                $(this).prop("checked",false);
            });
        }
    }

    this.GetSelectedValues=function(){
        var values = []
        $("#"+self.id+" td.datatable_col_sel :checkbox.checkable").each(function(){
            if($(this).prop("checked")){
                values.push(parseInt($(this).val()));
            }
        });
        return values;
    }
    this.color_current_row = function(btn){
        $("#" + self.id + " tr").removeAttr("style");
        $(btn).parent().parent().parent().attr("style", "background-color:#99CC99;");
    }
    this.form = {
        "cancel": function (btn) {
            self.switchTableAndEditFormPanel(false);
        },
        "save": function (btn, state) {
            if (!$("#" + self.id + "_form").valid()) {
                return;
            }
            if(typeof(datatable_data_before_add)!="undefined"){
                if(!datatable_data_before_add(self.id)){
                    return;
                }
            }
            $("#" + self.id + "_form").ajaxSubmit({
                "dataType": "json", "url": self.request_url + "save", "type": "post",
                "beforSubmit": function (formData, jqForm, options) {
                },
                "success": function (data, statusText, xhr, $form) {
                    if (data.success) {
                        toastr.success("保存成功!")
                        if(data.flag=="add"){
                            $("#" + self.id + "_form #id").val(data.msg);
                            if (typeof(datatable_data_add) != "undefined") {
                                return datatable_data_add(self.id, data.msg);
                            }
                        }else if(data.flag == "update"){
                            if (typeof(datatable_data_update) != "undefined") {
                                return datatable_data_update(self.id, $("#" + self.id + "_form #id").val(), data.msg);
                            }
                        }
                        if (state == "clear") {
                            $("#" + self.id + "_form").resetForm();
                            $("#" + self.id + "_form input[type='hidden']").val("");
                        }
                        self.Refresh();
                    }else{
                        toastr.error("保存失败! "+data.msg);
                    }
                },
                "error": function () {
                    toastr.error("服务器内部错误!");
                }
            });
        },
        "reset": function (btn) {
            $("#" + self.id + "_form").resetForm();
            $("#" + self.id + "_form input[type='hidden']").val("");
        }
    };
    this.RecordSetProvider = {
        "id": function () {
            return self.id;
        },
        "form_id": function () {
            return $('#' + this.id()).data("EditFormId");
        },
        "New": function (btn) {
            self.switchTableAndEditFormPanel(true);
        },
        "Modify": function (btn, record_id) {
            self.color_current_row(btn);
            $.post(self.request_url+"view",{id:record_id},function(data){
                if(data.success){
                    self.switchTableAndEditFormPanel(true);
                    var current_row = data.msg;
                    try {
                        for (var k in current_row) {
                            $("#" + self.id + "_form #" + k).val(current_row[k]);
                        }
                        if (typeof(datatable_form_fill) != "undefined") {
                            datatable_form_fill(self.id, current_row);
                        }
                    } catch (e) {}
                }
            });
        },
        "Delete": function (btn, record_id) {
            self.color_current_row(btn);
            var label = "确定要删除当前选中的记录吗?";
            if (typeof(datatable_data_delete_confirm_label) != "undefined") {
                label = datatable_data_delete_confirm_label(self.id);
            }
            if (confirm(label)) {
                $.post(self.request_url + "delete", {id: record_id}, function (data) {
                    if (data.success) {
                        toastr.success("删除成功!")
                        if (typeof(datatable_data_delete) != "undefined") {
                            return datatable_data_delete(self.id, record_id);
                        }
                        self.Refresh();
                    }else{
                        toastr.error("删除失败!")
                    }
                }, "json");
            }
        }
    };
}
