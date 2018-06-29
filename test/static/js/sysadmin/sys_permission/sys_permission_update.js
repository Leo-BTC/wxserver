jQuery(function () {
    var id_result = -3;  //当前选中层级id

    var select_id_list;  //选中id list


    $(document).ready(function () {

        settingParentSelect();

        $(".icon-picker").iconPicker(); //初始化图标选择器

    });

    function settingParentSelect() {
        var id = getCurrentID();

        $.ajax({
            type: 'POST',
            url: '/permission/update/get_level',
            data: {"id": id},
            success: function (data) {
                var d = JSON.parse(data);
                var jsondata = d['data'];

                for (var i = 0; i < jsondata.length; i++) {

                    var box = $('#click_sellect_item');
                    box.append("<select  class='selectpicker'  id='form-field-select-"
                        + i
                        + "'>"
                        + "<option value='-2'>无(创建层级)</option></select>");

                    for (j = 0; j < jsondata[i][0].length; j++) {
                        if (id != jsondata[i][0][j][0]) {
                            var $html = "<option value='" + jsondata[i][0][j][0] + "'>" + jsondata[i][0][j][1] + "</option>"
                            $("#form-field-select-" + i).append($html);
                        }
                    }


                    bind_select_with_level(i);

                    $("#form-field-select-" + i).find("option[value=" + jsondata[i][1] + "]").attr("selected", true);

                    $("#" + "form-field-select-" + i).selectpicker('refresh');


                }
            }
        });

    }

    function bind_select_with_level(level) {

        $("#" + "form-field-select-" + level).on('changed.bs.select', function () {

            var num_list = new Array();
            var id_list = new Array();

            $("#click_sellect_item").find("select").each(function (i, a) {
                var id = $(this).attr("id");
                num_list[i] = id;
                num_list.push(id);
                var obj = document.getElementById(id);
                var index = obj.selectedIndex; // 选中索引
                var value = obj.options[index].value; // 选中值
                if (value >= 0) {
                    id_list.push(value);
                }
            });

            select_id_list = id_list;

            var id = $(this).attr('id');
            var num = id.charAt(id.length - 1);
            var select_num_tag = parseInt(num) + 1;
            var productId = $('#' + id).val();
            if (productId >= 0) {
                id_result = productId;
            } else {
                if (id_list.length >= level - 1 && id_list.length > 0 && level !== 0) {
                    id_result = id_list[level - 1];
                } else {
                    id_result = 0;
                }
            }

            setParentID(id_result);


            for (var i = 0; i < num_list.length; i++) {
                var nums = num_list[i].charAt(num_list[i].length - 1);
                if (nums > num) {
                    $("#" + num_list[i] + '.selectpicker').selectpicker('destroy');
                }
            }

            $.ajax({
                type: 'POST',
                url: '/permission/add/get_level_data',
                data: {"parent_id": productId, "tag": 0},
                success: function (data) {
                    var select_data_list = data['data']['select_data_list'];

                    var newSelectPickerStr = "<option value='-2'>无(创建层级)</option>";

                    var span = document.createElement('select');
                    span.setAttribute('class', 'selectpicker');
                    span.setAttribute('id', 'form-field-select-' + select_num_tag);
                    span.innerHTML = newSelectPickerStr;
                    document.getElementById('click_sellect_item').appendChild(span);


                    for (var i = 0; i < select_data_list.length; i++) {
                        var $html = "<option value=\"" + select_data_list[i][0] + "\">" + select_data_list[i][1] + "</option>"
                        $("#form-field-select-" + select_num_tag).append($html);
                    }
                    if (select_data_list.length === 0) {
                        $("#form-field-select-" + select_num_tag).remove();
                    }

                    $('.selectpicker').selectpicker('render');
                    $("#form-field-select-" + select_num_tag).selectpicker('refresh');

                    bind_select_with_level(select_num_tag);
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    console.log("error");
                },
                dataType: 'json'
            });
        });

    }

});


function setParentID(value) {
    document.getElementById("parent_id").value = value;
}

function getCurrentID() {
    var curPath = window.document.location.href;
    var pathList = curPath.split("/");
    return pathList[pathList.length - 1];
}







