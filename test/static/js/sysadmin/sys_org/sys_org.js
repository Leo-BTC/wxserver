/**
 * Created by PC on 2017/11/1.
 * bootstrap-table----参考文档
 * http://bootstrap-table.wenzhixin.net.cn/zh-cn/documentation/
 */
jQuery(function () {
    var $table = $('#bootstrap-table');

    $(document).ready(function () {

        $table.bootstrapTable({
            url: '/sysorg/org/get/list',  // table 请求路径
            toolbar: ".toolbar",
            showRefresh: true,
            search: true,
            showToggle: true,
            showColumns: true,
            clickToSelect: true,  //触发选中事件
            onlyInfoPagination: true,
            pagination: true,
            sortable: true,                     //是否启用排序
            sortOrder: "asc",
            sidePagination: "server",
            searchAlign: 'left',
            pageSize: 5,    // 前端分页数量
            pageList: [5, 10, 20,],  // 前端分页展示数据
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
                    field: 'org_name',
                    title: '机构名',
                    align: 'center',
                    sortable:true,
                    sortOrder: "asc",
                },
                {
                    field: 'tel',
                    title: '联系方式',
                    align: 'center',
                      sortable:true,
                    sortOrder: "asc",
                },
                {
                    field: 'org_id',
                    title: '机构号',
                    align: 'center',
                    sortable:true,
                    sortOrder: "asc",
                },
                {
                    field: 'org_code',
                    title: '机构编码',
                    align: 'center',
                    sortable:true,
                    sortOrder: "asc",
                },
                {
                    field: 'status',
                    title: '状态',
                    align: 'center',
                    sortable:true,
                    sortOrder: "asc",
                    formatter: formatOperatStatus
                },
                {
                    field: 'id',
                    title: '操作',
                    align: 'center',
                    // valign: 'middle',
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
            },

        });

        //activate the tooltips after the data table is initialized
        $('[rel="tooltip"]').tooltip();

        $(window).resize(function () {
            $table.bootstrapTable('resetView');
        });


    });

    function formatOperat(value, row, index) {
        return ['<a href="' + '/sysorg/edit/org/' + row.id +'/0'+ '" ><button class="btn btn-round btn-xs btn-info btn-fill" >查看/编辑</button></a>'];
    }

    function formatOperatStatus(value, row, index) {
        if (value == '正常') {
            return ['<button class="btn btn-round btn-xs btn-success btn-fill" id="to_end" onclick="javascript:clickOrgEnable('+row.id+') ">正常</button>'];
        } else if (value == '停用'){
            return ['<button class="btn btn-round btn-xs btn-error btn-fill" id="to_start" onclick="javascript:clickOrgDisable('+row.id+') ">停用</button>'];
        }

    }


    $("#delete").on('click', function (e) {
        var arr = $('#bootstrap-table').bootstrapTable('getSelections');
        if (arr.length != 0) {
            if (arr.length > 1) {
                swal({text: '不能同时多选', type: 'warning'});
            } else {
                swal({
                        title: "确认删除此机构吗?",
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
                                url: "/sysorg/org/delete/?id=" + arr[0].id,
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
            swal({text: '请选择需要停用的选项', type: 'warning'});
        }

    })

    $("#add").on('click', function (e) {
        window.location.href = "/sysorg/org/add"
    })


});


function clickOrgEnable(id) {
    var result = id;

    if (id == 1) {
        swal({text: '该机构不能被停用', type: 'error'});
        return;
    }

    swal({
            title: "确认停用机构?",
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
                    url: "/sysorg/org/changestatus/?id=" + result,
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


function clickOrgDisable(id) {
    var result = id;

    swal({
            title: "确认启用机构?",
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
                    url: "/sysorg/org/changestatus/?id=" + result,
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