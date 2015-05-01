/**
 * Created by Repina on 15.03.2015.
 */

(function() {
    angular
        .module('app',['components', 'checklist-model'])
        .factory('ajaxFactory', ajaxFactory)
        .factory('updateFactory', updateFactory)
        .controller('treeController', treeController)
        .controller('hierarchyController', hierarchyController)
        .controller('groupsController', groupsController)
        .controller('chooseGroupController', chooseGroupController)
        .controller('groupQuestionController', groupQuestionController)
        .controller('groupHierarchyController', groupHierarchyController)
        .controller('usersController', usersController)
        .controller('groupHierarchyVotesController', groupHierarchyVotesController)
        .controller('tabController', tabController)
        .controller('dontknowController', dontknowController)
        .directive ('popup', popup)
})();