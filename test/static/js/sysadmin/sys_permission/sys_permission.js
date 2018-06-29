/**
 * Created by linjunjie on 2017/11/6.
 */
jQuery(function () {
    var table = $('#permission_table');

    $(document).ready(function () {

        settingTable();

        //activate the tooltips after the data table is initialized
        $('[rel="tooltip"]').tooltip();

        $(window).resize(function () {
            table.bootstrapTable('resetView');
        });


    });

    function settingTable() {
        table.bootstrapTable({
            url: '/permission/get_list',
            toolbar: ".toolbar",
            showRefresh: true,
            search: true,
            showToggle: true,
            showColumns: true,
            clickToSelect: true,  //触发选中事件
            pagination: true,
             sortable: true,                     //是否启用排序
            sortOrder: "asc",
            // sortOrder: 'desc',
            sidePagination: "server",
            searchAlign: 'left',
            pageSize: 5,    // 前端分页数量
            pageList: [5, 10, 20],  // 前端分页展示数据
            queryParams: function (params) {
                return {
                    searchData: params.search,
                    pageNumber: params.offset,
                    pageSize: params.limit,
                     sort: params.sort,      //排序列名
                    sortOrder: params.order
                };
            },
            columns: [
                {
                    checkbox: true,
                    align: 'center'
                },
                {
                    title: '序号',
                    align: 'center',
                    switchable: false,
                    formatter: function (value, row, index) {
                        var pageSize = table.bootstrapTable('getOptions').pageSize;//通过表的#id 可以得到每页多少条
                        var pageNumber = table.bootstrapTable('getOptions').pageNumber;//通过表的#id 可以得到当前第几页
                        return pageSize * (pageNumber - 1) + index + 1;  //返回每条的序号： 每页条数 * （当前页 - 1 ）+ 序号
                    }
                },
                {
                    field: 'name',
                    title: '权限名称',
                    align: 'center',
                     sortable:true,
                    sortOrder: "asc"
                },
                {
                    field: 'url',
                    title: '权限路径',
                    align: 'center',
                    // width: 200,
                     sortable:true,
                    sortOrder: "asc"
                },
                {
                    field: 'type',
                    title: '权限类型',
                    align: 'center',
                     sortable:true,
                    sortOrder: "asc"
                },
                {
                    field: 'sort',
                    title: '显示顺序',
                    align: 'center',
                     sortable:true,
                    sortOrder: "asc"
                },
                {
                    field: 'icon',
                    title: '菜单图标',
                    align: 'center',
                    sortable:false,
                    sortOrder: "asc",
                    formatter: formatOperatIcon
                },
                {
                    field: 'update_date',
                    title: '更新时间',
                    align: 'center',
                     sortable:true,
                    sortOrder: "asc"
                },
                {
                    field: 'status',
                    title: '状态',
                    align: 'center',
                     sortable:true,
                    sortOrder: "asc",
                    formatter: formatOperatStatus
                }
            ],
            icons: {
                refresh: 'fa fa-refresh',
                toggle: 'fa fa-th-list',
                columns: 'fa fa-columns',
                detailOpen: 'fa fa-plus-circle',
                detailClose: 'fa fa-minus-circle'
            },
            formatShowingRows: function (pageFrom, pageTo, totalRows) {
                //do nothing here, we don't want to show the text "showing x of y from..."
                return "总计：" + totalRows + "条";
            },
            formatRecordsPerPage: function (pageNumber) {
                return pageNumber + " 显示";
            },
            onClickRow: function (row, $element) {
                // 当某一行被点击时触发该事件
            },
            onCheck: function (row) {
                // 当某一行被选中时触发
            },
            onCheckAll: function (rows) {
                // 全部行被选中时触发
            },
        });
    }

    function formatOperatStatus(value, row, index) {

        if (value === 0) {
            return ['<button class="btn btn-round btn-xs btn-success btn-fill" id="enable" ' +
            'onclick="javascript:clickPermissionEnable('+row.id+')" >正常</button>'];
        } else {
            return ['<button class="btn btn-round btn-xs btn-error btn-fill" id="disable" ' +
            'onclick="javascript:clickPermissionDisable(' + row.id + ')" >停用</button>'];
        }

    }

    function formatOperatIcon(value, row, index) {
        if (value != '') {
            var class_str = 'menu-icon ' + value;
            return "<i class=\"" + class_str + "\" style=\"font-size:18px\"></i>";
        }
        return '';
    }

    //添加按钮点击
    $("#add").on('click', function (e) {

        window.location.href = "/permission/add";
    });

    //更新按钮点击
    $("#update").on('click', function (e) {
        var arr = table.bootstrapTable('getSelections');
        var len = arr.length;
        if (len === 0) {
            return swal({text: '请选择需要编辑的选项', type: 'warning'});
        }
        else if (len > 1) {

            return swal({text: '不能同时编辑多个选项', type: 'warning'});
        } else {

            var update_obj = arr[0];
            var status = update_obj['status'];
            if (status != 0) {
                return swal({text: '停用权限不能编辑', type: 'warning'});
            }

            window.location.href = "/permission/update/" + arr[0].id;
        }

    });

    //delete 按钮点击
    $("#delete").on('click', function (e) {
        
        var isDefault = checkNoDefaultPermission();
        if (!isDefault) {
            deletePermission();
        }else {
            swal({text: '默认权限不能删除', type: 'warning'});
            return;
        }

    });

    //检查没有默认权限
    function checkNoDefaultPermission() {
        var arr = table.bootstrapTable('getSelections');
        for (var i = 0; i < arr.length; i++) {
            if (arr[i].type == "默认权限") {
                return true;
            }
        }
        return false
    }

    function deletePermission() {
        var arr = table.bootstrapTable('getSelections');
        var len = arr.length;
        if (len === 0) {
            return swal({text: '请选择需要删除的选项', type: 'warning'});

        } else {

            var result = [];
            for (var i = 0; i < arr.length; i++) {
                result.push(arr[i].id);
            }
            swal({
                    title: "确认删除?",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "确认",
                    cancelButtonText: "取消",
                    closeOnConfirm: false,
                    closeOnCancel: true
                },
                function (isConfirm) {
                    if (isConfirm) {
                        // //删除选择的选项
                        $.ajax({
                            url: "/permission/delete/" + result,
                            type: 'POST',
                            data: {},
                            success: function (data) {
                                var d = JSON.parse(data);
                                // alert_dialog(d['desc'])
                                if (d['code'] == '0') {
                                    swal({text: d['desc'], type: 'success'}, function () {
                                        window.location.reload();
                                    });

                                } else {
                                    swal({text: d['desc'], type: 'error'});
                                }
                            },
                            error: function (res) {
                                
                            }

                        });
                    }
                });
        }
    }



});

