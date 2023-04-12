#[derive(Hash, PartialEq, Eq, Debug)]
pub struct Node {
    pub branch: &'static str,
    pub commit: &'static str,
    pub parent: Option<&'static str>,
    pub children: Vec<&'static str>,
    pub is_owned: bool,
    pub commit_prefix: &'static str,
    pub commit_suffix: &'static str,
}

impl Node {
    pub fn new (
        branch: &'static str,
        commit: &'static str,
        parent: Option<&'static str>,
        children: Vec<&'static str>,
        is_owned: bool,
        commit_prefix: &'static str,
        commit_suffix: &'static str) -> Self {
            Node { branch, commit, parent, children, is_owned, commit_prefix, commit_suffix }
        }
}
