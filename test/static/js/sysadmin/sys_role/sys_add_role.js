/**
 * Created by 440S on 2017/11/1.
 */

jQuery(function () {
    // 获取 id

    $("#save").on('click', function () {
        alert(12)
        window.location.href = '/sysuser/add/user/' + 1
    })


     //select2加载机构
    var $select2 = $(".select2").select2({
        allowClear: true,
        placeholder: "请选择所属机构",
        ajax: {
            url: "/sysorg/to/get/org/pagine/list",
            dataType: "json",
            delay: 250,
            data: function (params) {
                return {
                    name: params.term,
                    page: params.page || 1
                };
            },
            cache: true,
            processResults: function (res, params) {
                var item = res["data"]["item"];
                var options = [];
                for (var i = 0, len = item.length; i < len; i++) {
                    var option = {"id": item[i]["id"], "text": item[i]["value"]};
                    options.push(option);
                }
                return {
                    results: options,
                    pagination: {
                        more: res["data"]["more"]
                    }
                };
            },
            escapeMarkup: function (markup) {
                return markup;
            },
            minimumInputLength: 1
        },
    });
    
    //select2初始化
    $.ajax({
        type: "get",
        url: "/sysuser/get/edit/user/one/org/data",//请求数据的地址
        dataType: "json",
        data: {
            org_id: $("#org_id").val()
        },
        success: function (result) {
            if(result['code'] == '-1'){}
            else{
             for (var i = 0; i < 1; i++) {
                var item = result[0];
                var option = new Option(item.value, item.id, true, true);
                $select2.append(option)
            }
            $select2.trigger('change');
            }
        }
    })
    

    $("#add_role_sel_menu").on('change', function(){
        var org_data = $("#add_role_sel_menu").val();
        $("#org_id").val(org_data)
        })
    
    $("#edit_role_sel_menu").on('change', function(){
        var org_data = $("#edit_role_sel_menu").val();
        $("#org_id").val(org_data)
        })
})


//$("#org").on("change", function () {
//    //console.log($("#org").val())
//    $.ajax({
//        async: false,
//        url: "/sysuser/get/role/by/org_id",
//        data: {
//            org_id: $("#org").val()
//        },
//        type: "GET"
//    })
//})
//
//
//$(function () {
//    if (!ace.vars['touch']) {
//        $('.chosen-select').chosen({allow_single_deselect: true});
//        //resize the chosen on window resize
//
//        $(window)
//            .off('resize.chosen')
//            .on('resize.chosen', function () {
//                $('.chosen-select').each(function () {
//                    var $this = $(this);
//                    $this.next().css({'width': "83%"});
//                })
//            }).trigger('resize.chosen');
//        //resize chosen on sidebar collapse/expand
//        $(document).on('settings.ace.chosen', function (e, event_name, event_val) {
//            if (event_name != 'sidebar_collapsed') return;
//            $('.chosen-select').each(function () {
//                var $this = $(this);
//                $this.next().css({'width': "83%"});
//            })
//        });
//
//
//        $('#chosen-multiple-style .btn').on('click', function (e) {
//            var target = $(this).find('input[type=radio]');
//            var which = parseInt(target.val());
//            if (which == 2) $('#id_mem_type_code').addClass('tag-input-style');
//            else $('#id_mem_type_code').removeClass('tag-input-style');
//        });
//    }
//})
