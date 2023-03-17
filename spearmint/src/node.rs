pub struct Node<'a> {
    pub branch: String,
    pub commit: String,
    pub parent: Option<&'a Node<'a>>,
    pub children: Vec<&'a Node<'a>>,
    pub is_owned: bool,
    pub commit_prefix: String,
    pub commit_suffix: String,
}

impl<'a> Node <'a> {
    pub fn new (
        branch: String,
        commit: String,
        parent: Option<&'a Node>,
        children: Vec<&'a Node>,
        is_owned: bool,
        commit_prefix: String,
        commit_suffix: String) -> Self {
            Node { branch, commit, parent, children, is_owned, commit_prefix, commit_suffix }
        }
}
