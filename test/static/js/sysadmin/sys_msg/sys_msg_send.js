/**
 * Created by PC on 2017/11/1.
 * bootstrap-table----参考文档
 * http://bootstrap-table.wenzhixin.net.cn/zh-cn/documentation/
 */
jQuery(function () {
    var $table = $('#bootstrap-table');

    $(document).ready(function () {
        $table.bootstrapTable({
            url: '/sysmsg/msg/get_send_list',  // table 请求路径
            toolbar: ".toolbar",
            showRefresh: true,
            search: true,
            showToggle: true,
            showColumns: true,
            clickToSelect: true,  //触发选中事件
            pagination: true,
            sortable: true,                     //是否启用排序
            sortOrder: "desc",
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
                    title: '序号',
                    align: 'center',
                    width: 5,
                    switchable: false,
                    formatter: function (value, row, index) {
                        var pageSize = $table.bootstrapTable('getOptions').pageSize;//通过表的#id 可以得到每页多少条
                        var pageNumber = $table.bootstrapTable('getOptions').pageNumber;//通过表的#id 可以得到当前第几页
                        return pageSize * (pageNumber - 1) + index + 1;  //返回每条的序号： 每页条数 * （当前页 - 1 ）+ 序号
                    }
                },

                {
                    field: 'msg_title',
                    title: '标题',
                    align: 'center',
                     sortable:true,
                    sortOrder: "desc",
                },
                {
                    field: 'msg_type',
                    title: '消息类型',
                    align: 'center',
                     sortable:true,
                    sortOrder: "desc",
                },
                {
                    field: 'msg_date',
                    title: '发送时间',
                    align: 'center',
                     sortable:true,
                    sortOrder: "desc",
                },
                {
                    field: 'Status',
                    title: '操作',
                    align: 'center',
                    valign: 'middle',
                    formatter: formatOperat
                }

            ],

            formatRecordsPerPage: function (pageNumber) {
                return pageNumber + " 显示";
            },
            formatShowingRows: function (pageFrom, pageTo, totalRows) {
                return "总计：" + totalRows + "条";
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


    function formatOperat(value, row, index) {
        return ['<button class="btn btn-round btn-xs btn-success btn-fill" onclick="javascript:btn_detail(' + row.id + ');">查看</button>' +' '+ '<button class="btn btn-round btn-xs btn-info btn-fill" id="btn_delete" onclick="javascript:btn_delete(' + row.id + ');">删除</button>'];


    }

    $("#add").on('click', function (e) {

        window.location.href = "/sysmsg/msg_add";
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
        delete_msg();
    });


    function delete_msg() {
        var arr = $('#bootstrap-table').bootstrapTable('getSelections');
        var len = arr.length
        if (len == 0) {
            return swal({text: '请选择需要删除的选项', type: 'warning'});

        } else {

            var result = []
            for (var i = 0; i < arr.length; i++) {
                result.push(arr[i].id);
            }

            swal({
                    title: "确认删除所选消息?",
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
                            url: "/sysmsg/msg_delete/" + result,
                            type: 'POST',
                            data: {},
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
    }

});

function btn_detail(id) {
    window.location.href = "/sysmsg/get_detail/" + id+"/1";
}

function btn_delete(id) {

    var result = [];
    result.push(id);
    swal({
            title: "确认删除所选消息?",
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
                    url: "/sysmsg/msg_delete/" + result,
                    type: 'POST',
                    data: {},
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
