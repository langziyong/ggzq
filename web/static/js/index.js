let PAGE = 1
let LIMIT = 50
let ALL_PAGE = null
let WEIGHTS_VALUE = 0


$(function () {
    $("#previous_page").click(function () {
            turn_pages("previous")
        }
    )
    $("#next_page").click(function () {
            turn_pages("next")
        }
    )
    $("#search_jump").click(function () {
        let page_value = $("#to_page").val()
        let weights_value = $("#weights").val()

    })


    load_data_to_table()
})

function load_data_to_table() {
    let result_table = $("#result_table");
    let result_table_body = result_table.find("tbody")

    if (WEIGHTS_VALUE !== 0){
        PAGE = 1
        LIMIT = 50
        $.ajax({
            url: "/api/get_all_data_by_weights?page=" + PAGE + "&limit=" + LIMIT + "&weights=" + value,
            type: "get",
            complete: function (r, s) {
                if (s === "success") {
                    let data = r["responseJSON"]["data"]
                    ALL_PAGE = Math.ceil(r["responseJSON"]["total"] / LIMIT)
                    result_table_body.html("")
                    for (const d in data) {
                        let html_f = `<tr><td>${data[d]["id"]}</td><td><a href="${data[d]["web_url"]}">${data[d]["web_name"]}</a></td><td><a href="${data[d]["target_url"]}">${data[d]["target_title"]}</a></td><td>${data[d]["target_date"]}</td><td>${data[d]["weights"]}</td></tr>`
                        result_table_body.append(html_f)
                    }
                    $("#now_page").html(PAGE)
                    $("#test_info").html(`当前第${PAGE}页,总${ALL_PAGE}页\n权重搜索`)
                } else {
                    console.log(r)
                    alert("网络连接失败")
                }
            }
        })
        return 0
    }

    $.ajax({
        url: "/api/get_all_data?page=" + PAGE + "&limit=" + LIMIT,
        type: "get",
        complete: function (r, s) {
            if (s === "success") {
                let data = r["responseJSON"]["data"]
                ALL_PAGE = Math.ceil(r["responseJSON"]["total"] / LIMIT)
                result_table_body.html("")
                for (const d in data) {
                    let html_f = `<tr><td>${data[d]["id"]}</td><td><a href="${data[d]["web_url"]}">${data[d]["web_name"]}</a></td><td><a href="${data[d]["target_url"]}">${data[d]["target_title"]}</a></td><td>${data[d]["target_date"]}</td><td>${data[d]["weights"]}</td></tr>`
                    result_table_body.append(html_f)
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

