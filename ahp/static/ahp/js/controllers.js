/**
 * Created by Repina on 15.03.2015.
 */
//урлы на сервер сформировать по другому, может отдавать не по одной сущности,а объединять внутри страницы


function tabController( $scope ){
    $scope.tab = {}
}

function treeController( $scope, ajaxFactory ){
    $scope.adjacency_list = []; //структура дерева adjacency_list[n1] = [n2,n3]//удобнее для сервера матрицей смежности, хотя и ак норм, просто цикл на сервере
    $scope.hash = {}; //описание всех объектов hash['n1'] = {name: '', description: '', users: [], groups: []}//может user и group вынести в отдельный массив+ инфо о сущностях раделить по хешам
    $scope.hash_node = {};
    $scope.hash_group = {};
    $scope.hash_user = {};
    $scope.hash_level = {};
    $scope.level_nodes_list = {}; //уровни с вершинами  level_nodes_list['l1'] = [n1]
    $scope.group_list = {}; //список групп со списком пользователей group_list['students'] = [u1,u2,u3]
    //какие новые структуры?
    //где инициализируем
    //как мы будем отпарвлять дерево? целиком измененное или по частям

    $scope.adjacency_list[1] = [2,3];
    $scope.hash_node [1] = {name: 'node_1', description: 'node_1wotowt'};
    $scope.hash_node [2] = {name: 'node_2', description: 'node_2222wotowt'};
    $scope.hash_node [3] = {name: 'node_3', description: 'node_333333wotowt'};
    $scope.testdatarequest = { adjacency_list:$scope.adjacency_list, hash_node: $scope.hash_node };

    $scope.senddata = function() {
        req = ajaxFactory.postRequest($scope.testdatarequest);
        /*    req.success(function(data, status, headers, config) {
           var r = JSON.parse(data)[1];
            for( var key in r ){
                console.log(key)
                console.log(r[key])
            }
            console.log(r.fields.parent)
        })
        */

    }

    //функция для генерации дерева по уровням
    //проходим по массиву с левелами, проверяем вершины
    // как понять что вершины еще на уровень ниже, но на этом уровне ? смотрим есть ли у нее родители на это уровне ( постоянно бегать по уровню - плохо, но куда деваться)

}

function usersController( $scope, ajaxFactory, updateFactory ) {
    $scope.init = function() {
        $scope.act_type = '';
        $scope.user_hash = {};
        $scope.user_list = [];
        $scope.update();
    };

    $scope.update = function() {
        ajaxFactory.getRequest('users_list', '', '')
            .success(function(data, status, headers, config) {
                $scope.user_hash = updateFactory.updateUserHash(data.users);
                $scope.user_list = updateFactory.updateUserList(data.users);
            }).error(function(data, status, headers, config){})
    };

    $scope.paramForUserPopup = function(act_type, user_id, name, description, email){
        $scope.act_type = act_type;
        $scope.entity_type = 'user';
        $scope.name = name;
        $scope.description = description;
        $scope.email = email;
        $scope.user_id = user_id;
    };

    $scope.addUser = function() {
        $scope.paramForUserPopup('add', '', '', '','');
    };

    $scope.editUser = function(user) {
        $scope.paramForUserPopup('edit', user.id, user.name, user.description, user.email);
    };

    $scope.deletUser = function(user) {
        $scope.paramForUserPopup('delet', user.id, '', '', '');
    };

    $scope.sendEmail = function(user) {
        $scope.entity_type = 'email';
        $scope.act_type = 'send_email';
        $scope.name = user.name;
        $scope.description = user.description;
        $scope.email =user.email;
        $scope.user_id = user.id;
    }
}

function chooseGroupController( $scope, ajaxFactory, updateFactory ) {

    $scope.init = function() {
        $scope.group_hash = {};
        $scope.update();
    };

    $scope.update = function() {
        ajaxFactory.getRequest('groups_list', '', '')
            .success(function (data, status, headers, config) {
                $scope.group_hash = updateFactory.updateGroupHash(data);
                if ( !$scope.chosen_group ){
                    for (var key in $scope.group_hash) {
                        $scope.chosen_group = key;
                        break;
                    }
                }
            })
            .error(function (data, status, headers, config) {});
    };

    $scope.chooseGroupNodes = function(group) {
        $scope.chosen_group = group;
    };
}

