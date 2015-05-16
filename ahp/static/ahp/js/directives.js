/**
 * Created by Repina on 15.03.2015.
 */
//project id должно быть в url
//наследует $scope контроллера (вкладки в этом случае)
function popup(ajaxFactory){
    return {
        restrict: 'E',
        scope: false,
        templateUrl: 'popup',
        controller: function($scope) {
            $scope.closePopup = function() {
                $scope.check = '';
                $scope.act_type='';
                /*
                if ($scope.act_type=='error'){
                    $scope.act_type=''
                }
                else {
                    $scope.init();
                }*/
            };

            $scope.input_check = function() {
                //if(entity_type=='level'||entity_type=='node'||entity_type=='alternative'||entity_type=='goal'||entity_type=='group'||entity_type=='user') {
                if ($scope.act_type != 'add' && $scope.act_type != 'edit') return true;
                if ($scope.name == '') {
                    $scope.check = 'error';
                    return false;
                }
                if ($scope.entity_type == 'level') {
                    for (var key in $scope.level_hash) {
                        if ($scope.level_hash[key].name == $scope.name && $scope.level_id != key) {
                            $scope.check = 'level_exist';
                            return false;
                        }
                    }
                }
                if ($scope.entity_type == 'alternative') {
                    for (var key in $scope.node_hash) {
                        if ($scope.node_hash[key].name == $scope.name && $scope.node_id != key) {
                            $scope.check = 'alt_exist';
                            return false;
                        }
                    }
                }
                if ($scope.entity_type == 'node') {
                    for (var key in $scope.node_hash) {
                        if ($scope.node_hash[key].name == $scope.name && $scope.node_id != key) {
                            $scope.check = 'node_exist';
                            return false;
                        }
                    }
                }
                if ($scope.entity_type == 'group') {
                    for (var key in $scope.group_hash) {
                        if ($scope.group_hash[key].name == $scope.name && $scope.group_id != key) {
                            $scope.check = 'group_exist';
                            return false;
                        }
                    }
                }
                if ($scope.entity_type == 'user') {
                    var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
                    if ($scope.email !== '') {
                        if (!re.test($scope.email)) {
                            $scope.check = 'email_error';
                            return false;
                        }
                    }
                }
                $scope.check = '';
                return true;
            }

            //разные в зависимости от типа - уровень или вершина
            $scope.postLevel = function() {
                if ($scope.input_check()) {
                    var data = {act_type: $scope.act_type, level_id: $scope.level_id, name: $scope.name, description: $scope.description, order: $scope.order};
                    $scope.postToServer($scope.entity_type, data)
                }
            };

            $scope.postNode = function() {
                if ($scope.input_check()) {
                var data = {act_type: $scope.act_type, node_id: $scope.node_id, level_id: $scope.level_id, name: $scope.name, description: $scope.description, parent: $scope.parent};
                $scope.postToServer('node', data)
                }
            };

            $scope.postGroup = function() {
                if ($scope.input_check()) {
                var data = {act_type: $scope.act_type, group_id: $scope.group_id, name: $scope.name, description: $scope.description};
                $scope.postToServer($scope.entity_type, data)
                }
            };

            $scope.postQuestion = function() {
                var data = {act_type: $scope.act_type, question_id: $scope.question_id, group_id: $scope.group_id, name: $scope.name, description: $scope.description};
                $scope.postToServer($scope.entity_type, data)
            };

            $scope.postUser = function() {
                if ($scope.input_check()) {
                var data = {act_type: $scope.act_type, user_id: $scope.user_id, group_id: $scope.group, name: $scope.name, description: $scope.description, email: $scope.email};
                $scope.postToServer($scope.entity_type, data)
                }
            };

            $scope.postEmail = function() {
                var data = {act_type: $scope.act_type, user_id: $scope.user_id, group_id: $scope.group, name: $scope.name, description: $scope.description, email: $scope.email, text:'текст наверное понадобится'};
                $scope.postToServer($scope.entity_type, data);
            };

            $scope.refresh_user = function() {
                for (var i=0;i<$scope.user_list.length;i++) {
                    if ($scope.user_list[i].id == $scope.user_id) {
                        if ($scope.act_type == 'send_email_hierarchy') {
                            $scope.user_list[i].hierarchy_form = 'email'
                        }  else {
                            $scope.user_list[i].comparison_form = 'email';
                        }
                    }
                }
                $scope.closePopup();
            }

            $scope.postToServer = function(entity_type, data) {
                if (entity_type=='email') {
                    console.log('email_success')
                }
                ajaxFactory.postRequest(entity_type, data)
                    .success(function(data, status, headers, config) {
                        if (entity_type=='email') {
                            $scope.check='success_email'
                        }
                        else {
                            $scope.init();
                        }

                    })
                    .error(function(data, status, headers, config) {
                        if (entity_type=='email') {
                            $scope.check='error_email'
                        }
                    });
            }
        }
    }
}

