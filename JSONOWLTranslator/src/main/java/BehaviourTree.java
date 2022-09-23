import java.util.ArrayList;

/*
 * Class where we are going to represent a BehaviourTree
 * 
 * @author Marta Caro-Martinez
 * */

public class BehaviourTree {
	private String id;
	private String title;
	private String description;
	private String version;
	private String scope;
	
	// The name of the explanation experience for which this BT is a solution. 
	// This value is not on the JSON file but we can get it by adding the title + “ExplanationExperience”. 
	// It is important to have it to include the solution in the proper explanation experience.
	private String explanationExperience;
	private ArrayList<Tree> trees;

	
	public BehaviourTree() {
		this.id = "";
		this.title = "";
		this.description = "";
		this.version = "";
		this.scope = "";
		this.explanationExperience = "";
		this.trees = new ArrayList<Tree>();
	}

	// Getters and setters

	public String getId() {
		return id;
	}


	public void setId(String id) {
		this.id = id;
	}


	public String getTitle() {
		return title;
	}


	public void setTitle(String title) {
		this.title = title;
	}


	public String getDescription() {
		return description;
	}


	public void setDescription(String description) {
		this.description = description;
	}


	public String getVersion() {
		return version;
	}


	public void setVersion(String version) {
		this.version = version;
	}


	public String getScope() {
		return scope;
	}


	public void setScope(String scope) {
		this.scope = scope;
	}


	public String getExplanationExperience() {
		return explanationExperience;
	}


	public void setExplanationExperience(String explanationExperience) {
		this.explanationExperience = explanationExperience;
	}


	public ArrayList<Tree> getTrees() {
		return trees;
	}


	public void setTrees(ArrayList<Tree> trees) {
		this.trees = trees;
	}

	@Override
	public String toString() {
		String result = "BehaviourTree [id=" + id + ", title=" + title + ", description=" + description + ", version=" + version
				+ ", scope=" + scope + ", explanationExperience=" + explanationExperience + ", trees= ";
		
		for(int i = 0; i < this.trees.size(); i++) {
			result += "tree " + i + " " + this.trees.get(i).toString() + "\n";
		}
		
		result += "]";
		return result;
	}
	
	
	
}
