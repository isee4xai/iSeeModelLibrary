import org.semanticweb.owlapi.model.OWLOntologyCreationException;
import org.semanticweb.owlapi.model.OWLOntologyStorageException;

/*
 * This class executes the program
 * 
 * @author Marta Caro-Martinez
 * */

public class Main {

	public static void main(String[] args) {
		JSONReader reader = new JSONReader("RandomTreeSimple.json");
		
		BehaviourTree BT = reader.getBT();
		
		System.out.println(BT.toString());
		
		// these examples are working
		//OWLInstance owlInstance = new OWLInstance("pizza.func.owl", BT);
		
		OWLInstance owlInstance = new OWLInstance("iSeeOnto.owl", BT);
		
		
		try {
			owlInstance.addNewInstanceFromBT();
		} catch (OWLOntologyCreationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (OWLOntologyStorageException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

}