function groupQuestionController( $scope, ajaxFactory, updateFactory ) {

    $scope.init = function() {
        $scope.act_type = "";
       // $scope.group_question_list = {};//уровни с вершинами  groupQuestion['1'] = [n1]
        $scope.questions = [];
        $scope.edit = false;
        $scope.add = false;
        $scope.question_name = '';
        $scope.repeat_index = -1;
        $scope.settab = 'question';
        $scope.update();
    };

    $scope.update = function() {
        ajaxFactory.getRequest('group_question_list', '', '')
            .success(function (data, status, headers, config) {
               // $scope.group_question_list = updateFactory.updateGroupQuestionList(data.group_questions).list;
                $scope.questions = updateFactory.updateQuestionList(data.group_questions);
            })
            .error(function(data, status, headers, config){});
    };

    $scope.paramForQuestionPopup = function(act_type, name, description, question_id, group_id) {
        $scope.act_type = act_type;
        $scope.entity_type = 'question';
        $scope.name = name;
        $scope.description = description;
        $scope.question_id = question_id;
        $scope.group_id = group_id;
    };

    $scope.addGroupQuestion = function(group_id) {
        $scope.paramForQuestionPopup('add', '', '', '', group_id);
    };

    $scope.deletGroupQuestion = function(group_id, question_id) {
        $scope.paramForQuestionPopup('delet', question_id, question_id, question_id, group_id);
    };

    $scope.deletQuestion = function(question_id) {
        var index = $scope.questions.map(function(q){return q.id}).indexOf(question_id);
        $scope.questions.splice(index,1);
    };

    $scope.editQuestion = function(index) {
        $scope.repeat_index = index;
        //ну все таки проверку на повторения надо же сделать!
    };

    $scope.ifEdit = function(index) {
        return $scope.repeat_index == index;
    };

    $scope.newQuestion = function() {
        $scope.add = true;
    };

    $scope.addQuestion = function(group_id) {
        var id_r = Math.floor(Math.random() * (1000 - 0 + 1)) + 0;
        $scope.questions.push({id: $scope.question_name+group_id+id_r, name: $scope.question_name, description: '', group: group_id});
        $scope.add = false;
        $scope.question_name = '';
        $scope.repeat_index = -1;
        console.log($scope.questions);
        //ну все таки проверку на повторения надо же сделать!! тут особенно
    };

    $scope.cancelQuestion = function () {
        $scope.add = false;
        $scope.question_name = '';
        $scope.repeat_index = -1;
    };

    $scope.save = function() {
        console.log($scope.questions);
        ajaxFactory.postRequest('questions', $scope.questions)
            //пока что отправлять будем все кучей, но может  отправлять например при каждом нажатии
            .success(function(data, status, headers, config) {
                $scope.init();
            }).error(function(data, status, headers, config){});
    };
}

