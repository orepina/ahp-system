/**
 * Created by Repina on 15.03.2015.
 */

function ajaxFactory( $http ) {
    //запрос на общее дерево (первая вкладка, сделать 18.03) ( вершины + группы? + пусть ока только вершины)
    //вообще формируем общее дерево(только цели+критерии+альтернативы!!!), след вкладка группы + пользователи(или потом), след вкладка  дерео для групп, а теперь пользователи. ура, а потом группы+ пользователи + альтернативы + количество=> подвкладки у одной большо вкладки ?
    //добавить дообавление в базу, удаление, обноление в модели
    //список групп, дальше вершины по группам
    //TODO определить urls константами
    return {
        //при get все параметры в url, на сервере по url разберемся
        postRequest : function( entity_type, data ) {
            return $http ({
                    method: 'POST',
                    url: 'http://127.0.0.1:8000/ahp/' + entity_type +'/',// +act_type ,   //'http://127.0.0.1:8000/ahp/'
                    data: data
                })
        },

        getRequest : function( method, parameters ) {
            return $http ({
                    method: 'GET',
                    url: 'http://127.0.0.1:8000/ahp/' + method + parameters +'/'
                })
        }
    }
}

function updateFactory() {
    return {

        //разобраться с кучей одинаковых методов

        updateNodeHash: function(data) {
            var temp = JSON.parse(data).concat(),
                node_hash = {};
            for (var i=0; i<temp.length; i++){
                node_hash[temp[i].pk] = {name: temp[i].fields.name, description: temp[i].fields.description};
            }
            return node_hash;
        },

        updateLevelHash: function(data) {
            var temp = JSON.parse(data).concat(),
                level_hash = {};
            for (var i=0; i<temp.length; i++){
                level_hash[temp[i].pk] = {name: temp[i].fields.name, description: temp[i].fields.description};
            }
            return level_hash;
        },

        updateLevelOrder: function(data) {
            var temp = JSON.parse(data).concat(),
                order,
                level_order = [];
            for (var i=0; i<temp.length; i++){
                order = temp[i].fields.order.toString();
                level_order[order] = temp[i].pk;
            }
            return level_order;
        },

        updateLevelList: function(data) {
            var temp = JSON.parse(data).concat(),
                level_nodes_list = {};
            for (var i=0; i<temp.length; i++){
                level_nodes_list[temp[i].fields.level] = level_nodes_list[temp[i].fields.level] || [];
                level_nodes_list[temp[i].fields.level].push(temp[i].fields.node);
            }
            return level_nodes_list;
        },

        updateAdjacencyList: function(data) {
            var temp = JSON.parse(data).concat(),
                adjacency_list = {};
            for (var i=0; i<temp.length; i++){
                adjacency_list[temp[i].fields.parent] = adjacency_list[temp[i].fields.parent] || [];
                adjacency_list[temp[i].fields.parent].push(temp[i].fields.node);
            }
            return adjacency_list
        },

        updateGroupHash: function(data) {
            var temp = JSON.parse(data.groups).concat(),
                temp_count = data.groups_count,
                group_hash = {};
            for (var i=0; i<temp.length; i++){
                group_hash[temp[i].pk] = {name: temp[i].fields.name, description: temp[i].fields.description, count: temp_count[temp[i].pk]};
            }
            return group_hash;
        },

        updateUserHash : function(data) {
            var temp = JSON.parse(data).concat(),
                user_hash = {};
            for (var i=0; i<temp.length; i++){
                user_hash[temp[i].pk] = {name: temp[i].fields.name, description: temp[i].fields.description, group: temp[i].fields.group, email: temp[i].fields.email, hierarchy_form: temp[i].fields.hierarchy_form, comparison_form: temp[i].fields.comparison_form};
            }
            return user_hash;
        },

        updateUserList : function(data) {
            var temp = JSON.parse(data).concat(),
                user_list = [];
            for (var i=0; i<temp.length; i++){
                user_list.push({id: temp[i].pk, name: temp[i].fields.name, description: temp[i].fields.description, group: temp[i].fields.group, email: temp[i].fields.email, hierarchy_form: temp[i].fields.hierarchy_form, comparison_form: temp[i].fields.comparison_form});
            }
            return user_list;
        },

        updateGroupNodesList: function(data) {
            var temp = JSON.parse(data).concat(),
                group_nodes_list = {};
            for (var i=0; i<temp.length; i++){
                group_nodes_list[temp[i].fields.group] = group_nodes_list[temp[i].fields.group] || [];
                group_nodes_list[temp[i].fields.group].push(temp[i].fields.node);
            }
            return group_nodes_list;
        },

        updateGroupNodesVotesList: function(data) {
            var temp = JSON.parse(data).concat(),
                group_nodes_count_list = {},
                group_nodes_for_comparison_list =  {};
            for (var i=0; i<temp.length; i++){
                group_nodes_count_list[temp[i].fields.group] = group_nodes_count_list[temp[i].fields.group] || {};
                group_nodes_count_list[temp[i].fields.group][temp[i].fields.node] = {count: temp[i].fields.count, type: temp[i].fields.type};
                group_nodes_for_comparison_list[temp[i].fields.group] = group_nodes_for_comparison_list[temp[i].fields.group] || [];
                if (temp[i].fields.type=='for comparison form') { group_nodes_for_comparison_list[temp[i].fields.group].push(temp[i].fields.node) };
            }
            return {count: group_nodes_count_list, type: group_nodes_for_comparison_list};
        },

        updateGroupQuestionList: function(data) {
            var temp = JSON.parse(data).concat(),
                group_question_list = {},
                question_hash = {};
            for (var i=0; i<temp.length; i++){
                question_hash[temp[i].pk] = {name: temp[i].fields.name, description: temp[i].fields.description};
                group_question_list[temp[i].fields.group] = group_question_list[temp[i].fields.group] || [];
                group_question_list[temp[i].fields.group].push(temp[i].pk);
            }
            return {list: group_question_list, hash: question_hash};

        },

        updateQuestionList: function(data) {
            var temp = JSON.parse(data).concat(),
                id_r = 0,
                questions = [];
            for (var i=0; i<temp.length; i++){
                id_r = Math.floor(Math.random() * (1000 - 0 + 1)) + 0;
                questions.push({id: temp[i].fields.name+temp[i].fields.group+id_r, name: temp[i].fields.name, description: temp[i].fields.description, group: temp[i].fields.group});
               // question_hash[temp[i].pk] = {name: temp[i].fields.name, description: temp[i].fields.description, group: temp[i].fields.group};
            }
            return questions;
        }
    }
}

