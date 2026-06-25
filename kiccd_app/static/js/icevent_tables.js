/**
 * Module/App: Datatables for Site Tables
 */


$(document).ready(function () {
    "use strict";

    // Default Datatable
    $('#basic-datatable').DataTable({
        order: [],
        keys: false,
        fixedHeader: true,
        pageLength: 50,
        layout: {
        topStart: {pageLength: {menu: [50, 100, 150, 200]}},
        topEnd: {search: {placeholder: 'Search'}},
        bottomStart: 'info',
        bottomEnd: 'paging',
        bottom: {buttons: ['copy', 'csv', 'pdf']}  
        },      
        "language": {
            "paginate": {
                "previous": "<i class='ti ti-chevron-left'>",
                "next": "<i class='ti ti-chevron-right'>"
            }
        },
    
        "drawCallback": function () {
            $('.dataTables_paginate > .pagination').addClass('pagination-rounded');
        }
    });

    // Buttons examples
    // var table = $('#datatable-buttons').DataTable({
    //   lengthChange: false,
    //   buttons: ['copy', 'print'],
    //   "language": {
    //       "paginate": {
    //           "previous": "<i class='ti ti-chevron-left'>",
    //           "next": "<i class='ti ti-chevron-right'>"
    //       }
    //   },
    //   "drawCallback": function () {
    //       $('.dataTables_paginate > .pagination').addClass('pagination-rounded');
    //   }
    // });

    table.buttons().container().appendTo('#datatable-buttons_wrapper .col-md-6:eq(0)');



    // Multi Selection Datatable
    // $('#selection-datatable').DataTable({
    //     select: {
    //         style: 'multi'
    //     },
    //     "language": {
    //         "paginate": {
    //             "previous": "<i class='ti ti-chevron-left'>",
    //             "next": "<i class='ti ti-chevron-right'>"
    //         }
    //     },
    //     "drawCallback": function () {
    //         $('.dataTables_paginate > .pagination').addClass('pagination-rounded');
    //     }
    // });


    // Alternative Pagination Datatable
    // $('#alternative-page-datatable').DataTable({
    //     "pagingType": "full_numbers",
    //     "drawCallback": function () {
    //         $('.dataTables_paginate > .pagination').addClass('pagination-rounded');
    //     }
    // });

    // Scroll Vertical Datatable
    // $('#scroll-vertical-datatable').DataTable({
    //     "scrollY": "350px",
    //     "scrollCollapse": true,
    //     "paging": false,
    //     "language": {
    //         "paginate": {
    //             "previous": "<i class='ti ti-chevron-left'>",
    //             "next": "<i class='ti ti-chevron-right'>"
    //         }
    //     },
    //     "drawCallback": function () {
    //         $('.dataTables_paginate > .pagination').addClass('pagination-rounded');
    //     }
    // });

    // Scroll Vertical Datatable
    // $('#scroll-horizontal-datatable').DataTable({
    //     "scrollX": true,
    //     "language": {
    //         "paginate": {
    //             "previous": "<i class='ti ti-chevron-left'>",
    //             "next": "<i class='ti ti-chevron-right'>"
    //         }
    //     },
    //     "drawCallback": function () {
    //         $('.dataTables_paginate > .pagination').addClass('pagination-rounded');
    //     }
    // });

    // Complex headers with column visibility Datatable
    // $('#complex-header-datatable').DataTable({
    //     "language": {
    //         "paginate": {
    //             "previous": "<i class='ti ti-chevron-left'>",
    //             "next": "<i class='ti ti-chevron-right'>"
    //         }
    //     },
    //     "drawCallback": function () {
    //         $('.dataTables_paginate > .pagination').addClass('pagination-rounded');
    //     },
    //     "columnDefs": [{
    //         "visible": false,
    //         "targets": -1
    //     }]
    // });

    // Row created callback Datatable
    // $('#row-callback-datatable').DataTable({
    //     "language": {
    //         "paginate": {
    //             "previous": "<i class='ti ti-chevron-left'>",
    //             "next": "<i class='ti ti-chevron-right'>"
    //         }
    //     },
    //     "drawCallback": function () {
    //         $('.dataTables_paginate > .pagination').addClass('pagination-rounded');
    //     },
    //     "createdRow": function (row, data, index) {
    //         if (data[5].replace(/[\$,]/g, '') * 1 > 150000) {
    //             $('td', row).eq(5).addClass('text-danger');
    //         }
    //     }
    // });

    // State Saving Datatable
    // $('#state-saving-datatable').DataTable({
    //     stateSave: true,
    //     "language": {
    //         "paginate": {
    //             "previous": "<i class='ti ti-chevron-left'>",
    //             "next": "<i class='ti ti-chevron-right'>"
    //         }
    //     },
    //     "drawCallback": function () {
    //         $('.dataTables_paginate > .pagination').addClass('pagination-rounded');
    //     }
    // });

    // Fixed header Datatable
    // $('#fixed-header-datatable').DataTable({
    //     fixedHeader: true,
    // });

    // Fixed Columns Datatable
    // $('#fixed-columns-datatable').DataTable({
    //     scrollY: 300,
    //     scrollX: true,
    //     scrollCollapse: true,
    //     paging: false,
    //     fixedColumns: true
    // });

    $(".dataTables_length select").addClass('form-select form-select-sm');
    $(".dataTables_length label").addClass('form-label');

});
