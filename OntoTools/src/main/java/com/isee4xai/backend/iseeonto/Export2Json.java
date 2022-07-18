package com.isee4xai.backend.iseeonto;

import static org.semanticweb.owlapi.search.EntitySearcher.getAnnotationObjects;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.Set;
import java.util.stream.Stream;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.AxiomType;
import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLAnnotation;
import org.semanticweb.owlapi.model.OWLAnnotationProperty;
import org.semanticweb.owlapi.model.OWLAnnotationValue;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLClassExpression;
import org.semanticweb.owlapi.model.OWLDataFactory;
import org.semanticweb.owlapi.model.OWLEntity;
import org.semanticweb.owlapi.model.OWLIndividual;
import org.semanticweb.owlapi.model.OWLLiteral;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLObject;
import org.semanticweb.owlapi.model.OWLObjectProperty;
import org.semanticweb.owlapi.model.OWLObjectPropertyAssertionAxiom;
import org.semanticweb.owlapi.model.OWLObjectPropertyExpression;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyCreationException;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.reasoner.NodeSet;
import org.semanticweb.owlapi.reasoner.OWLReasoner;
import org.semanticweb.owlapi.reasoner.OWLReasonerFactory;
import org.semanticweb.owlapi.reasoner.structural.StructuralReasonerFactory;
import org.semanticweb.owlapi.search.EntitySearcher;
import org.semanticweb.owlapi.util.OWLAPIStreamUtils;

//import org.json.simple.parser.JSONParser;
//import org.json.simple.parser.ParseException;

/**
 * Hello world!
 *
 */
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
				propertyObject.put("class", labelFor(cls));//Export the class of ExplanationExperience 
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
	/*Export the annotation property of instance 'ins'*/
	   List<OWLAnnotation> annoList= OWLAPIStreamUtils.asList(EntitySearcher.getAnnotationObjects(ins, ontology));
	   JSONArray annoArray = new JSONArray();
       for(Iterator<OWLAnnotation> annoIterator = annoList.iterator();annoIterator.hasNext();){
		   OWLAnnotation anno = annoIterator.next();
		   JSONObject properties = new JSONObject();
		   OWLAnnotationProperty property;
			/*Get the name of the annotation property */
//		   if(anno.getProperty()!=null) 
//				{
		   if(anno.getProperty().isComment()||anno.getProperty().isLabel()){
				continue;
			}
			else 
			{	property = anno.getProperty();
				properties.put("name", property.getIRI().getShortForm());
		      	/*Get the value of the annotation property */
				OWLAnnotationValue indValue = anno.getValue();
//				if (indValue instanceof OWLLiteral) //subclass is associated with rdfs:Literal
//	    		{
//				//         OWLLiteral literal = (OWLLiteral) indValue;
//				           properties.put("instance",((OWLLiteral) indValue).getLiteral());
//				//         System.out.println("Literal:" +((OWLLiteral) indValue).getLiteral());
//				 }
//				else {
//				    //if (indValue instanceof IRI) {
				properties.put("instance",((IRI) indValue).getShortForm());
            	/*Add all the properties to the array*/
				annoArray.put(properties);
				for (int k = 0; k < annoArray.length(); k++) {
			    	propertyObject.put("property", annoArray); //Put the array into the JSON file			
				}
//				System.out.println(properties);
			    //Get the OWLNamedindividual
			    Set<OWLNamedIndividual> i = ontology.getIndividualsInSignature();
			    for(Iterator<OWLNamedIndividual> itCls= i.iterator();itCls.hasNext();) {
			         OWLNamedIndividual ind =itCls.next();
			         /*Check if the instance is already exported or not - should not have cycles*/
			         if((ind.getIRI().getShortForm()).equals(((IRI) indValue).getShortForm())) {
						/*Export the class of the instance*/
			             classFor(ind,properties);
			      		 /*Pass the instance and property object*/
			        	 exportToJSON( ind, ontology, properties);
			         }
			       else {
			       		continue;
			       }
			     }
//				}	       
     		}
    	}
    	objectPropertyFor(ins,propertyObject,annoArray);
    	classFor(ins,propertyObject);
 }


/*Get the object property of instance 'ins'*/
private String objectPropertyFor(OWLNamedIndividual insta, JSONObject propertyObj, JSONArray propertyArray) throws JSONException, IOException {		
	for (OWLObjectProperty obj : ontology.getObjectPropertiesInSignature()) {
		NodeSet<OWLNamedIndividual> objVal = reasoner.getObjectPropertyValues(insta, obj);
		Set<OWLNamedIndividual> propValues = objVal.getFlattened();
		for (Iterator<OWLNamedIndividual> objIterator = objVal.entities().iterator(); objIterator.hasNext();) {
			OWLNamedIndividual obInd=objIterator.next();
			JSONObject objProperty = new JSONObject();
		   /*Get the Object property 'obj' of the instance 'ins'*/
			objProperty.put("name",obj.getIRI().getShortForm());
			objProperty.put("instance",obInd.getIRI().getShortForm());
			classFor(insta,objProperty);
			propertyArray.put(objProperty);
//			System.out.println(objProperty);
		    propertyObj.put("property", propertyArray);
			exportToJSON(obInd, ontology, objProperty);
		}
	}
	return null;
}    