//启用权限
function clickPermissionEnable(id) {
    var result = [id];
    swal({
            title: "确认停用?",
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "确认",
            cancelButtonText: "取消",
            closeOnConfirm: false,
            closeOnCancel: true
        },
        function (isConfirm) {
            if (isConfirm) {
                // //删除选择的选项
                $.ajax({
                    url: "/permission/disable/" + result,
                    type: 'POST',
                    success: function (data) {
                        var d = JSON.parse(data);
                        if (d['code'] == '0') {
                            swal({text: d['desc'], type: 'success'}, function () {
                                window.location.reload();
                            });

                        } else {
                            swal({text: d['desc'], type: 'error'});
                        }

                    },

                });
            }
        });
}

//停用权限
function clickPermissionDisable(id) {
    swal({
            title: "恢复为正常状态?",
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "确认",
            cancelButtonText: "取消",
            closeOnConfirm: false,
            closeOnCancel: true
        },
        function (isConfirm) {
            if (isConfirm) {
                // 更改状态选择的选项
                $.ajax({
                    url: "/permission/usable",
                    type: 'POST',
                    data: {
                        id: id
                    },
                    success: function (data) {

                        var d = JSON.parse(data)
                        if (d['code'] == '0') {
                            swal({text: d['desc'], type: 'success'}, function () {
                                window.location.reload();
                            });
                        } else {
                            swal({text: d['desc'], type: 'error'});
                        }
                    },

                });
            }
        });
}