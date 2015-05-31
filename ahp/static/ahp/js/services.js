/**
 * Created by Repina on 15.03.2015.
 */

function ajaxFactory( $http ) {
    return {
        postRequest : function( entity_type, data, project ) {
            return $http ({
                    method: 'POST',
                    url: entity_type +'/',// +project
                    data: data
                })
        },

        getRequest : function( method, parameters, project ) {
            return $http ({
                    method: 'GET',
                    url: method + parameters +'/',// +project
                })
        }
    }
}

function updateFactory() {
    return {

        updateNodeHash: function(data) {
            var temp = JSON.parse(data),
                node_hash = {};
            for (var i=0; i<temp.length; i++){
                node_hash[temp[i].pk] = {name: temp[i].fields.name, description: temp[i].fields.description};
            }
            return node_hash;
        },

        updateNodePriority: function(data) {
            var temp = JSON.parse(data),
                node_priority = {};
            for (var i=0; i<temp.length; i++){
                node_priority[temp[i].pk] = 0;
            }
            return node_priority;
        },

        updateLevelHash: function(data) {
            var temp = JSON.parse(data),
                level_hash = {};
            for (var i=0; i<temp.length; i++){
                level_hash[temp[i].pk] = {name: temp[i].fields.name, description: temp[i].fields.description, type: temp[i].fields.type};
            }
            return level_hash;
        },

        updateLevelOrder: function(data) {
            var temp = JSON.parse(data),
                order,
                level_order = [];
            for (var i=0; i<temp.length; i++){
                order = temp[i].fields.order.toString();
                level_order[order] = temp[i].pk;
            }
            return level_order;
        },

        updateLevelList: function(data) {
            var temp = JSON.parse(data),
                level_nodes_list = {};
            for (var i=0; i<temp.length; i++){
                level_nodes_list[temp[i].fields.level] = level_nodes_list[temp[i].fields.level] || [];
                level_nodes_list[temp[i].fields.level].push(temp[i].fields.node);
            }
            return level_nodes_list;
        },

        updateAdjacencyList: function(data) {
            var temp = JSON.parse(data),
                adjacency_list = {};
            for (var i=0; i<temp.length; i++){
                adjacency_list[temp[i].fields.parent] = adjacency_list[temp[i].fields.parent] || [];
                adjacency_list[temp[i].fields.parent].push(temp[i].fields.node);
            }
            return adjacency_list
        },

        updateEdgesList: function(data) {
            var temp = JSON.parse(data),
                edges_list = [];
            for (var i=0; i<temp.length; i++){
                if (temp[i].fields.parent==null) continue;
                edges_list.push({parent: temp[i].fields.parent, node: temp[i].fields.node})
            }
            return edges_list
        },

        updateAltEdgesList: function(data, alt_id) {
            var temp = JSON.parse(data),
                alt_edges_list = {};
            for (var i=0; i<temp.length; i++){
                if (temp[i].fields.level==alt_id) {
                    alt_edges_list[temp[i].fields.parent] = alt_edges_list[temp[i].fields.parent] || [];
                    alt_edges_list[temp[i].fields.parent].push({alt: temp[i].fields.node, value: 0});
                }
            }
            return alt_edges_list
        },

        updateUsersAnswerHierarchy: function(data) {
            var temp = JSON.parse(data.user_nodes),
                user_nodes = {};
            for (var i=0; i<temp.length; i++){
                user_nodes[temp[i].fields.user] = user_nodes[temp[i].fields.user] || [];
                user_nodes[temp[i].fields.user].push(temp[i].fields.node);
            }
            return user_nodes
        },

        updateUsersAnswer: function(data) {
        },

        updateUsersAnswerComparison: function(data) {
            return data.user_comparison
        },

        updateGroupHash: function(data) {
            var temp = JSON.parse(data.groups),
                temp_count = data.groups_count,
                group_hash = {};
            for (var i=0; i<temp.length; i++){
                group_hash[temp[i].pk] = {name: temp[i].fields.name, description: temp[i].fields.description, count: temp_count[temp[i].pk]};
            }
            return group_hash;
        },

        updateGroupPriority: function(data) {
            var temp = JSON.parse(data.groups),
                temp_count = data.groups_count,
                group_priority = {};
            for (var i=0; i<temp.length; i++){
                group_priority[temp[i].pk] = {name: temp[i].fields.name, description: temp[i].fields.description, count: temp_count[temp[i].pk], priority: 0};
            }
            return group_priority;
        },

        updateGroupVotes: function(data) {
            var temp = data,
                group_votes = {};
            console.log(temp)
            for (var i=0; i<temp.length; i++){
                group_votes[temp[i].group] = {hierarchy_email: temp[i].hierarchy_email, comparison_email: temp[i].comparison_email};
            }
            return group_votes;
        },

        updateUserHash : function(data) {
            var temp = JSON.parse(data),
                user_hash = {};
            for (var i=0; i<temp.length; i++){
                user_hash[temp[i].pk] = {name: temp[i].fields.name, description: temp[i].fields.description, group: temp[i].fields.group, email: temp[i].fields.email, hierarchy_form: temp[i].fields.hierarchy_form, comparison_form: temp[i].fields.comparison_form};
            }
            return user_hash;
        },

        updateUserList : function(data) {
            var temp = JSON.parse(data),
                user_list = [];
            for (var i=0; i<temp.length; i++){
                user_list.push({id: temp[i].pk, name: temp[i].fields.name, description: temp[i].fields.description, group: temp[i].fields.group, email: temp[i].fields.email, hierarchy_form: temp[i].fields.hierarchy_form, comparison_form: temp[i].fields.comparison_form});
            }
            return user_list;
        },

        updateUserConfidenceList : function(data) {
            var temp = JSON.parse(data),
                user_list = [],
                user_checked_list = [];
            for (var i=0; i<temp.length; i++){
                user_list.push({id: temp[i].pk, name: temp[i].fields.name, description: temp[i].fields.description, group: temp[i].fields.group, email: temp[i].fields.email, hierarchy_form: temp[i].fields.hierarchy_form, comparison_form: temp[i].fields.comparison_form, avt_count: temp[i].fields.confidence1, confidence: temp[i].fields.confidence2});
                if (temp[i].fields.comparison_form=='check') {
                    user_checked_list.push(temp[i].pk);
                }
            }
            return {info: user_list, list: user_checked_list};
        },

        updateGroupNodesList: function(data) {
            var temp = JSON.parse(data),
                group_nodes_list = {};
            for (var i=0; i<temp.length; i++){
                group_nodes_list[temp[i].fields.group] = group_nodes_list[temp[i].fields.group] || [];
                group_nodes_list[temp[i].fields.group].push(temp[i].fields.node);
            }
            return group_nodes_list;
        },

        updateGroupNodesVotesList: function(data) {
            var temp = JSON.parse(data),
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
            var temp = JSON.parse(data),
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
            var temp = JSON.parse(data),
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

