function autocomplete(id, provider, tpl, at) {
    $("#" + id + "_text").atwho({
        at: at,
        data: [],
        tpl: tpl,
        limit:10,
        show_the_at: false,
        start_with_space: false,
        callbacks: {
            remote_filter: function (word, cb) {
                $.post("/autocomplete/" + provider, {search_word: word}, function (data) {
                    cb(data);
                }, "json");
            },
            before_insert: function (v, li) {
                $("#" + id).val(li[0].dataset["key"]);
                return v;
            }
        }
    });
}
//回显自动完成的文本框值
function autocomplete_text_show(id){
    $("#"+id).change();
}