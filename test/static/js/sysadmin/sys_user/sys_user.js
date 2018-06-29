/**
 * Created by PC on 2017/11/1.
 * bootstrap-table----参考文档
 * http://bootstrap-table.wenzhixin.net.cn/zh-cn/documentation/
 */
jQuery(function () {
    var $table = $('#bootstrap-table');

    $(document).ready(function () {



        $table.bootstrapTable({
            url: '/sysuser/user/list',  // table 请求路径
            toolbar: ".toolbar",
            showRefresh: true,
            search: true,
            showToggle: true,
            showColumns: true,
            clickToSelect: false,  //触发选中事件
            onlyInfoPagination:true,
            sortable: true,                     //是否启用排序
            sortOrder: "desc" ,
            pagination: true,
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
                    field: 'username',
                    title: '账号',
                    align: 'center',
                    sortable:true,
                    //sortOrder: "asc",

                },
                {
                    field: 'mobile',
                    title: '手机号',
                    align: 'center',
                    sortable:true,
                    //sortOrder: "asc",

                },
                {
                    field: 'email',
                    title: '邮箱',
                    align: 'center',
                    sortable:true,
                    //sortOrder: "asc",

                },
                {
                    field: 'org_name',
                    title: '所属机构',
                    align: 'center',
                    sortable:true,
                    //sortOrder: "asc",

                },
                {
                    field: 'role',
                    title: '角色',
                    align: 'center',
                    sortable:true,
                    //sortOrder: "asc",

                },
                {
                    field:'update_time',
                    title:'更新时间',
                    align:'center',
                    sortable:true,
                    sortOrder:"desc",
                },
                {
                    field:'login_time',
                    title:'上次登陆时间',
                    align:'center',
                    sortable:true,
                    //sortOrder:"desc"
                },
                {
                    field: 'status',
                    title: '状态',
                    align: 'center',
                    sortable:true,
                    //sortOrder: "asc",
                    formatter: formatOperatStatus,


                },
                {
                    field: 'Status',
                    title: '操作',
                    align: 'center',
                    valign: 'middle',
                    sortable:true,
                    //sortOrder: "asc",
                    formatter: formatOperat
                }

            ],
            // 设置列表总数
            formatShowingRows: function (pageFrom, pageTo, totalRows) {
                //do nothing here, we don't want to show the text "showing x of y from..."
                return "总计：" + totalRows + "条";
            },
            // formatDetailPagination:function (totalRows) {
            //     // return "总计" + totalRows + "条";
            // },
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

        });

        //activate the tooltips after the data table is initialized
        $('[rel="tooltip"]').tooltip();

        $(window).resize(function () {
            $table.bootstrapTable('resetView');
        });


    });




    function formatOperat(value, row, index) {
        return ['<button class="btn btn-round btn-xs btn-success btn-fill" onclick="javascript:resetPassword('+row.id+')" id="reset">重置密码</button>' + '<a href="'+'/sysuser/update/user/' +row.id +'" ><button class="btn btn-round btn-xs btn-info btn-fill" >查看/编辑</button></a>'].join('');
    }

    function formatOperatStatus(value, row, index) {
        if (value == 1) {
            return '<button class="btn btn-round btn-xs btn-success btn-fill" id="to_end" onclick="javascript:closeStatus('+row.id+');">正常</button>';
            //   return ['<button class="btn btn-round btn-xs btn-success btn-fill" id="to_end" >正常</button>'];
        } else {
            return ['<button class="btn btn-round btn-xs btn-error btn-fill" id="to_start" onclick="javascript:openStatus('+row.id+');">停用</button>'];
        }

    };



    $("#add").on('click', function (e) {

         window.location.href = "/sysuser/add/user/0"
    })
    $("#update").on('click', function (e) {
        var arr = $('#bootstrap-table').bootstrapTable('getSelections');
        var len = arr.length
        if (len == 0){
            return swal({text:'请选择需要编辑的选项',type:'warning'})
        }
        else if(len > 1){
             return swal({text:'不能同时编辑多个选项',type:'warning'})
        }else {
            window.location.href = "/sysuser/update/user/" + arr[0].id
        }

    })
    $("#delete").on('click', function(e){
        var arr = $('#bootstrap-table').bootstrapTable('getSelections');
        for(var i=0;i<arr.length;i++){
        }
        var len = arr.length
        if (len == 0){
            return swal({text:'请选择需要删除的选项',type:'warning'})
        }
        else if(len > 1){
             return swal({text:'不能同时删除多个选项',type:'warning'})
        }else {
            if (arr[0]['role'][0][0] == "超级管理员"){
                return swal({text:'不能同时删除超级管理员',type:'warning'})
            }else{
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
                    function(isConfirm){
                        if (isConfirm){
                            $.ajax({
                                url:'/sysuser/delete/user/'+arr[0].id,
                                success:function(data){
                                    data = JSON.parse(data)
                                    swal({text: data['msg'], type: 'success'},function(){
                                        window.location.reload()
                                        });
                                    }
                                })
                        }
                    }
                )

            }
        }
    })
})

function closeStatus(id){
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
        function(isConfirm){
            if (isConfirm){
                $.ajax({
                    url:'/sysuser/close/user/'+id,
                    success:function(data){
                        data = JSON.parse(data)
                        if (data['code'] == '-1'){
                            swal({
                                title:'超级管理员不能被停用！',
                                type:"warning",
                                showCancelButton: true,
                                confirmButtonColor: "#DD6B55",
                                confirmButtonText: "确认",
                                cancelButtonText: "取消",
                                closeOnConfirm: false,
                                closeOnCancel: true
                                },
                                function(isConfirm){
                                    if (isConfirm){
                                        window.location.reload()
                                    }
                                }
                            )
                        }else {
                            window.location.reload()
                        }

                    }

    })
            }
        })
    }

function openStatus(id){
    swal({
        title: "确认启用?",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "确认",
        cancelButtonText: "取消",
        closeOnConfirm: false,
        closeOnCancel: true
        },
        function(isConfirm){
            if (isConfirm){
                $.ajax({
                    url:'/sysuser/open/user/'+id,
                    success:function(data){
                        data = JSON.parse(data)
                        window.location.reload()
                    }

                })
            }

    })

    }

function resetPassword(id){
    swal({
        title: "确认重置密码?",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "确认",
        cancelButtonText: "取消",
        closeOnConfirm: false,
        closeOnCancel: true
        },
        function(isConfirm){
            if (isConfirm){
                $.ajax({
                    url:'/sysuser/reset/password/'+id,
                    success:function(data) {
                        data = JSON.parse(data)
                        if (data['code'] == '0'){
                            swal({text: "密码已成功发送至用户邮箱！", type: 'success'});
                        }else{
                            swal({text: "密码重置失败！", type: 'warning'});
                        }

                    }
                })
            }
        }
    )

    }