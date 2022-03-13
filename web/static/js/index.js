let PAGE = 1
let LIMIT = 50
let ALL_PAGE = null
let CONDITION_ALL_PAGE = null
let WEIGHTS_VALUE = 0


$(function () {
    $("#weights").val("")
    $("#previous_page").click(function () {
            turn_pages("previous")
        }
    )
    $("#next_page").click(function () {
            turn_pages("next")
        }
    )
    $("#search_jump").click(function () {
        let weights_value = $("#weights").val()
        if (weights_value === ""){
            weights_value = 0
        }
        WEIGHTS_VALUE = weights_value
        PAGE = $("#to_page").val()
        console.log(PAGE)
        load_data_to_table()
    })
    $("#data_self_check").click(function () {
        let choose = confirm("数据清理将会重新根据现有关键词计算权重，并删除不符合要求的数据，此操作不可逆，还要继续吗？")
        if (choose === true){
            $.ajax({
                url: "/api/data_self_check",
                complete:function (r,s) {
                    if(s==="success"){
                        console.log(r)
                        alert(r["responseText"])
                    } else {
                        alert("网络连接失败")
                    }
                }
            })
        } else {
            console.log("什么也不干")
        }
    })

// 初始化界面
    load_data_to_table()
})

function load_data_to_table() {
    let result_table = $("#result_table");
    let result_table_body = result_table.find("tbody")

    if (WEIGHTS_VALUE !== 0){
        $.ajax({
            url: "/api/get_all_data_by_weights?page=" + PAGE + "&limit=" + LIMIT + "&weights=" + WEIGHTS_VALUE,
            type: "get",
            complete: function (r, s) {
                if (s === "success") {
                    let data = r["responseJSON"]["data"]
                    PAGE = r["responseJSON"]["page"]
                    CONDITION_ALL_PAGE = r["responseJSON"]["all_page"]
                    result_table_body.html("")
                    for (const d in data) {
                        let html_f = `<tr><td>${data[d]["id"]}</td><td><a target="_blank" href="${data[d]["web_url"]}">${data[d]["web_name"]}</a></td><td><a target="_blank" href="${data[d]["target_url"]}">${data[d]["target_title"]}</a></td><td>${data[d]["target_date"]}</td><td>${data[d]["weights"]}</td></tr>`
                        result_table_body.append(html_f)
                    }
                    console.log(r["responseJSON"])
                    $("#now_page").html(PAGE)
                    $("#page_info").html(`当前第${PAGE}页,总${CONDITION_ALL_PAGE}页`)
                    $("#to_page").html("")
                    for (let i = 1; i <= CONDITION_ALL_PAGE; i++) {
                        let html_f
                        if(i===PAGE){
                            html_f = `<option value="${i}" selected>${i}</option>`
                        } else {
                            html_f = `<option value="${i}">${i}</option>`
                        }
                        $("#to_page").append(html_f)
                    }
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
                PAGE = r["responseJSON"]["page"]
                ALL_PAGE = r["responseJSON"]["all_page"]
                console.log(r["responseJSON"])
                result_table_body.html("")
                for (const d in data) {
                    let html_f = `<tr><td>${data[d]["id"]}</td><td><a target="_blank" href="${data[d]["web_url"]}">${data[d]["web_name"]}</a></td><td><a target="_blank" href="${data[d]["target_url"]}">${data[d]["target_title"]}</a></td><td>${data[d]["target_date"]}</td><td>${data[d]["weights"]}</td></tr>`
                    result_table_body.append(html_f)
                }
                $("#now_page").html(PAGE)
                $("#page_info").html(`当前第${PAGE}页,总${ALL_PAGE}页`)
                $("#to_page").html("")
                for (let i = 1; i <= ALL_PAGE; i++) {
                    let html_f
                    if(i===PAGE){
                        html_f = `<option value="${i}" selected>${i}</option>`
                    } else {
                        html_f = `<option value="${i}">${i}</option>`
                    }
                    $("#to_page").append(html_f)
                }
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