/*Export the class/es of the property (annotation and object) values and its annotations - */
private String classFor(OWLNamedIndividual insta, JSONObject propertyObj){
	 List<OWLClassExpression> listCls = OWLAPIStreamUtils.asList(EntitySearcher.getTypes(insta,ontology));
//	 System.out.println(listCls);
//	 List<String> classList = new ArrayList<>();
	 JSONArray classArray = new JSONArray();
	 for (Iterator<OWLClassExpression> clsIterator = listCls.iterator(); clsIterator.hasNext();) {
//		  OWLClassExpression obInd = clsIterator.next();
//		  propertyObj.put("classes", obInd.asOWLClass().getIRI().getFragment());
		  OWLClass obInd = (OWLClass) clsIterator.next();
		  /*Export the list of classes associated with the instance*/
		  classArray.put(labelFor(obInd));
		  for (int j = 0; j < classArray.length(); j++) {
			  propertyObj.put("classes", classArray);
		  }

		  /*Export the 'subClass of' and their annotation properties*/
//		  ontology.getAxioms(AxiomType.SUBCLASS_OF));
//		  getOWLSubClassOfAxiom

		  
		  /*Export the applicableSimilarityStrategy*/ 
		  //if insta has no objProp or annoProp -> get the class label & check for clsAnno. 
		  OWLAnnotationProperty clsAnno = df.getOWLAnnotationProperty("http://www.w3id.org/iSeeOnto/SimilarityKnowledge#applicableSimilarityStrategy");
		  Stream<OWLAnnotation> clsStream = EntitySearcher.getAnnotationObjects(obInd.asOWLClass(), ontology);
		  JSONArray clsAnnoArray = new JSONArray();
		  for(Iterator<OWLAnnotation> clsAnnoIterator = clsStream.iterator();clsAnnoIterator.hasNext();){
				OWLAnnotation anno = clsAnnoIterator.next();
//				if(anno.getProperty().equals(df.getRDFSLabel())){}// here you have found a rdfs:label annotation, so you can use the value for your purposes 
				if(anno.getProperty().equals(clsAnno)) {
					if(!anno.getValue().toString().equalsIgnoreCase("_:genid1422")) //DataType -> <SimilarityKnowledge:applicableSimilarityStrategy><rdf:Description/></SimilarityKnowledge:applicableSimilarityStrategy>
					{		
						/*Get the name of the annotation property */
						OWLAnnotationProperty property = anno.getProperty();
						JSONObject clsAnnoProperty = new JSONObject();
						/*Get the value of the annotation property */
						if (anno.getValue() instanceof OWLLiteral) {
		                    OWLLiteral val = (OWLLiteral) anno.getValue();
		                    System.out.println(anno.getValue() instanceof OWLLiteral);
						}
						else {
							OWLAnnotationValue indValue = anno.getValue();
						    clsAnnoProperty.put(property.getIRI().getShortForm(),((IRI) indValue).getShortForm());
//							clsAnnoProperty.put("name", property.getIRI().getShortForm());
//							clsAnnoProperty.put("class",((IRI) indValue).getShortForm());
//						    System.out.println(anno.getProperty().getIRI().getShortForm() + ": " + ((IRI) anno.getValue()).getShortForm());
			            	/*Add all the properties to the array*/
							clsAnnoArray.put(clsAnnoProperty);
							for (int k = 0; k < clsAnnoArray.length(); k++) {
								propertyObj.put("property", clsAnnoArray); //Put the array into the JSON file			
							}
					   }
					}
					else {
						continue;
					}
				}
					
				else {
					continue; //iterate through the rdfs:label/comment, dc:description, etc.
				}
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




/*Export the subclasses*/
//Stream<OWLClassExpression> subs = EntitySearcher.getSubClasses((OWLClass) obInd,ontology);
//	JSONArray subArray = new JSONArray();
//for(Iterator<OWLClassExpression> subclassIterator = subs.iterator();subclassIterator.hasNext();){
//        	OWLClassExpression subclass = subclassIterator.next();
//        	JSONObject sub = new JSONObject();
//        	sub.put("class", subclass.asOWLClass().getIRI().getFragment());
//        	System.out.println(subclass.asOWLClass().getIRI().getFragment());
//        	subArray.put(sub);
//        	propertyObj.put("subclass",subArray);
// }

/*Export the dataproperties*/

   
 /*Export the sub object properties related to a specified OWLNamedIndividual*/
//  private Set<OWLObjectProperty> getRelatedSubObjectProperties(OWLNamedIndividual individual) {
//    HashSet<OWLObjectProperty> relatedObjectProperties = new HashSet<>();
//
//    HashSet<OWLObjectPropertyExpression> subProperties = new HashSet<>();
//    subProperties.addAll(hasPart.getSubProperties(ontology));
//
//    Set<OWLClass> types = reasoner.getTypes(individual, true).getFlattened();
//
//    for (OWLObjectPropertyExpression property : subProperties) {
//        Set<OWLClassExpression> domains = property.getDomains(ontology);
//        for (OWLClassExpression domain : domains) {
//            if (types.contains(domain.asOWLClass())) {
//                relatedObjectProperties.add(property.asOWLObjectProperty());
//            }
//        }
//    }
//
//    return relatedObjectProperties;
// }
   
   
}

