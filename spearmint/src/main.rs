mod branches;
mod node;
mod tree;

fn main() {
    let test = node::Node::new("test", "12345", None, Vec::new(), true, "foo", "bar");
    println!("{}", test.branch);
    let my_tree = tree::Tree::get();
    println!("{:?}", my_tree.tree);
}
