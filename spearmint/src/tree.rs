use std::{collections::HashMap};

use crate::branches;
use crate::node;

pub struct Tree {
    pub tree: HashMap<&'static str, node::Node>
}

impl Tree {
    pub fn new(tree: HashMap<&'static str, node::Node>) -> Self {
        Tree { tree }
    }

    pub fn get() -> Self {
        let branchNames = branches::get_all_branches();
        let mut tree: HashMap<&'static str, node::Node> = HashMap::new();
        let (branchesToParents, parentsToBranches, uniqueHashes) = Self::generate_parents_and_branches(branchNames);
        // Regenerate branch names as _generateParentsAndBranches may have
        // created new branches::
        let branchNames = branches::get_all_branches();
        for branch in branchNames {
            let commit = branches::get_commit_for_branch(branch);
            let parent = branchesToParents.get(&branch).unwrap().clone();
            let children = parentsToBranches.get(&branch).unwrap().clone();
            let is_owned = branches::is_branch_owned(branch);
            tree.insert(branch, node::Node::new(&branch, &commit, parent, children, is_owned,
                                &uniqueHashes.get(&commit).unwrap().0, &uniqueHashes.get(&commit).unwrap().1));
        }
        return Tree::new(tree);
    }

    fn generate_parents_and_branches(branchNames: Vec<&'static str>) -> (HashMap<&'static str, Option<&'static str>>, HashMap<&'static str, Vec<&'static str>>, HashMap<&'static str, (&'static str, &'static str)>) {
    /*
        Generates mappings to be used to generate the tree object.
        This is split into a few distinct stages.
            1.) Create bi directional mappings between commits and branches.
                Also create a list of unowned commits in date order.
                There is a check at this stage to ensure that no two 
                branches point to the same commit.
            
            2.) Iterate through the branches and map each branch's commit 
                to its parent and its children. These mappings are stored in 
                commitsToParents and parentsToCommits respectively.
                This stage also realises phantom nodes. Nodes whose parents 
                are not pointed to by a branch have "phantom" parents. They 
                exist but not in Gum's commit tree. Branches are created for 
                each of these phantom parents in this stage.
            
            3.) If an unowned commit has a commit date before the head 
                branch, the names of the branches are swapped. The new head 
                branch will be the oldest unowned commit in the repository.

            4.) Branchify the mappings: the two dictionaries containing the 
                commit mappings are copied but each commit reference is 
                replaced with a branch name.
    */
    (HashMap::new(), HashMap::new(), HashMap::new())
    }
}
