/**
 * Created by Repina on 15.03.2015.
 */

(function() {
    angular
        .module('app',['components', 'checklist-model','ui.slider'])
        .factory('ajaxFactory', ajaxFactory)
        .factory('updateFactory', updateFactory)
        .controller('hierarchyController', hierarchyController)
        .controller('groupsController', groupsController)
        .controller('chooseGroupController', chooseGroupController)
        .controller('groupQuestionController', groupQuestionController)
        .controller('groupHierarchyController', groupHierarchyController)
        .controller('usersController', usersController)
        .controller('groupHierarchyVotesController', groupHierarchyVotesController)
        .controller('tabController', tabController)
        .controller('globalPriorityController', globalPriorityController)
        .directive ('popup', popup)
        .directive ('hierarchygraph', hierarchygraph)
        .directive ('hierarchygraphgroups', hierarchygraphgroups)
        .directive ('hierarchygraphgroupsvotes', hierarchygraphgroupsvotes)
})();