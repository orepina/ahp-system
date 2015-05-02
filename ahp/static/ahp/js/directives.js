/**
 * Created by Repina on 15.03.2015.
 */
//project id должно быть в url
//наследует $scope контроллера (вкладки в этом случае)
function popup(ajaxFactory){
    return {
        restrict: 'E',
        scope: false,
        templateUrl: 'popup.html',
        controller: function($scope) {
            $scope.closePopup = function() {
                if ($scope.act_type=='error'){
                    $scope.act_type=''
                }
                else {
                    $scope.init();
                }
            };

            //разные в зависимости от типа - уровень или вершина
            $scope.postLevel = function() {
                var data = {act_type: $scope.act_type, level_id: $scope.level_id, name: $scope.name, description: $scope.description, order: $scope.order};
                $scope.postToServer($scope.entity_type, data)
            };

            $scope.postNode = function() {
                var data = {act_type: $scope.act_type, node_id: $scope.node_id, level_id: $scope.level_id, name: $scope.name, description: $scope.description, parent: $scope.parent};
                $scope.postToServer($scope.entity_type, data)
            };

            $scope.postGroup = function() {
                var data = {act_type: $scope.act_type, group_id: $scope.group_id, name: $scope.name, description: $scope.description};
                $scope.postToServer($scope.entity_type, data)
            };

            $scope.postQuestion = function() {
                var data = {act_type: $scope.act_type, question_id: $scope.question_id, group_id: $scope.group_id, name: $scope.name, description: $scope.description};
                $scope.postToServer($scope.entity_type, data)
            };

            $scope.postUser = function() {
                var data = {act_type: $scope.act_type, user_id: $scope.user_id, group_id: $scope.group, name: $scope.name, description: $scope.description, email: $scope.email};
                $scope.postToServer($scope.entity_type, data)
            };

            $scope.postEmail = function() {
                var data = {act_type: $scope.act_type, user_id: $scope.user_id, group_id: $scope.group, name: $scope.name, description: $scope.description, email: $scope.email, text:'текст наверное понадобится'};
                $scope.postToServer($scope.entity_type, data);
                //на отправку сообщения анимация
            };

            $scope.postToServer = function(entity_type, data) {
                ajaxFactory.postRequest(entity_type, data)
                    .success(function(data, status, headers, config) {
                        $scope.init();
                    }).error(function(data, status, headers, config){});
            }

        }
    }
}