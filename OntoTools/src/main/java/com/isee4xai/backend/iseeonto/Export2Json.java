package com.isee4xai.backend.iseeonto;

import static org.semanticweb.owlapi.search.EntitySearcher.getAnnotationObjects;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Iterator;
import java.util.List;
import java.util.Set;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLAnnotation;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLClassExpression;
import org.semanticweb.owlapi.model.OWLDataFactory;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLObjectProperty;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyCreationException;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.reasoner.NodeSet;
import org.semanticweb.owlapi.reasoner.OWLReasoner;
import org.semanticweb.owlapi.reasoner.OWLReasonerFactory;
import org.semanticweb.owlapi.reasoner.structural.StructuralReasonerFactory;
import org.semanticweb.owlapi.search.EntitySearcher;
import org.semanticweb.owlapi.util.OWLAPIStreamUtils;


public class Export2Json
{
    public static void main( String[] args ) throws FileNotFoundException
    {
	    Export2Json parser = new Export2Json();
	    parser.run();
    }
   
OWLOntology ontology;
OWLDataFactory df;
OWLReasoner reasoner;
JSONObject jo = new JSONObject();
JSONArray ret = new JSONArray();

@SuppressWarnings("deprecation")
private void run() {

	OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
	df = OWLManager.getOWLDataFactory();
    OWLReasonerFactory reasonerFactory = new StructuralReasonerFactory();
    OWLClass cls = df.getOWLClass(IRI.create(
     "http://www.w3id.org/iSeeOnto/explanationexperience#ExplanationExperience"));
	try {
		jo.put("explanation",ret);
	} catch (JSONException e1) {
		// TODO Auto-generated catch block
		e1.printStackTrace();
	}
	try {
		ontology = manager.loadOntologyFromOntologyDocument(new File("iSeeOnto.owl"));
		reasoner = reasonerFactory.createReasoner(ontology);
		/*Get the instances of ExplanationExperience*/
		NodeSet<OWLNamedIndividual> individuals = reasoner.getInstances(cls, true);
		if(!individuals.isEmpty()){
			for (OWLNamedIndividual ins : individuals.getFlattened()) {
				JSONObject propertyObject = new JSONObject();
				String individual =ins.getIRI().getShortForm();
				propertyObject.put("instance", individual); //Export the instance of ExplanationExperience class
				propertyObject.put("classes", labelFor(cls));//Export the class of ExplanationExperience 
				/*Create .json files for each ExplationExperience instance*/
				File f = new File(individual+".json");
				FileWriter file = null;
				f.createNewFile();
				file = new FileWriter(individual+".json");
				exportToJSON( ins, ontology, propertyObject);
				//  ret.put(propertyObject);
				file.write(propertyObject.toString(2));
				file.flush();
				file.close();
			}
		}
		} catch (OWLOntologyCreationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}				
}

@SuppressWarnings({ "deprecation", "unlikely-arg-type" })
void exportToJSON(OWLNamedIndividual ins, OWLOntology ontology, JSONObject propertyObject) throws JSONException, IOException
{
	JSONArray propertyArray = new JSONArray();
	for (OWLObjectProperty obj : ontology.getObjectPropertiesInSignature()) {
		NodeSet<OWLNamedIndividual> objVal = reasoner.getObjectPropertyValues(ins, obj);
		Set<OWLNamedIndividual> propValues = objVal.getFlattened();
		for (Iterator<OWLNamedIndividual> objIterator = objVal.entities().iterator(); objIterator.hasNext();) {
			OWLNamedIndividual obInd=objIterator.next();
			JSONObject objProperty = new JSONObject();
		   /*Get the Object property 'obj' of the instance 'ins'*/
			objProperty.put("name",obj.getIRI().getShortForm());
			objProperty.put("instance",obInd.getIRI().getShortForm());
			
			/*Export the class name*/
			classFor(ins,objProperty);
		
			/*Add all the properties to the array*/
			propertyArray.put(objProperty);
			for (int k = 0; k < propertyArray.length(); k++) {
		    	propertyObject.put("property", propertyArray); //Put the array into the JSON file
			}
			
			exportToJSON(obInd, ontology, objProperty);
		}
	}
	classFor(ins,propertyObject);
  } 

/*Export the class/es of the property (annotation and object) values and its annotations - */
private String classFor(OWLNamedIndividual insta, JSONObject propertyObj){
	 List<OWLClassExpression> listCls = OWLAPIStreamUtils.asList(EntitySearcher.getTypes(insta,ontology));
//	 List<String> classList = new ArrayList<>();
	 JSONArray classArray = new JSONArray();
	 for (Iterator<OWLClassExpression> clsIterator = listCls.iterator(); clsIterator.hasNext();) {
//		  OWLClassExpression obInd = clsIterator.next();
//		  propertyObj.put("classes", obInd.asOWLClass().getIRI().getFragment());
		  OWLClass instaClass = (OWLClass) clsIterator.next();
		  /*Export the list of classes associated with the instance*/
		  JSONObject classes = new JSONObject();
		  classArray.put(labelFor(instaClass));	  
		  for (int j = 0; j < classArray.length(); j++) {
			  propertyObj.put("classes", classArray);
		  }
     }
	return null;
	
} 

/*Export the label of the class*/
private String labelFor(OWLClass clazz) {
       /*
        * Use a visitor to extract label annotations
        */
       LabelExtractor le = new LabelExtractor();
       for (Object anno : getAnnotationObjects(clazz, ontology).toArray()) {
           ((OWLAnnotation)anno).accept(le);
       }
       /* Print out the label if there is one. If not, just use the class URI */
       if (le.getResult() != null) {
           return le.getResult();
       } else {
       String iri = clazz.getIRI().toString();
           return iri.substring(iri.indexOf("#")+1);
           
       }
   }  

}
