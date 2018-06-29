jQuery(function () {
    $(document).ready(function (e) {
        var role_id = $('#role').val()
        // select2加载机构
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
                org_id: $("#org").val()
            },
            success: function (result) {
                if(result['code'] == '-1'){

                }else{
                    for (var i = 0; i < 1; i++) {
                    var item = result[0];
                    var option = new Option(item.value, item.id, true, true);
                    $select2.append(option)
                }
                $select2.trigger('change');
                }
            }
        })


        var org_data = $("#org").val()
        if(org_data.length == 0){
            var option = "<option selected='selected' value=\"" + "-1" + "\"";
            option += ">" + "--请先选择机构--" + "</option>";
            $("#user_role").append(option)
            $("#user_role").selectpicker('refresh');
        }else {

        }

        function sleep(d){
            for(var t = Date.now();Date.now() - t <= d;);
        }

        $("#sel_menu").on('change', function () {
            var get_org_data = $("#sel_menu").val()
            $("#org").val(get_org_data)
            change_org(get_org_data);
            sleep(500);
            init_role();
        })



        function change_org(get_org_data) {
           $.ajax({
            url: "/sysuser/to/get/org/role",
            type: "GET",
            data: {
                org_id: get_org_data
            },
            success: function (data) {
                $("#user_role").find("option:selected").text("");
                $("#user_role").empty();
                $("#user_role").selectpicker('refresh');
                data = JSON.parse(data)
                if (data.length == 0) {
                    var option = "<option selected='selected' value=\"" + "-1" + "\"";
                    option += ">" + "--请选择机构--" + "</option>";
                    $("#user_role").append(option)
                    $("#user_role").selectpicker('refresh');
                } else {
                    var opt = "<option selected='selected' value=\"" + "-1" + "\"" + ">" + "--请选择角色--" + "</option>"
                    $("#user_role").append(opt)
                    $("#user_role").selectpicker('refresh');
                    for (var i = 0; i < data.length; i++) {
                        var option = "<option value=\"" + String(data[i][0]) + "\"";
                        option += ">" + data[i][1] + "</option>";  //动态添加数据
                        $("#user_role").append(option)
                        $("#user_role").selectpicker('refresh');
                    }
                }

                $("#role").empty();
                $("#role").val($("#user_role").val())
                $("#role").selectpicker('refresh');
            },
        })
        }

        $("#user_role").on('change', function () {
            $("#role").empty();
            $("#role").val($("#user_role").val())
            $("#role").selectpicker('refresh');
            })




        function init_role() {
             $.ajax({
            url: "/sysuser/to/get/org/role",
            type: "GET",
            data: {
                org_id: $("#org").val()
            },
            success: function (data) {
                $("#user_role").find("option:selected").text("");
                $("#user_role").empty();
                $("#user_role").selectpicker('refresh');
                data = JSON.parse(data)
                if (data.length == 0) {
                    var option = "<option selected='selected' value=\"" + "-1" + "\"";
                    option += ">" + "--请选择机构--" + "</option>";
                    $("#user_role").append(option)
                    $("#user_role").selectpicker('refresh');
                } else {
                    var opt = "<option selected='selected' value=\"" + "-1" + "\"" + ">" + "--请选择角色--" + "</option>"
                    $("#user_role").append(opt)
                    $("#user_role").selectpicker('refresh');
                    for (var i = 0; i < data.length; i++) {
                        if (role_id == String(data[i][0])) {
                            var option = "<option selected='selected' value=\"" + String(data[i][0]) + "\"";
                            option += ">" + data[i][1] + "</option>";  //动态添加数据
                        } else {
                            var option = "<option value=\"" + String(data[i][0]) + "\"";
                            option += ">" + data[i][1] + "</option>";  //动态添加数据
                        }
                        $("#user_role").append(option)
                        $("#user_role").selectpicker('refresh');
                    }
                }

                $("#role").empty();
                $("#role").val($("#user_role").val())
                $("#role").selectpicker('refresh');
            },
        })
        }
    });
    $(window).on('load', function () {
        $('.selectpicker').selectpicker({
            'selectedText': 'cat'
        });

    });
})