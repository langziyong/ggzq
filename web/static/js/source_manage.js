let PAGE = 1
let LIMIT = 50
let ALL_PAGE = null


$(function () {
    $("#previous_page").click(function () {
            turn_pages("previous")
        }
    )
    $("#next_page").click(function () {
            turn_pages("next")
        }
    )
    $("#add_source").click(function () {
        $(".source_manage_display").hide()
        $(".load_web_detailed").show().load("/manageApi/add_source #load_this", function () {
            $("#back").click(function () {
                $(".load_web_detailed").hide()
                $(".source_manage_display").show()
            })
        })
    })
    load_data_to_table()
})

function load_data_to_table() {
    let table_body = $(".source_manage_display_body")

    $.ajax({
        url: "/api/get_source?page=" + PAGE + "&limit=" + LIMIT,
        type: "GET",
        complete: function (r, s) {
            if (s === "success") {
                let data = r["responseJSON"]["data"]
                console.log(data)
                ALL_PAGE = Math.ceil(r["responseJSON"]["total"] / LIMIT)
                table_body.html("")
                for (const d in data) {
                    let html_f = `
                        <div class="source_unit">
                        <span class="flex_item flex_item_1" style="text-align: center">${data[d]["id"]}</span>
                        <span class="flex_item flex_item_2" >${data[d]["web_name"]}</span>
                        <span class="flex_item flex_item_3"><a target="_blank" href="${data[d]["web_url"]}">${data[d]["web_url"]}</a></span>
                        <span class="flex_item flex_item_1" style="text-align: center;color: ${data[d]["web_status"] === "FAIL" ? "red" : "green"}">${data[d]["web_status"]}</span>
                        <span class="flex_item flex_item_1" style="text-align: center">${data[d]["web_info"]}</span>
                        <span class="flex_item flex_item_1" style="text-align: center;color: ${data[d]["disabled"] === 0 ? "" : "red"}">${data[d]["disabled"] === 0 ? "YES" : "DISABLED"}</span>
                        <span class="flex_item flex_item_2" style="text-align: center">
                            <a target="_blank" style="color: rgb(0, 0, 0);cursor: pointer" apiurl="/manageApi/edit?id=${data[d]["id"]}" class="edit_btn">编辑</a>   
                            <a target="_blank" v="${data[d]["disabled"] === 0 ? "1" : "0"}" style="color: ${data[d]["disabled"] === 0 ? "black" : "green"};cursor: pointer" class="disabled_btn" apiurl="/manageApi/disabled?id=${data[d]["id"]}">${data[d]["disabled"] === 0 ? "禁用" : "启用"}</a>
                            <a target="_blank" style="color: rgb(0, 0, 0);cursor: pointer" apiurl="/manageApi/delete?id=${data[d]["id"]}" class="delete_btn">删除</a>
                        </span>
                        </div>`
                    table_body.append(html_f)
                }
                $(".edit_btn").click(function () {
                    $(".source_manage_display").hide()
                    $(".load_web_detailed").show().load($(this).attr("apiurl") + " #load_this", function () {
                        $("#back").click(function () {
                            $(".load_web_detailed").hide()
                            $(".source_manage_display").show()
                        })
                    })
                })
                $(".disabled_btn").click(function () {
                    let url = $(this).attr("apiurl") +"&v=" + $(this).attr("v")
                    $.ajax({
                        url: url,
                        complete: function (r, s) {
                            if (s === "success") {
                                console.log(r["responseJSON"])
                                alert("更改成功")
                                location.reload()
                            } else {
                                alert("网络连接失败")
                            }
                        }
                    })
                })
                $(".delete_btn").click(function () {
                    let url = $(this).attr("apiurl")
                    $.ajax({
                        url: url,
                        complete: function (r, s) {
                            if (s === "success") {
                                console.log(r["responseJSON"])
                                alert("删除成功")
                                location.reload()
                            } else {
                                alert("网络连接失败")
                            }
                        }
                    })
                })
                $("#now_page").html(PAGE)
                $("#info").html(`共${r["responseJSON"]["total"]}条记录`)
                // $("#test_info").html(`当前第${PAGE}页,总${ALL_PAGE}页`)
            } else {
                console.log(r)
                alert("网络连接失败")
            }
        }
    })
}

function turn_pages(direction) {
    if (direction === "previous") {
        PAGE--
        if (PAGE === 0) {
            PAGE = 1
            alert("已经是第一页啦")
            return 0
        }
        load_data_to_table()
    } else {
        if (PAGE > ALL_PAGE) {
            PAGE = ALL_PAGE
            alert("已经是最后一页啦")
            return 0
        }
        PAGE++
        load_data_to_table()
    }
}


