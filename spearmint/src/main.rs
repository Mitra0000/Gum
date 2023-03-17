mod node;

fn main() {
    let test = node::Node::new(String::from("test"), String::from("12345"), None, Vec::new(), true, String::from("foo"), String::from("bar"));
    println!("{}", test.branch);
}