function hierarchygraph(){
    return {
        restrict: 'E',
        scope: false,
        templateUrl: 'hierarchy_graph',
        link: function (scope, element, attrs) {
            scope.$watchGroup(['node_hash', 'edges_list'], function(newValue, oldValue) {

                node_hash = newValue[0];
                edges_list = newValue[1];

                 var g = new dagreD3.graphlib.Graph()
                        .setGraph({})
                        .setDefaultEdgeLabel(function() { return {}; });

                for (var id in node_hash) {
                    g.setNode(id, { label: node_hash[id].name, class: "" });
                };

                g.nodes().forEach(function(v) {
                });

                for (var i=0; i<edges_list.length; i++) {
                    g.setEdge(edges_list[i].parent, edges_list[i].node);
                };

                // Create the renderer
                var render = new dagreD3.render();

                // Set up an SVG group so that we can translate the final graph.
                var svg = d3.select("svg"),
                        svgGroup = svg.append("g");

                // Run the renderer. This is what draws the final graph.
                render(d3.select("svg g"), g);

                // Center the graph
                console.log(svg.attr("width"))
                console.log(svg.attr(g.graph().width))
                var xCenterOffset = (svg.attr("width")) / 2;
                svgGroup.attr("transform", "translate(" + xCenterOffset + ", 20)");
            }, true)
        }
    }
}

function hierarchygraphgroups(){
    return {
        restrict: 'E',
        templateUrl: 'hierarchy_graph',
        link: function (scope, element, attrs) {
         scope.$watchGroup(['node_hash', 'edges_list', 'group_nodes_list', 'chosen_group'], function(newValue, oldValue) {
            node_hash  = newValue[0]
            edges_list = newValue[1]
            group_nodes_list = newValue[2]
            chosen_group = newValue[3]

        var g = new dagreD3.graphlib.Graph()
                .setGraph({})
                .setDefaultEdgeLabel(function() { return {}; });

        for (var id in node_hash) {
            if (group_nodes_list[chosen_group].indexOf(id)!=-1) {
                g.setNode(id, { label: node_hash[id].name, class: "checked" });
            }
            else {
                g.setNode(id, { label: node_hash[id].name, class: "unchecked" });
            }
        };

        g.nodes().forEach(function(v) {
        });

        for (var i=0; i<edges_list.length; i++) {
            if (group_nodes_list[chosen_group].indexOf(edges_list[i].parent)!=-1 && group_nodes_list[chosen_group].indexOf(edges_list[i].node)!=-1) {
                g.setEdge(edges_list[i].parent, edges_list[i].node, {lineInterpolate: 'basis'});
                // class??
            }
            else {
            }
        };

        // Create the renderer
        var render = new dagreD3.render();

        // Set up an SVG group so that we can translate the final graph.
        var svg = d3.select("svg"),
                svgGroup = svg.append("g");

        // Run the renderer. This is what draws the final graph.
        render(d3.select("svg g"), g);

        // Center the graph
        var xCenterOffset = (svg.attr("width") - g.graph().width) / 2;
        svgGroup.attr("transform", "translate(" + xCenterOffset + ", 20)");
        }, true)}
    }
}

function hierarchygraphgroupsvotes(){
    return {
        restrict: 'E',
        scope: false,
        templateUrl: 'hierarchy_graph',
        link: function (scope, element, attrs) {

        var g = new dagreD3.graphlib.Graph()
                .setGraph({})
                .setDefaultEdgeLabel(function() { return {}; });

        for (var id in scope.node_hash) {
            if (scope.group_nodes_for_comparison_list[scope.chosen_group].indexOf(id)!=-1) {
                g.setNode(id, { label: scope.node_hash[id].name, class: "checked" });
            }
            else {
                g.setNode(id, { label: scope.node_hash[id].name, class: "unchecked" });
            }
        };

        g.nodes().forEach(function(v) {

        });

        for (var i=0; i<scope.edges_list.length; i++) {
            if (scope.group_nodes_for_comparison_list[scope.chosen_group].indexOf(scope.edges_list[i].parent)!=-1 && scope.group_nodes_for_comparison_list[scope.chosen_group].indexOf(scope.edges_list[i].node)!=-1) {
                g.setEdge(scope.edges_list[i].parent, scope.edges_list[i].node, {lineInterpolate: 'basis'});
                // class??
            }
            else {
            }
        };

        // Create the renderer
        var render = new dagreD3.render();

        // Set up an SVG group so that we can translate the final graph.
        var svg = d3.select("svg"),
                svgGroup = svg.append("g");

        // Run the renderer. This is what draws the final graph.
        render(d3.select("svg g"), g);

        // Center the graph
        var xCenterOffset = (svg.attr("width") - g.graph().width) / 2;
        svgGroup.attr("transform", "translate(" + xCenterOffset + ", 20)");

        }
    }
}