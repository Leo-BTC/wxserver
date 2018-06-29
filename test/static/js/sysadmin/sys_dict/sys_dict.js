/**
 * Created by PC on 2017/11/1.
 * bootstrap-table----参考文档
 * http://bootstrap-table.wenzhixin.net.cn/zh-cn/documentation/
 */
jQuery(function () {
    var $table = $('#bootstrap-table');

    $(document).ready(function () {
        $table.bootstrapTable({
            url: '/sysdict/dict/get_list',  // table 请求路径 指向路由
            toolbar: ".toolbar",
            showRefresh: true,
            search: true,
            showToggle: true,
            showColumns: true,
            sortable:true,
            sortOrder:'asc',
            clickToSelect: true,  //触发选中事件
            pagination: true,
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
                    align: 'center',
                },
                {
                    field: 'sort',
                    title: '序号',
                    align: 'center',
                     sortable:true,
                    sortOrder: "asc",
                },

                {
                    field: 'dict_name',
                    title: '字典名称',
                    align: 'center',
                     sortable:true,
                    sortOrder: "asc",
                },
                {
                    field: 'dict_id',
                    title: '字典id号',
                    align: 'center',
                     sortable:true,
                    sortOrder: "asc",
                },
                {
                    field: 'dict_type',
                    title: '字典类型',
                    align: 'center',
                     sortable:true,
                    sortOrder: "asc",
                },
                {
                    field: 'description',
                    title: '描述',
                    align: 'center',
                     sortable:true,
                    sortOrder: "asc",
                },
                {
                    field: 'remarks',
                    title: '备注',
                    align: 'center',
                     sortable:true,
                    sortOrder: "asc",
                },
                {
                    field: 'del_flag',
                    title: '状态',
                    align: 'center',
                     sortable:true,
                    sortOrder: "asc",
                    formatter: formatOperatStatus
                },
                // {
                //     field: 'Status',
                //     title: '操作',
                //     align: 'center',
                //     valign: 'middle',
                //     formatter: formatOperat
                // }

            ],

            formatShowingRows: function (pageFrom, pageTo, totalRows) {
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
        if (value == 0) {
            return ['<button class="btn btn-round btn-xs btn-success btn-fill">正常</button>'];
        } else {
            return ['<button class="btn btn-round btn-xs btn-error btn-fill" onclick="javascript:disable(' + row.id + ')">停用</button>'];
        }

    }

    $("#add").on('click', function (e) {

        window.location.href = "/sysdict/dict_add";
    })
    $("#update").on('click', function (e) {
        var arr = $('#bootstrap-table').bootstrapTable('getSelections');
        var len = arr.length
        if (len == 0) {
            return swal({text: '请选择需要编辑的选项', type: 'warning'});

        }
        else if (len > 1) {

            return swal({text: '不能同时编辑多个选项', type: 'warning'});
            ;
        } else {
            window.location.href = "/sysdict/dict_update/" + arr[0].id
        }

    })
    $("#delete").on('click', function (e) {
        var arr = $('#bootstrap-table').bootstrapTable('getSelections');
        var len = arr.length
        if (len == 0) {
            return swal({text: '请选择需要停用的选项', type: 'warning'});

        } else {

            var result = []
            for (var i = 0; i < arr.length; i++) {
                result.push(arr[i].id);
            }

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
                            url: "/sysdict/dict_delete/" + result,
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
    });

    $("#import").on('click', function (e) {
        e.preventDefault();

        swal({
            title: '请选择文件',
            html: '<input id="file" class="form-control" type="file">',
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "确认",
            cancelButtonText: "取消",
            closeOnConfirm: false,
            closeOnCancel: true
        }, function (isConfirm) {
            if (isConfirm) {
                var formData = new FormData();
                formData.append("file", document.getElementById("file").files[0]);
                $.ajax({
                    url: "/sysdict/dict_import",
                    type: 'POST',
                    data: formData,
                    /**
                     *必须false才会自动加上正确的Content-Type
                     */
                    contentType: false,
                    /**
                     * 必须false才会避开jQuery对 formdata 的默认处理
                     * XMLHttpRequest会对 formdata 进行正确的处理
                     */
                    processData: false,
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
            } else {

            }
        });


    });

    $("#export").on('click', function (e) {
        e.preventDefault();
        location.href = "/sysdict/dict_export";
    });

});

function disable(id) {
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
                    url: "/sysdict/dict_update_del_flag",
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
