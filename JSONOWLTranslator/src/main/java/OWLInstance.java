import java.io.File;
import java.util.ArrayList;

import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLClassAssertionAxiom;
import org.semanticweb.owlapi.model.OWLDataFactory;
import org.semanticweb.owlapi.model.OWLDocumentFormat;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyCreationException;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.model.OWLOntologyStorageException;
import org.semanticweb.owlapi.model.PrefixManager;
import org.semanticweb.owlapi.util.DefaultPrefixManager;

/*
 * This class loads the iSeeOnto ontology and create a new instance for this ontology from a behaviour tree
 * 
 * @author Marta Caro-Martinez
 * */
public class OWLInstance {
	
	// file path where our ontology is
	private File iSeeOnto;
	
	// BT we want to translate
	private BehaviourTree behaviourTree;
	
	// URL that identifies our ontology
	private String base;
	
	
	public OWLInstance(String ontologyPath, BehaviourTree bt) {
		this.iSeeOnto = new File(ontologyPath);
		this.behaviourTree = bt;
		this.base = "https://www.w3id.org/iSeeOnto/BehaviourTree#";
		//this.base = "http://www.co-ode.org/ontologies/pizza/pizza.owl#";
	}
	
	// function to create an assertion --> including an instance for a class
	private void addAssertion(ArrayList<OWLClassAssertionAxiom> assertList, OWLDataFactory dataFactory, PrefixManager pm, String className, String instanceName){
		
		OWLClassAssertionAxiom classAssertion = null;
		
		// getting the class where we want to include the instance
		OWLClass my_class = dataFactory.getOWLClass(":" + className, pm);
		
		// creating the new instance for our class
		OWLNamedIndividual my_instance = dataFactory.getOWLNamedIndividual(":" + instanceName, pm);
		
		// including the new instance as an instance of the class
		// fst parameter: class where including the instance (second parameter)
		classAssertion = dataFactory.getOWLClassAssertionAxiom(my_class, my_instance);
		
		assertList.add(classAssertion);

	}
	
	
	// TODO: CREATE THE RELATIONSHIP BETWEEN EXPLANATION EXPERIENCE AND THE BT
	// function to create the axioms for BT, trees and nodes instances we have in our Behaviour Tree
	private ArrayList<OWLClassAssertionAxiom> createMyAssertion(OWLDataFactory dataFactory, PrefixManager pm) {
		ArrayList<OWLClassAssertionAxiom> myAssertions = new ArrayList<OWLClassAssertionAxiom>();
		
		// BT instance
		addAssertion(myAssertions, dataFactory, pm, "BehaviourTree", this.behaviourTree.getTitle());
		
		
		// doing the same we have done with BT, but for all the trees		
		int btTreeListSize = this.behaviourTree.getTrees().size();
		for(int i = 0; i < btTreeListSize; i++) {
			Tree currentTree = this.behaviourTree.getTrees().get(i);
			
			addAssertion(myAssertions, dataFactory, pm, "Tree", currentTree.getId());
			
			int treeNodesListSize = currentTree.getNodes().size();
			for(int j = 0; j < treeNodesListSize; j++) {
				Node currentNode = currentTree.getNodes().get(j);
				
				// doing the same for all the nodes
				addAssertion(myAssertions, dataFactory, pm, "Node", currentNode.getId());
			}
			
		}
	
		
		return myAssertions;
	}
	
	/*private ArrayList<OWLClassAssertionAxiom> assertPizza(OWLDataFactory dataFactory, PrefixManager pm) {
		ArrayList<OWLClassAssertionAxiom> myAssertions = new ArrayList<OWLClassAssertionAxiom>();
		OWLClassAssertionAxiom classAssertion = null;
		
		// getting the class where we want to include the instance
		OWLClass bt_class = dataFactory.getOWLClass(":Vegetarian", pm);
		
		// creating the new instance for our BT
		OWLNamedIndividual bt_instance = dataFactory.getOWLNamedIndividual(":Maria", pm);
		
		// including the new instance as an instance of the class
		// fst parameter: class where including the instance (second parameter)
		classAssertion = dataFactory.getOWLClassAssertionAxiom(bt_class, bt_instance);
		
		myAssertions.add(classAssertion);
		
		return myAssertions;
	}*/
	
	// Create the instances and add them to the ontology
	private OWLOntology createNewInstance(OWLOntologyManager m, OWLOntology o) {
		// manager to create the data
		OWLDataFactory dataFactory = m.getOWLDataFactory();
		PrefixManager prefixManager = new DefaultPrefixManager(null, null, this.base);
		
		// create all the assertions
		ArrayList<OWLClassAssertionAxiom> classAssertion = createMyAssertion(dataFactory, prefixManager);
		
		// checking with pizza
		//ArrayList<OWLClassAssertionAxiom> classAssertion = assertPizza(dataFactory, prefixManager);
		
		for(int i = 0; i < classAssertion.size(); i++) {
			// include the new assertions into the ontology
			m.addAxiom(o, classAssertion.get(i));
		}
		
		
		return o;
	}
	
	// execute the creation of an instance in the ontology from the BT
	public void addNewInstanceFromBT() throws OWLOntologyCreationException, OWLOntologyStorageException{
		
		// Obtain a copy of a manager to manage a set of ontologies
		OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
		
		// loading an ontology (iSeeOnto in this case) from a file
		OWLOntology ontology = manager.loadOntologyFromOntologyDocument(this.iSeeOnto);
		
		// Getting all the classes of the ontology
		for (OWLClass cls : ontology.getClassesInSignature()) {
	        System.out.println(cls);
	    }
		
		createNewInstance(manager, ontology);
		
		// writing the result in a new file
		IRI destination = IRI.create(new File("updated-iSeeOnto.owl"));
        //manager.saveOntology(ontology, new OWLXMLDocumentFormat(), destination);
		
		OWLDocumentFormat format = manager.getOntologyFormat(ontology);   
		manager.saveOntology(ontology, format, destination);
	}
}
