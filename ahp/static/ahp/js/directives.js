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
                if ($scope.act_type=='error'){
                    $scope.act_type=''
                }
                else {
                    $scope.init();
                }
            };

            $scope.input_check = function() {
                //if(entity_type=='level'||entity_type=='node'||entity_type=='alternative'||entity_type=='goal'||entity_type=='group'||entity_type=='user') {
                if ($scope.name == '') {
                    $scope.check = 'error';
                    return false;
                }
                if ($scope.entity_type == 'level') {
                    for (var key in $scope.level_hash) {
                        if ($scope.level_hash[key].name == $scope.name) {
                            $scope.check = 'level_exist';
                            return false;
                        }
                    }
                }
                if ($scope.entity_type == 'alternative') {
                    for (var key in $scope.node_hash) {
                        if ($scope.node_hash[key].name == $scope.name) {
                            $scope.check = 'alt_exist';
                            return false;
                        }
                    }
                }
                if ($scope.entity_type == 'node') {
                    for (var key in $scope.node_hash) {
                        if ($scope.node_hash[key].name == $scope.name) {
                            $scope.check = 'node_exist';
                            return false;
                        }
                    }
                }
                if ($scope.entity_type == 'group') {
                    for (var key in $scope.group_hash) {
                        if ($scope.group_hash[key].name == $scope.name) {
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
                //на отправку сообщения анимация
            };

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