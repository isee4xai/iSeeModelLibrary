package com.isee4xai.backend.iseeonto;

import static org.semanticweb.owlapi.search.EntitySearcher.getAnnotationObjects;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Iterator;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.OWLAnnotation;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyCreationException;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.reasoner.NodeSet;
import org.semanticweb.owlapi.reasoner.OWLReasoner;
import org.semanticweb.owlapi.reasoner.OWLReasonerFactory;
import org.semanticweb.owlapi.reasoner.structural.StructuralReasonerFactory;

/**
 * Hello world!
 *
 */
public class Onto2Json 
{
	private static final String CLASS = "class";
	private static final String INSTANCES2 = "instances";
	private static final String SUBCLASSES = "subclasses";
	private static final String NOTHING = "Nothing";
	OWLOntology ontology;
	
	public static void main( String[] args ) throws FileNotFoundException
    {
		Onto2Json parser = new Onto2Json();
		parser.run();
    }
    
    
    
	private void run() {
    	OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
    	//OWLDataFactory df = OWLManager.getOWLDataFactory();

    	OWLReasonerFactory reasonerFactory = new StructuralReasonerFactory();
    	
		
		JSONObject jo = new JSONObject();
		JSONArray ret = new JSONArray();
		try {
			jo.put("iSeeOnto",ret);
		} catch (JSONException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
		try {
			ontology = manager.loadOntologyFromOntologyDocument(new File("iSeeOnto.owl"));
			OWLClass top = manager.getOWLDataFactory().getOWLThing();
			JSONObject clase = new JSONObject();
			//clase.put(anno.getProperty().getIRI().getShortForm(), ((IRI) anno.getValue()).getShortForm());
			//System.out.println(anno.getProperty().getIRI().getShortForm() + ": " + ((IRI) anno.getValue()).getShortForm());
			writeToJSON( top,  ontology,  reasonerFactory, clase);
			ret.put(clase);
			

				File f = new File("iSeeOnto.json");
		    	FileWriter file = null;
				f.createNewFile();
				file = new FileWriter("iSeeOnto.json", false);
				file.write(jo.toString(2));
				file.flush();
				file.close();

			
		} catch (OWLOntologyCreationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} 
    	
		
	}



	@SuppressWarnings("deprecation")
	void writeToJSON(OWLClass cls, OWLOntology ontology, OWLReasonerFactory reasonerFactory,JSONObject clase) throws JSONException
    {
		//clase.put("class", cls.getIRI().getShortForm());
		clase.put(CLASS, labelFor(cls));
		OWLReasoner reasoner = reasonerFactory.createNonBufferingReasoner(ontology);
        NodeSet<OWLNamedIndividual> instances = reasoner.getInstances(cls, true);
        
        if(!instances.isEmpty())
        {
        	Iterator<OWLNamedIndividual> it = instances.entities().iterator();
            JSONArray instArray = new JSONArray();
            while(it.hasNext())
            {
            	instArray.put(it.next().getIRI().getShortForm());
            }
            clase.put(INSTANCES2, instArray);
           
            	
        }
    
        
       
    	JSONArray subArray = new JSONArray();
    	for (OWLClass child : reasoner.getSubClasses(cls, true).getFlattened()) 
            if (!child.equals(cls) && !labelFor(child).equals(NOTHING)) {
	        	JSONObject sub = new JSONObject();
	        	writeToJSON(child, ontology, reasonerFactory, sub);
	        	subArray.put(sub);
    	}
        if(!subArray.isEmpty())
        	clase.put(SUBCLASSES,subArray);        	
   
          
    }
    
    
    
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
