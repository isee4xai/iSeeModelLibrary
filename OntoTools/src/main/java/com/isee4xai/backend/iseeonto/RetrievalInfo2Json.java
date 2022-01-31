package com.isee4xai.backend.iseeonto;

import static org.semanticweb.owlapi.search.EntitySearcher.getAnnotationObjects;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Iterator;
import java.util.stream.Stream;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLAnnotation;
import org.semanticweb.owlapi.model.OWLAnnotationProperty;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLClassExpression;
import org.semanticweb.owlapi.model.OWLDataFactory;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyCreationException;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.reasoner.NodeSet;
import org.semanticweb.owlapi.reasoner.OWLReasoner;
import org.semanticweb.owlapi.reasoner.OWLReasonerFactory;
import org.semanticweb.owlapi.reasoner.structural.StructuralReasonerFactory;
import org.semanticweb.owlapi.search.EntitySearcher;

/**
 * Hello world!
 *
 */
public class RetrievalInfo2Json 
{
    public static void main( String[] args ) throws FileNotFoundException
    {
    	RetrievalInfo2Json parser = new RetrievalInfo2Json();
    	parser.run();
    	
    }
    
	OWLOntology ontology;
    
    
	private void run() {
    	OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
    	OWLDataFactory df = OWLManager.getOWLDataFactory();
    	OWLReasonerFactory reasonerFactory = new StructuralReasonerFactory();
    	
		
		JSONObject jo = new JSONObject();
		JSONArray ret = new JSONArray();
		try {
			jo.put("retrievalInfo",ret);
		} catch (JSONException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
		try {
			ontology = manager.loadOntologyFromOntologyDocument(new File("iSeeOnto.owl"));
			OWLAnnotationProperty simAnno = df.getOWLAnnotationProperty("http://www.w3id.org/iSeeOnto/SimilarityKnowledge#applicableSimilarityStrategy");
			for (Iterator<OWLClass> iterator = ontology.classesInSignature().iterator(); iterator.hasNext();) {
				OWLClass cls = iterator.next();
				Stream<OWLAnnotation> stream = EntitySearcher.getAnnotationObjects(cls, ontology);
				Iterator<OWLAnnotation> it = stream.iterator();
				while(it.hasNext())
				{
					OWLAnnotation anno = it.next();
					if(anno.getProperty().equals(simAnno))
					{
						if(!anno.getValue().toString().equalsIgnoreCase("_:genid2147485010"))
						{
							JSONObject clase = new JSONObject();
							clase.put(anno.getProperty().getIRI().getShortForm(), ((IRI) anno.getValue()).getShortForm());
							//System.out.println(anno.getProperty().getIRI().getShortForm() + ": " + ((IRI) anno.getValue()).getShortForm());
							writeToJSON( cls,  ontology,  reasonerFactory, clase);
							ret.put(clase);
	                     
					
						}
					
						
					}
						
					
				}
			}

				File f = new File("RetrievalInfo.json");
		    	FileWriter file = null;
				f.createNewFile();
				file = new FileWriter("RetrievalInfo.json", false);
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



	void writeToJSON(OWLClass cls, OWLOntology ontology, OWLReasonerFactory reasonerFactory,JSONObject clase) throws JSONException
    {
		clase.put("class", labelFor(cls));
		OWLReasoner reasoner = reasonerFactory.createReasoner(ontology);
        NodeSet<OWLNamedIndividual> instances = reasoner.getInstances(cls, true);
        
        if(!instances.isEmpty())
        {
        	Iterator<OWLNamedIndividual> it = instances.entities().iterator();
            JSONArray instArray = new JSONArray();
            while(it.hasNext())
            {
            	instArray.put(it.next().getIRI().getShortForm());
            }
            clase.put("instances", instArray);
           
            	
        }
    
        
        Stream<OWLClassExpression> subs = EntitySearcher.getSubClasses(cls,ontology);
        Iterator<OWLClassExpression> it = subs.iterator();
        
        if(it.hasNext())
        {
        	JSONArray subArray = new JSONArray();
        	while(it.hasNext())
        	{
        		
            	OWLClassExpression ce = it.next();
            	JSONObject sub = new JSONObject();
            	writeToJSON(ce.asOWLClass(), ontology, reasonerFactory, sub);
            	subArray.put(sub);
            	
        	}
        	clase.put("subclasses",subArray);
        }
        
        
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