function groupHierarchyController( $scope, ajaxFactory, updateFactory ) {

    $scope.tabInit = function() {
        $scope.init();
        $scope.$parent.init();
    };

    $scope.init = function() {
        $scope.group_nodes_list = {};
        $scope.adjacency_list = {};
        $scope.node_hash = {};
        $scope.level_hash = {};
        $scope.level_nodes_list = {};
        $scope.level_order = [];
        $scope.message = '';
        $scope.act_type = '';
        $scope.update();
    };

    $scope.update = function() {
        ajaxFactory.getRequest('common_hierarchy', '', '')
            .success(function(data, status, headers, config) {
                $scope.node_hash = updateFactory.updateNodeHash(data.nodes);
                $scope.level_hash = updateFactory.updateLevelHash(data.levels);
                $scope.level_order = updateFactory.updateLevelOrder(data.levels);
                $scope.level_nodes_list = updateFactory.updateLevelList(data.level_nodes);
                $scope.adjacency_list = updateFactory.updateAdjacencyList(data.edges);
            })
            .error(function(data, status, headers, config){});
        ajaxFactory.getRequest('group_nodes_list', '', '')
            .success(function (data, status, headers, config) {
                $scope.group_nodes_list = updateFactory.updateGroupNodesList(data.group_nodes);
            }).error(function(data, status, headers, config){});
    };

    $scope.save = function(chosen_group) {
        $scope.message = $scope.check_levels($scope.group_nodes_list[chosen_group]);
        if ($scope.message != ''){
            $scope.act_type = 'error';
            $scope.entity_type = 'error';
        }
        else {
            ajaxFactory.postRequest('chosen_group_nodes', {nodes: $scope.group_nodes_list[chosen_group], group: chosen_group})
                .success(function(data, status, headers, config) {
                    $scope.init();
                }).error(function(data, status, headers, config){});
        }

    };

    $scope.check_levels = function(nodes) {
        var levels_count = {},
            alt_message = '',
            level_message = [],
            message = '';
        if (nodes.length>0) {
            for (var level in $scope.level_nodes_list) {
                if ($scope.level_hash[level].name == 'goal') continue;
                levels_count[level] = 0;
                for (var i=0; i<nodes.length; i++) {
                    if ($scope.level_nodes_list[level].indexOf(nodes[i]) !== -1) {
                        levels_count[level]++;
                    }
                }
                if (levels_count[level]<2) {
                    if ($scope.level_hash[level].name == 'alternatives') {
                        alt_message = (levels_count[level]==0) ? 'Вы не выбрали ни одной альтернативы' : 'Вы выбрали только одну альтернативу'
                    }
                    else {
                        level_message.push($scope.level_hash[level].name );
                    }
                }
            }
            if (level_message.length > 0 ) {
                message = (level_message.length > 1 ) ? 'Вы выбрали недостаточно критериев на уровнях '+level_message.join(', ') : 'Вы выбрали недостаточно критериев на уровне '+level_message[0]
            }
            message = message+alt_message;
        }
        else {
            message = 'Вы не выбрали ни одного критерия и ни одной альтернативы'
        }
        return message;
    }


}

function groupHierarchyVotesController( $scope, ajaxFactory, updateFactory ) {
    $scope.init = function() {
        $scope.act_type = '';
        $scope.group_nodes_count_list = {};
        $scope.group_nodes_for_comparison_list = {};
        $scope.message = '';
        $scope.act_type = '';
        $scope.entity_type = '';
        $scope.update();
    };

    $scope.tabInit = function() {
        $scope.init();
        $scope.$parent.tabInit();
    };

    $scope.tab.initGroupHierarchyVotes = function() {
        $scope.tabInit()
    };

    $scope.update = function() {

        ajaxFactory.getRequest('group_nodes_list', '', '')
            .success(function (data, status, headers, config) {
                var temp = updateFactory.updateGroupNodesVotesList(data.group_nodes);
                $scope.group_nodes_count_list = temp.count;
                $scope.group_nodes_for_comparison_list = temp.type;
                console.log('groupHierarchyVotesController: group_nodes_list   ', temp)
            }).error(function(data, status, headers, config){});
    };

    $scope.isForShow = function(group, node) {
        return $scope.group_nodes_list[group] && $scope.group_nodes_list[group].indexOf(node)>=0 ;
    };

    $scope.save = function () {
        ajaxFactory.postRequest('chosen_group_nodes_for_comparison', $scope.group_nodes_for_comparison_list)
            .success(function(data, status, headers, config) {
                $scope.init();
            }).error(function(data, status, headers, config){});
    };

    $scope.send = function (chosen_group) {
        $scope.message = $scope.$parent.check_levels($scope.group_nodes_for_comparison_list[chosen_group]);
        if ($scope.message != ''){
            $scope.act_type = 'error';
            $scope.entity_type = 'error';
        }
        else {
            ajaxFactory.postRequest('chosen_group_nodes_for_comparison', {nodes: $scope.group_nodes_for_comparison_list[chosen_group], group: chosen_group})
                //пока что отправлять будем все кучей, но может  отправлять например при каждом нажатии
                .success(function(data, status, headers, config) {
                    console.log($scope.group_nodes_for_comparison_list);
                    // init, но не всего!
                    $scope.init();
                }).error(function(data, status, headers, config){});
        }
    };
    //сохраняет только чекбоксы, остальное в других местах. поэтому нужно избавиться от кнопки
}

