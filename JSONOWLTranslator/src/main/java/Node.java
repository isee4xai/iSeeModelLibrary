import java.util.ArrayList;
import java.util.Hashtable;

/*
 * Class where we are going to represent a node for a BehaviourTree.
 * 
 * @author Marta Caro-Martinez
 * */


public class Node {
	
	private String id;
	private NodeType type;
	
	// This attribute only makes sense when the nodeType is ExplanationMethodNode. 
	// Then instance will have the value of the explainer name.
	private String instance; 
	
	//private String title;
	private String description;
	private Hashtable properties;
	private ArrayList<String> children; 
	
	public Node() {
		this.id = "";
		this.type = null;
		this.instance = "";
		//this.title = "";
		this.description = "";
		this.properties = new Hashtable();
		this.children = new ArrayList<String>();
	}

	// Getters and setters

	public String getId() {
		return id;
	}

	public void setId(String id) {
		this.id = id;
	}

	public NodeType getType() {
		return type;
	}

	public void setType(NodeType type) {
		this.type = type;
	}
	
	public String getInstance() {
		return instance;
	}

	public void setInstance(String instance) {
		this.instance = instance;
	}

	/*public String getTitle() {
		return title;
	}

	public void setTitle(String title) {
		this.title = title;
	}*/

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public Hashtable getProperties() {
		return properties;
	}

	public void setProperties(Hashtable properties) {
		this.properties = properties;
	}

	public ArrayList<String> getChildren() {
		return children;
	}

	public void setChildren(ArrayList<String> children) {
		this.children = children;
	}

	@Override
	public String toString() {
		String result = "Node [id=" + id + ", type=" + type + ", instance=" + instance + ", description=" + description
				+ ", properties=" + properties + ", children= "; // + children + "]";
		
		for(int i = 0; i < this.children.size(); i++) {
			result += this.children.get(i) + ",";
		}
		
		return result;
	
	
	}
	
	
	
}
