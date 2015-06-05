/**
 * Created by Repina on 15.03.2015.
 */


function tabController( $scope, ajaxFactory ){
    $scope.tab = {};

    $scope.backToProjects = function () {
    ajaxFactory.getRequest('back_to_projects','')
        .success(function(data, status, headers, config){})
        .error(function(data, status, headers, config){});
    }

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
        $scope.email = user.email;
        $scope.user_id = user.id;
    }
}

function chooseGroupController( $scope, ajaxFactory, updateFactory ) {

    $scope.init = function() {
        $scope.group_hash = {};
        $scope.groups_votes = {}
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
        ajaxFactory.getRequest('groups_votes', '')
            .success(function (data, status, headers, config) {
                $scope.groups_votes = updateFactory.updateGroupVotes(data.group_votes);
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
                $scope.questions = [];
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
        $scope.initialisation = false;
        $scope.graphics = '';

        $scope.message = '';
        $scope.act_type = '';
        $scope.save_nodes = '';
        $scope.update();

    };

    $scope.update = function() {
    //get exist users with email send
        ajaxFactory.getRequest('common_hierarchy', '', '')
            .success(function(data, status, headers, config) {
                $scope.edges_list = [];
                $scope.node_hash = {};
                $scope.level_hash = {};
                $scope.level_nodes_list = {};
                $scope.level_order = [];

                $scope.node_hash = updateFactory.updateNodeHash(data.nodes);
                $scope.edges_list = updateFactory.updateEdgesList(data.edges);
                $scope.level_hash = updateFactory.updateLevelHash(data.levels);
                $scope.level_order = updateFactory.updateLevelOrder(data.levels);
                $scope.level_nodes_list = updateFactory.updateLevelList(data.level_nodes);
                $scope.initialisation = true;
            })
            .error(function(data, status, headers, config){});
        ajaxFactory.getRequest('group_nodes_list', '', '')
            .success(function (data, status, headers, config) {
                $scope.group_nodes_list = {};
                $scope.group_nodes_list = updateFactory.updateGroupNodesList(data.group_nodes);
            }).error(function(data, status, headers, config){});
    };

    $scope.save = function(chosen_group) {
        $scope.message = $scope.check_levels($scope.group_nodes_list[chosen_group]);
        if ($scope.message != '') {
            $scope.act_type = 'error';
            $scope.entity_type = 'error';
        }
        else {
            ajaxFactory.postRequest('chosen_group_nodes', {nodes: $scope.group_nodes_list[chosen_group], group: chosen_group})
                .success(function(data, status, headers, config) {
                    $scope.init();
                    $scope.save_nodes = 'success'
                }).error(function(data, status, headers, config){$scope.save_nodes = 'error'});
        }
    };

    $scope.check_levels = function(nodes) {
        var levels_count = {},
            alt_message = '',
            level_message = [],
            message = '';
        if (typeof(nodes)!=='undefined' && nodes.length>0) {
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
        return message
    }
}

function groupHierarchyVotesController( $scope, ajaxFactory, updateFactory ) {
    $scope.init = function() {
        $scope.act_type = '';
        $scope.message = '';
        $scope.entity_type = '';
        $scope.save_nodes_v = '';
        $scope.graphics = '';
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
                $scope.group_nodes_count_list = {};
                $scope.group_nodes_for_comparison_list = {};
                var temp = updateFactory.updateGroupNodesVotesList(data.group_nodes);
                $scope.group_nodes_count_list = temp.count;
                $scope.group_nodes_for_comparison_list = temp.type;
                $scope.save_nodes = 'success'
            }).error(function(data, status, headers, config){$scope.save_nodes = 'error'});
    };

    $scope.isForShow = function(group, node) {
        return $scope.group_nodes_list[group] && $scope.group_nodes_list[group].indexOf(node)>=0 ;
    };

    $scope.send = function(chosen_group) {
        console.log('send ')
        $scope.$parent.message = $scope.$parent.check_levels($scope.group_nodes_for_comparison_list[chosen_group]);
        console.log('message  ', $scope.message)
        if ($scope.$parent.message != '') {
            $scope.$parent.act_type = 'error';
            $scope.$parent.entity_type = 'error';
        }
        else {
            ajaxFactory.postRequest('chosen_group_nodes_for_comparison', {nodes: $scope.group_nodes_for_comparison_list[chosen_group], group: chosen_group})
                .success(function(data, status, headers, config) {
                    $scope.init();
                    $scope.save_nodes_v = 'success'
                }).error(function(data, status, headers, config){$scope.save_nodes_v = 'error'});
        }
    };

     $scope.save = function () {
        ajaxFactory.postRequest('chosen_group_nodes_for_comparison', $scope.group_nodes_for_comparison_list)
            .success(function(data, status, headers, config) {
                $scope.init();
            }).error(function(data, status, headers, config){});
    };
}

function groupsController( $scope, ajaxFactory, updateFactory  ) {
    $scope.Math = window.Math;
    $scope.init = function() {
        $scope.act_type = '';
        $scope.settab = 'question';
        $scope.users_answer_hierarchy = {};
        $scope.text = ''
        $scope.update();
    };

    $scope.tab.initGroups = function() {
        $scope.init();
    };

    $scope.update = function() {
        ajaxFactory.getRequest('groups_list', '', '')
            .success(function(data, status, headers, config) {
                $scope.group_hash = {};
                $scope.group_hash = updateFactory.updateGroupHash(data);
            }).error(function(data, status, headers, config){});
        ajaxFactory.getRequest('users_list', '', '')
                .success(function(data, status, headers, config) {
                $scope.user_hash = {};
                $scope.user_list = [];
                //$scope.user_hash = updateFactory.updateUserHash(data.users);
                $scope.user_list = updateFactory.updateUserList(data.users);
            }).error(function(data, status, headers, config){})
        ajaxFactory.getRequest('users_answer_hierarchy', '')
            .success(function(data, status, headers, config) {
                $scope.users_answer_hierarchy = updateFactory.updateUsersAnswerHierarchy(data);
                $scope.users_question = updateFactory.updateUsersAnswer(data);
            }).error(function(data, status, headers, config){});
        ajaxFactory.getRequest('users_answer_comparison', '')
            .success(function(data, status, headers, config) {
                $scope.users_answer_comparison = updateFactory.updateUsersAnswerComparison(data);
            }).error(function(data, status, headers, config){});

        ajaxFactory.getRequest('common_hierarchy', '', '')
            .success(function(data, status, headers, config) {
                //по-другому оформить
                $scope.node_hash = updateFactory.updateNodeHash(data.nodes);
                $scope.level_hash = updateFactory.updateLevelHash(data.levels);
                $scope.level_order = updateFactory.updateLevelOrder(data.levels);
                $scope.level_nodes_list = updateFactory.updateLevelList(data.level_nodes);
                //$scope.adjacency_list = updateFactory.updateAdjacencyList(data.edges);
                $scope.edges_list = updateFactory.updateEdgesList(data.edges);
            })
            .error(function(data, status, headers, config){})
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
        //$scope.text = 'Здравствуйте, '+user.name+'!. Вы приглашены для участия в голосовании по проблеме '+$scope.node_hash[$scope.level_nodes_list[$scope.level_order[0]][0]].name+'. По ссылке Вы можете перейти к первому этапу голосования. Через несколько дней Вам придет письмо с приглашением к участию во втором этапе голосования.'
        $scope.text = 'Здравствуйте, '+user.name+'! Нас интересует Ваше мнение по проблеме "'+$scope.node_hash[$scope.level_nodes_list[$scope.level_order[0]][0]].name+'". Если Вы хотите принять участие в решении данной проблемы, то пройдите анкету по ссылке в течение 2-3 дней. Затем Вам будет выслана анкета для второго этапа голосования. Спасибо за Ваше участие. Если Вы не хотите учавствовать, то просто проигнорируйте это письмо.'
    };

    $scope.sendEmailComparison = function(user, group_id) {
        $scope.entity_type = 'email';
        $scope.act_type = 'send_email_comparison';
        $scope.name = user.name;
        $scope.description = user.description;
        $scope.email = user.email;
        $scope.user_id = user.id;
        $scope.group = group_id;
        $scope.text = 'Здравствуйе, '+user.name+'! Это второй этап голосования по проблеме "'+$scope.node_hash[$scope.level_nodes_list[$scope.level_order[0]][0]].name+'". По ссылке Вы можете перейти ко второму этапу голосования. Спасибо за участие.'
    };

    $scope.showUserAnswerHierarchy = function(user) {
        $scope.act_type = 'answer';
        $scope.entity_type = 'answer_hierarchy';
        $scope.user_id = user.id;
    };

    $scope.showUserAnswerComparison = function(user) {
        $scope.act_type = 'answer';
        $scope.entity_type = 'answer_comparison';
        $scope.user_id = user.id;
    }
}

function hierarchyController( $scope, ajaxFactory, updateFactory ) {

    //разбить на функции
    $scope.init = function() {
        $scope.act_type = '';
        $scope.graphics = '';
        $scope.update();
    };

    $scope.tab.initHierarchy = function() {
        $scope.init()
    };

    $scope.update = function() {
        ajaxFactory.getRequest('common_hierarchy', '', '')
            .success(function(data, status, headers, config) {
                //по-другому оформить
                $scope.node_hash = {};
                $scope.level_hash = {};
                $scope.level_nodes_list = {}; //уровни с вершинами  level_nodes_list['1'] = [n1]
                $scope.level_order = []; //порядок уровней =
                $scope.edges_list = [];
                $scope.node_hash = updateFactory.updateNodeHash(data.nodes);
                $scope.level_hash = updateFactory.updateLevelHash(data.levels);
                $scope.level_order = updateFactory.updateLevelOrder(data.levels);
                $scope.level_nodes_list = updateFactory.updateLevelList(data.level_nodes);
                //$scope.adjacency_list = updateFactory.updateAdjacencyList(data.edges);
                $scope.edges_list = updateFactory.updateEdgesList(data.edges);
                $scope.type = $scope.level_hash[$scope.level_order[1]].type
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
    $scope.paramForNodePopup = function(entity_type, act_type, name, description, level_id, node_id, parent)  {
        $scope.act_type = act_type;
        $scope.entity_type = entity_type;
        $scope.name = name;
        $scope.description = description;
        $scope.level_id = level_id;
        $scope.node_id = node_id;
        $scope.parent = parent;
    };


    $scope.editGoal = function(node_id, level_id) {
        $scope.paramForNodePopup('goal', 'edit', $scope.node_hash[node_id].name, $scope.node_hash[node_id].description, level_id, node_id,'');
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
        entity_type = $scope.level_hash[level_id].name == 'alternatives' ? 'alternative' : 'node'
        $scope.paramForNodePopup(entity_type,'add', '', '', level_id, '', parent);
    };

    $scope.editNode = function(level_id, node_id, parent) {
        entity_type = $scope.level_hash[level_id].name == 'alternatives' ? 'alternative' : 'node'
        $scope.paramForNodePopup(entity_type, 'edit', $scope.node_hash[node_id].name, $scope.node_hash[node_id].description, level_id, node_id, parent);
    };

    $scope.deletNode = function(level_id, node_id, parent) {
        entity_type = $scope.level_hash[level_id].name == 'alternatives' ? 'alternative' : 'node'
        $scope.paramForNodePopup(entity_type, 'delet', $scope.node_hash[node_id].name, $scope.node_hash[node_id].description, level_id, node_id, parent);
    };

    $scope.editType = function(level_id) {
        $scope.paramForNodePopup('alt_type', 'edit_type', '', '', level_id, '', '')
    }

}

function globalPriorityController( $scope, ajaxFactory, updateFactory ) {

    $scope.tab.initGlobalPriority = function() {
        $scope.init()
    };

    $scope.Math = window.Math;

    $scope.init = function() {
        $scope.act_type = '';
        $scope.checked_group_list = [];
        $scope.all = false
        $scope.result = {};
        $scope.all_result = {};
        $scope.type = '';
        $scope.show_priority = false;
        $scope.calculated = false;
        $scope.update();
    };

    $scope.initResult = function() {

        for (var i=0;i<$scope.level_nodes_list[$scope.level_order[1]].length;i++) {
            $scope.result[$scope.level_nodes_list[$scope.level_order[1]][i]]=0;
        }
    };

    $scope.changePriority = function() {
        group_hash[checked_group_list[0]].priority = 100
    };

    $scope.slider = {
        'options': {
            start: function (event, ui) { },
            stop: function (event, ui) { }
            }
    };

    $scope.change = function(group_key) {
        var sum = 0,
            sum_dif = 0,
            zero = false;
        for (var i=0;i<$scope.checked_group_list.length;i++){
            sum = Math.round((sum+$scope.group_hash[$scope.checked_group_list[i]].priority)*10)/10
        }
        sum_dif = Math.round(((100-sum)/($scope.checked_group_list.length-1))*10)/10
        for (var i=0;i<$scope.checked_group_list.length;i++){
            if ($scope.group_hash[$scope.checked_group_list[i]].priority>=100&&$scope.checked_group_list[i]==group_key) {
                max_id = $scope.checked_group_list[i];
                for (var i=0;i<$scope.checked_group_list.length;i++){
                    if ($scope.checked_group_list[i]==max_id) continue;
                    $scope.group_hash[$scope.checked_group_list[i]].priority = 0;
                }
                continue;
            }
            if ($scope.checked_group_list[i]==group_key) continue;
            if ($scope.group_hash[$scope.checked_group_list[i]].priority+sum_dif>0) {
                $scope.group_hash[$scope.checked_group_list[i]].priority = Math.round(($scope.group_hash[$scope.checked_group_list[i]].priority+sum_dif)*10)/10
            } else {
                $scope.group_hash[$scope.checked_group_list[i]].priority = 0;
            }
        }
    }

    $scope.update = function() {
        ajaxFactory.getRequest('groups_list', '', '')
            .success(function(data, status, headers, config) {
                $scope.group_hash = {};
                $scope.group_hash = updateFactory.updateGroupPriority(data);
            }).error(function(data, status, headers, config){});
        ajaxFactory.getRequest('user_confidence_list', '', '')
            .success(function(data, status, headers, config) {
                $scope.user_confidence_list = [];
                $scope.checked_user_list = [];
                $scope.user_confidence_list = updateFactory.updateUserConfidenceList(data.users).info;
                $scope.checked_user_list = updateFactory.updateUserConfidenceList(data.users).list;
            }).error(function(data, status, headers, config){})
        ajaxFactory.getRequest('common_hierarchy', '', '')
            .success(function(data, status, headers, config) {
                $scope.node_hash = {};
                $scope.level_nodes_list = {};
                $scope.level_order = [];
                $scope.level_hash = {};
                $scope.group_priority = {};

                $scope.node_priority = updateFactory.updateNodePriority(data.nodes);
                $scope.node_hash = updateFactory.updateNodeHash(data.nodes);
                $scope.level_hash = updateFactory.updateLevelHash(data.levels);
                $scope.level_order = updateFactory.updateLevelOrder(data.levels);
                $scope.level_nodes_list = updateFactory.updateLevelList(data.level_nodes);
                $scope.type = $scope.level_hash[$scope.level_order[1]].type;
                $scope.alt_edges = updateFactory.updateAltEdgesList(data.edges, $scope.level_order[1]);
                $scope.initResult();
            })
            .error(function(data, status, headers, config){});
    };

    $scope.calculate = function() {
        var group_list = [];
        for (var i=0;i<$scope.checked_group_list.length;i++){
            var priority = ($scope.show_priority && $scope.checked_group_list.length>1) ? $scope.group_hash[$scope.checked_group_list[i]].priority : 100/$scope.checked_group_list.length;
            group_list.push({'id': $scope.checked_group_list[i], 'priority': priority})
        };

        ajaxFactory.postRequest('global_priority', {groups: group_list, users: $scope.checked_user_list})
            .success(function(data, status, headers, config) {
                    $scope.node_priority = data.result;
                    $scope.calculated = true;
            }).error(function(data, status, headers, config){});
    };

    $scope.user_settings = function(group_key) {
        $scope.chosen_group = group_key;
        $scope.act_type = 'user_list';
        $scope.entity_type = 'user_list';
    };

    $scope.saveAbsoluteValue = function() {
        ajaxFactory.postRequest('save_absolute_value', {alt_edges: $scope.alt_edges})
            .success(function(data, status, headers, config){})
            .error(function(data, status, headers, config){});
    }

}