function groupsController( $scope, ajaxFactory, updateFactory  ) {
    $scope.init = function() {
        $scope.act_type = '';
        $scope.group_hash = {};
        $scope.settab = 'question';
        $scope.user_hash = {};
        $scope.user_list = [];
        $scope.update();
    };

    $scope.tab.initGroups = function() {
        $scope.init();
    };

    $scope.update = function() {
        ajaxFactory.getRequest('groups_list', '', '')
            .success(function(data, status, headers, config) {
                $scope.group_hash = updateFactory.updateGroupHash(data);
            }).error(function(data, status, headers, config){});
        ajaxFactory.getRequest('users_list', '', '')
            .success(function(data, status, headers, config) {
                //$scope.user_hash = updateFactory.updateUserHash(data.users);
                $scope.user_list = updateFactory.updateUserList(data.users);
            }).error(function(data, status, headers, config){})
    };

    $scope.paramForGroupPopup = function(act_type, name, description, group_id){
        $scope.act_type = act_type;
        $scope.entity_type = 'group';
        $scope.name = name;
        $scope.description = description;
        $scope.group_id = group_id;
    };

    $scope.addGroup = function() {
        $scope.paramForGroupPopup('add', '', '', '');
    };

    $scope.editGroup = function(group_id) {
        $scope.paramForGroupPopup('edit', $scope.group_hash[group_id].name, $scope.group_hash[group_id].description, group_id);
    };

    $scope.deletGroup = function(group_id) {
        $scope.paramForGroupPopup('delet', $scope.group_hash[group_id].name, $scope.group_hash[group_id].description, group_id);
    };

    $scope.settingsGroup = function(group_id) {
        $scope.act_type = 'settings';
        $scope.entity_type = 'setting';
        $scope.group_id = group_id;
        //вызов попапа с настройками
        //попап запихать в отдельную директиву?

    };

    $scope.paramForUserPopup = function(act_type, user_id, name, description, email, group){
        $scope.act_type = act_type;
        $scope.entity_type = 'user';
        $scope.name = name;
        $scope.description = description;
        $scope.email = email;
        $scope.group = group;
        $scope.user_id = user_id;
    };

    $scope.addUser = function(group_id) {
        $scope.paramForUserPopup('add', '', '', '', '', group_id);
    };

    $scope.editUser = function(user, group_id) {
        //$scope.chooseGroupNodes($scope.user_hash[user_id].group);
        $scope.paramForUserPopup('edit', user.id, user.name, user.description, user.email, group_id);
    };

    $scope.deletUser = function(user, group_id) {
        $scope.paramForUserPopup('delet', user.id, '', '', '', group_id);
    };

    $scope.sendEmailHierarchy = function(user, group_id) {
        $scope.entity_type = 'email';
        $scope.act_type = 'send_email_hierarchy';
        $scope.name = user.name;
        $scope.description = user.description;
        $scope.email = user.email;
        $scope.user_id = user.id;
        $scope.group = group_id;
    };

    $scope.sendEmailComparison = function(user, group_id) {
        $scope.entity_type = 'email';
        $scope.act_type = 'send_email_comparison';
        $scope.name = user.name;
        $scope.description = user.description;
        $scope.email = user.email;
        $scope.user_id = user.id;
        $scope.group = group_id;
        //send_comparison_form

    }
}

