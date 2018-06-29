/**
 * Created by WangYingqi
 */
jQuery(function () {
    var $table = $('#bootstrap-table');
    var sort = function (value, row, index) {
        var pageSize = $table.bootstrapTable('getOptions').pageSize;//通过表的#id 可以得到每页多少条
        var pageNumber = $table.bootstrapTable('getOptions').pageNumber;//通过表的#id 可以得到当前第几页
        return pageSize * (pageNumber - 1) + index + 1;  //返回每条的序号： 每页条数 * （当前页 - 1 ）+ 序号
    };
    $(document).ready(function () {
        $table.bootstrapTable({
            url: '/ztest/get/list',  // table 请求路径 指向路由
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
            columns()

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
        function formatOperat(row) {
            return ['<a href="' + '/ztest/edit/' + row + '" ><button class="btn btn-round btn-xs btn-info btn-fill" >查看/编辑</button></a>'];
        }
        function formatOperatStatus(value, row, index) {
            if (value == 0) {
                return ['False'];
            } else {
                return ['True'];
            }
        }
    });


    $("#add").on('click', function (e) {
        window.location.href = "/ztest/add";
    });
    $("#update").on('click', function (e) {
        var arr = $('#bootstrap-table').bootstrapTable('getSelections');
        var len = arr.length;
        if (len == 0) {
            return swal({text: '请选择需要编辑的选项', type: 'warning'});

        }
        else if (len > 1) {

            return swal({text: '不能同时编辑多个选项', type: 'warning'});
        } else {
            window.location.href = "/ztest/edit/" + arr[0].id
        }

    });
    $("#delete").on('click', function (e) {
        var arr = $('#bootstrap-table').bootstrapTable('getSelections');
        var len = arr.length;
        if (len == 0) {
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
                            url: "/ztest/delete/" + result,
                            type: 'POST',
                            data: {},
                            success: function (data) {
                                var d = JSON.parse(data);
                                if (d['code'] == '00') {
                                    swal({text: d['desc'], type: 'success'}, function () {
                                        window.location.reload();
                                    });

                                } else {
                                    swal({text: d['desc'], type: 'error'});
                                }
                            }
                        });
                    }
                });
        }
    });
});
