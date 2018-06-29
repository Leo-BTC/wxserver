/**
 * Created by 440S on 2017/11/1.
 */

jQuery(function () {

    $(function () {
        var deboxlist = $('.debox').bootstrapDualListbox({
            nonSelectedListLabel: '可选择权限',
            selectedListLabel: '已选择权限',
            filterPlaceHolder: 'filter',
            showFilterInputs: true, //false
            // preserveSelectionOnMove: 'moved',
            moveOnSelect: false,
        });

    });

})