function hierarchyController( $scope, ajaxFactory, updateFactory ) {
    //разбить на функции
    $scope.init = function() {
        $scope.act_type = '';
        $scope.adjacency_list = {};
        $scope.node_hash = {};
        $scope.level_hash = {};
        $scope.level_nodes_list = {}; //уровни с вершинами  level_nodes_list['1'] = [n1]
        $scope.level_order = []; //порядок уровней =
        $scope.update();
    };

    $scope.tab.initHierarchy = function() {
        $scope.init()
    };

    $scope.update = function() {
        ajaxFactory.getRequest('common_hierarchy', '', '')
            .success(function(data, status, headers, config) {
                //по-другому оформить
                $scope.node_hash = updateFactory.updateNodeHash(data.nodes);
                $scope.level_hash = updateFactory.updateLevelHash(data.levels);
                $scope.level_order = updateFactory.updateLevelOrder(data.levels);
                $scope.level_nodes_list = updateFactory.updateLevelList(data.level_nodes);
                $scope.adjacency_list = updateFactory.updateAdjacencyList(data.edges);
            })
            .error(function(data, status, headers, config){})
    };

    $scope.paramForLevelPopup = function(act_type, name, description, level_id, order)  {
        $scope.act_type = act_type;
        $scope.entity_type = 'level';
        $scope.name = name;
        $scope.description = description;
        $scope.level_id = level_id;
        $scope.order = order;
    };

    //переписать присваивание в цикле
    $scope.paramForNodePopup = function(act_type, name, description, level_id, node_id, parent)  {
        $scope.act_type = act_type;
        $scope.entity_type = 'node';
        $scope.name = name;
        $scope.description = description;
        $scope.level_id = level_id;
        $scope.node_id = node_id;
        $scope.parent = parent;
    };


    $scope.editGoal = function(node_id, level_id) {
        $scope.paramForNodePopup('edit', $scope.node_hash[node_id].name, $scope.node_hash[node_id].description, level_id, node_id,'');
    };

    //организовать присваивания вызовом отдельной функции
    $scope.addLevel = function() {
        $scope.paramForLevelPopup('add', '', '', '', Object.keys($scope.level_hash).length);
    };

    $scope.editLevel = function(level_id) {
        $scope.paramForLevelPopup('edit', $scope.level_hash[level_id].name, $scope.level_hash[level_id].description, level_id, '');
    };

    $scope.deletLevel = function(level_id) {
        $scope.paramForLevelPopup('delet', $scope.level_hash[level_id].name, $scope.level_hash[level_id].description, level_id, $scope.level_order.indexOf(level_id));
    };

    $scope.addNode = function(level_id, parent) {
        $scope.paramForNodePopup('add', '', '', level_id, '', parent);
    };

    $scope.editNode = function(level_id, node_id, parent) {
        $scope.paramForNodePopup('edit', $scope.node_hash[node_id].name, $scope.node_hash[node_id].description, level_id, node_id, parent);
    };

    $scope.deletNode = function(level_id, node_id, parent) {
        $scope.paramForNodePopup('delet', $scope.node_hash[node_id].name, $scope.node_hash[node_id].description, level_id, node_id, parent);
    };

    $scope.test = function() {
        console.log('lalala')
    }

}

function globalPriorityController( $scope, ajaxFactory, updateFactory ) {

    $scope.init = function() {
        $scope.act_type = '';
        $scope.group_hash = {};
        $scope.user_list = [];
        $scope.checked_group_list = [];
        $scope.all = false
        $scope.node_hash = {};
        $scope.level_nodes_list = {};
        $scope.level_order = [];
        $scope.result = {};
        $scope.group_priority = {};
        $scope.update();

    };

    $scope.selectAll = function() {
        $scope.checked_group_list = []
        for (group in $scope.group_hash){
            $scope.checked_group_list.push(group)
        }
        console.log($scope.checked_group_list)
    };

    $scope.update = function() {
        ajaxFactory.getRequest('groups_list', '', '')
            .success(function(data, status, headers, config) {
                $scope.group_hash = updateFactory.updateGroupHash(data);
            }).error(function(data, status, headers, config){});
        ajaxFactory.getRequest('users_list', '', '')
            .success(function(data, status, headers, config) {
                $scope.user_list = updateFactory.updateUserList(data.users);
            }).error(function(data, status, headers, config){})
        ajaxFactory.getRequest('common_hierarchy', '', '')
            .success(function(data, status, headers, config) {
                $scope.node_hash = updateFactory.updateNodeHash(data.nodes);
                //$scope.level_hash = updateFactory.updateLevelHash(data.levels);
                $scope.level_order = updateFactory.updateLevelOrder(data.levels);
                $scope.level_nodes_list = updateFactory.updateLevelList(data.level_nodes);
            })
            .error(function(data, status, headers, config){});
    };

    $scope.calculate = function() {
    ajaxFactory.postRequest('global_priority', $scope.checked_group_list)
            .success(function(data, status, headers, config) {
                    $scope.result = data.result
            }).error(function(data, status, headers, config){});
    }


}