/**
 * Created by PC on 2017/11/1.
 * bootstrap-table----参考文档
 * http://bootstrap-table.wenzhixin.net.cn/zh-cn/documentation/
 */
jQuery(function () {
    var $table = $('#bootstrap-table');

    $(document).ready(function () {
        var pospDataTable = $table.bootstrapTable({
            url: '/sysrole/role/get/list',  // table 请求路径
            toolbar: ".toolbar",
            showRefresh: true,
            search: true,
            showToggle: true,
            showColumns: true,
            onlyInfoPagination: true,
            clickToSelect: true,  //触发选中事件
            pagination: true,
            sortable: true,                     //是否启用排序
            sortOrder: "desc",
            sidePagination: "server",
            searchAlign: 'left',
            pageSize: 5,    //
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
                    // field: 'id',
                    align: 'center',
                },
                {
                    field: 'name',
                    title: '角色',
                    align: 'center',
                    sortable: true,
                    // sortOrder: "desc",
                },
                {
                    field: 'description',
                    title: '描述',
                    align: 'center',
                    sortable: true,
                    // sortOrder: "desc",
                },
                {
                    field: 'org_id',
                    title: '所属机构',
                    align: 'center',
                    sortable: true,
                    // sortOrder: "desc",
                },
                {
                    field: 'role_type',
                    title: '创建类型',
                    align: 'center',
                    sortable: true,
                    // sortOrder: "desc",
                },
                {
                    field: 'status',
                    title: '状态',
                    align: 'center',
                    sortable: true,
                    // sortOrder: "desc",
                    formatter: formatOperatStatus,

                },
                {
                    field: 'id',
                    title: '操作',
                    align: 'center',
                    valign: 'middle',
                    formatter: formatOperat
                }

            ],
            formatShowingRows: function (pageFrom, pageTo, totalRows) {
                //do nothing here, we don't want to show the text "showing x of y from..."
                return "总计：" + totalRows + "条";
            },
            formatRecordsPerPage: function (pageNumber) {
                return pageNumber + " 显示";
            },
            icons: {
                refresh: 'fa fa-refresh',
                toggle: 'fa fa-th-list',
                columns: 'fa fa-columns',
                detailOpen: 'fa fa-plus-circle',
                detailClose: 'fa fa-minus-circle'
            },
            onClickRow: function (row, $element) {
                // 当某一行被点击时触发该事件
            },
            onCheck: function (row) {
                // 当某一行被选中时触发

            },
            onCheckAll: function (rows) {
                // 全部行被选中时触发
            }
        });

        //activate the tooltips after the data table is initialized
        $('[rel="tooltip"]').tooltip();

        $(window).resize(function () {
            $table.bootstrapTable('resetView');
        });


    });


    function formatOperatStatus(value, row, index) {
        if (value == '正常') {
            return ['<span class=" btn-round btn-xs btn-success btn-fill">正常</span>'];
        } else {
            return ['<span class=" btn-round btn-xs btn-danger btn-fill">停用</span>'];
        }

    }

    function formatOperat(value, row, index) {
        // alert(row.status)
        // if (row.id == 1) {
        //     return ['<span   class="btn btn-round btn-xs btn-info btn-fill"  onclick="javascript:givepower(' + row.id + ');"  )">授权/查看</span>' + ' ' +
        //     '<span     class="btn btn-round btn-xs btn-warning btn-fill"   >更改状态</span> '];
        // }
        if (row.status == "正常") {
            return ['<span   class="btn btn-round btn-xs btn-info btn-fill"  onclick="javascript:givepower(' + row.id + ');"  )">授权/查看</span>' + ' ' +
            '<span   class="btn btn-round btn-xs btn-info btn-fill"  onclick="javascript:editrole(' + row.id + ',1);"  )">编辑</span>' + ' ' +
            '<span     class="btn btn-round btn-xs btn-warning btn-fill" onclick="javascript:changeStatus(' + row.id + ');" >更改状态</span> '];
        } else {
            return ['<span   class="  btn-round btn-xs btn-info btn-fill"  onclick="javascript:givepower(' + row.id + ');"  )">授权/查看</span>' + ' ' +
            '<span   class="btn btn-round btn-xs btn-info btn-fill"  onclick="javascript:editrole(' + row.id + ',0);"  )">编辑</span>' + ' ' +
            '<span    class=" btn-round btn-xs btn-warning btn-fill" onclick="javascript:changeStatus(' + row.id + ');" >更改状态</span> '];
        }
    }


    $table.on('click', '#title_id--title_id', function () {
        var arr = $('#bootstrap-table').bootstrapTable('getSelections');
        swal({
                title: "确认更改状态?",
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
                        url: "/sysrole/role/changestatus/?status=" + arr[0].status + "&id=" + arr[0].id,
                        type: 'POST',
                        data: {},
                        success: function (data) {
                            var d = JSON.parse(data)
                            // alert_dialog(d['desc'])
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

    });

    $table.on('click', '#see', function () {
        var arr = $('#bootstrap-table').bootstrapTable('getSelections');
        window.location.href = "/sysrole/role/role_management/?name=" + arr[0].name + "&des=" + arr[0].description + "&id=" + arr[0].id
    });


    $("#add").on('click', function (e) {

        window.location.href = "/sysrole/role/add"
    })

    $("#delete").on('click', function (e) {
        var arr = $('#bootstrap-table').bootstrapTable('getSelections');
        if (arr.length != 0) {
            if (arr.length > 1) {
                swal({text: '不能同时多选', type: 'warning'});
            } else if (arr[0].id == 1) {
                swal({text: '超级管理员不能删除', type: 'warning'});
            } else {
                swal({
                        title: "确认删除角色吗?",
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
                                url: "/sysrole/role/delete/?id=" + arr[0].id,
                                type: 'POST',
                                data: {},
                                success: function (data) {
                                    var d = JSON.parse(data)
                                    // alert_dialog(d['desc'])
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
        } else {
            swal({text: '请选择需要删除的选项', type: 'warning'});
        }

    })

    $("#update").on('click', function (e) {

        window.location.href = "/sysrole/role/role_management/"
    })


})

function editrole(id, num) {
    if (id == 1) {
        swal("不能编辑超级管理员")
    }
    else {
        if (num == 0) {
            swal("停用时不能编辑")
        }
        else {
         window.location.href = "/sysrole/role/edit/?id=" + id  ;

        }

    }


}

function changeStatus(id) {

    if (id == 1) {
        swal("不能改变超级管理员状态")
    } else {
        swal({
                title: "确认更改状态?",
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
                        url: "/sysrole/role/changestatus/?id=" + id,
                        type: 'POST',
                        data: {},
                        success: function (data) {
                            var d = JSON.parse(data)
                            // alert_dialog(d['desc'])
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

}

function givepower(id) {

    window.location.href = "/sysrole/role/role_management/?id=" + id

}





