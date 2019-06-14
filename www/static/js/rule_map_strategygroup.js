//规则和策略联动显示
function rule_map_strategy(url, rule_id) {
    var rule_id = rule_id || $(".searchable-select-item.selected").data('value');
    $.ajax({
        url: url,
        data: {"rule_id": rule_id},
        dataType: "json",
        type: "GET",
        success: function (resp) {
            if (resp.state) {
                var strategys = JSON.stringify(resp.strategy_groups, null, 4);
                var strategy_groups_json = JSON.parse(strategys);

                $('.searchable-select-item').each(function (i) {
                    var group_rule_id = $(this).attr("data-value");
                    var _rule_id = group_rule_id.split("_")[0]
                    if (i > resp.rules_num) {
                        if (!(_rule_id in strategy_groups_json)) {
                            $(this).attr("style", "display: none;")
                        }
                        else {
                            $(this).removeAttr("style", "")
                        }
                    }
                    if (group_rule_id == "" || rule_id == "所有规则" || group_rule_id == "所有" || rule_id == "所有" || rule_id == "") {
                        $(this).removeAttr("style", "")
                    }

                })
            }
        }
    })

}
