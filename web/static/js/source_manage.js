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

    $("")

    load_data_to_table()
})

function load_data_to_table() {
    let table = $("#source_table");
    let table_body = table.find("tbody")

    $.ajax({
        url: "/api/get_all_source?page=" + PAGE + "&limit=" + LIMIT,
        type: "get",
        complete: function (r, s) {
            if (s === "success") {
                let data = r["responseJSON"]["data"]
                ALL_PAGE = Math.ceil(r["responseJSON"]["total"] / LIMIT)
                table_body.html("")
                for (const d in data) {
                    let html_f = `<tr><td>${data[d]["id"]}</td><td><a href="#">${data[d]["web_name"]}</a></td><td><a href="${data[d]["web_url"]}">${data[d]["web_url"]}</a></td><td>未定义</td><td><a href="">删除</a><a href="">修改</a></td></tr>`
                    table_body.append(html_f)
                }
                $("#now_page").html(PAGE)
                $("#test_info").html(`当前第${PAGE}页,总${ALL_PAGE}页`)
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
