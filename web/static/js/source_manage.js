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
                    let color = "green"
                    if (data[d]["web_status"] === "FAIL"){
                        color = "red"
                    }
                    let html_f = `
                <div class="source_unit">
                <span class="flex_item flex_item_1" style="text-align: center">${data[d]["id"]}</span>
                <span class="flex_item flex_item_2" >${data[d]["web_name"]}</span>
                <span class="flex_item flex_item_3"><a  href="${data[d]["web_url"]}">${data[d]["web_url"]}</a></span>
                <span class="flex_item flex_item_1" style="text-align: center;color: ${color}">${data[d]["web_status"]}</span>
                <span class="flex_item flex_item_1">${data[d]["web_info"]}</span>
                <span class="flex_item flex_item_1" style="text-align: center">${data[d]["disabled"]}</span>
                <span class="flex_item flex_item_2" style="text-align: center">
                    <a style="color: rgb(0, 0, 0)" href="www.baidu.com">编辑</a>
                    <a style="color: rgb(0, 0, 0)" href="www.baidu.com">禁用</a>
                    <a style="color: rgb(0, 0, 0)" href="www.baidu.com">删除</a>
                </span>
                </div>`
                    table_body.append(html_f)
                }
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

