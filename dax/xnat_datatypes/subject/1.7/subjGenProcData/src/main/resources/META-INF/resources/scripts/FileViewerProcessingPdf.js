function FileViewerProcessingPdf(_objp){
	//categories.object
	this.loading=0;
	this.requestRender=false;
	this.objp=_objp;
	if(this.objp.categories==undefined){
		this.objp.categories=new Object();
		this.objp.categories.ids=new Array();
	}
	
	if(this.objp.categories["misc"]==undefined || this.objp.categories["misc"]==null){
		this.objp.categories["misc"]=new Object();
		this.objp.categories["misc"].cats=new Array();
	}
	
	this.init=function(){
		if(this.loading==0){
			this.loading=1;
			this.resetCounts();
			var catCallback={
				success:this.processCatalogs,
				failure:this.handleFailure,
                cache:false, // Turn off caching for IE
				scope:this
			}
		
			YAHOO.util.Connect.asyncRequest('GET',this.objp.uri + '/resources?all=true&format=json&file_stats=true&sortBy=category,cat_id,label&timestamp=' + (new Date()).getTime(),catCallback,null,this);
			
		}else if(this.loading==1){
			//in process
		}
	}
	
	this.handleFailure=function(o){		
		closeModalPanel("refresh_file");
		alert("Error loading files");
	}
	
   this.getAssessor=function(ac, aid){
   		var gsAssessors=this.objp.categories[ac];
   		if(gsAssessors!=undefined && gsAssessors!=null){
			for(var gsaC=0;gsaC<gsAssessors.length;gsaC++){
				if(gsAssessors[gsaC].id==aid){
					return gsAssessors[gsaC];
				}
			}
   		}
		gsAssessors=null;
   		return null;
   }
   
   this.clearCatalogs=function(o){
   		var scans;
   		//clear catalogs
   		for(var catC=0;catC<this.objp.categories.ids.length;catC++)
   		{
   			scans=this.objp.categories[this.objp.categories.ids[catC]];
   			for(var sC=0;sC<scans.length;sC++){
   				scans[sC].cats =new Array();
   			}
   			
   			scans=null;
   		}
   		this.objp.categories["misc"].cats=new Array();
   }
   
   this.processCatalogs=function(o){
   		closeModalPanel("catalogs");
   		this.clearCatalogs();
   		
    	var catalogs= eval("(" + o.responseText +")").ResultSet.Result;
    	
    	for(var catC=0;catC<catalogs.length;catC++){
    		var assessor=this.getAssessor(catalogs[catC].category,catalogs[catC].cat_id);
    		if(assessor!=null){
    			if(assessor.cats==null || assessor.cats==undefined){
    				assessor.cats=new Array();
    			}
    			assessor.cats.push(catalogs[catC]);
    		}else{
    			if(this.objp.categories["misc"].cats==null || this.objp.categories["misc"].cats==undefined){
    				this.objp.categories["misc"].cats=new Array();
    			}
    			this.objp.categories["misc"].cats.push(catalogs[catC]);
    		}
    	}
    	
    	this.setPdfUrl();
    	
    	this.loading=3;
   }
   
   this.resetCounts=function(){
   		var assessors;
   		
   		for(var catC=0;catC<this.objp.categories.ids.length;catC++)
   		{
   			var catName=this.objp.categories.ids[catC];
   			assessors=this.objp.categories[this.objp.categories.ids[catC]];
   			for(var aC=0;aC<assessors.length;aC++){
   				var dest=document.getElementById(catName + "_" + assessors[aC].id + "_pdf");
   				if(dest!=null && dest !=undefined){
	   				dest.innerHTML="Loading...";
   				}
   			}
   			assessors=null;
   		}
   }
   
   this.setPdfUrl=function(){   		
   		for(var catC=0;catC<this.objp.categories.ids.length;catC++){
   			var catName=this.objp.categories.ids[catC];
   			var assessors=this.objp.categories[catName];
   			for(var aC=0;aC<assessors.length;aC++){
   				var dest=document.getElementById(catName + "_" + assessors[aC].id + "_pdf");
   				if(dest!=null && dest!=undefined){
   					var pdfFound = false;
	   				for(var acAC=0;acAC<assessors[aC].cats.length;acAC++){
	   					if (assessors[aC].cats[acAC].label == 'PDF'){
	   						pdfFound = true;
	   						if(assessors[aC].cats[acAC].files!=undefined && assessors[aC].cats[acAC].files!=null){
								var file=assessors[aC].cats[acAC].files[0];
								var pdfImage=serverRoot+"/images/pdf.gif";
								dest.innerHTML="<a href=\"" +serverRoot + file.URI + "\"><img src=\""+pdfImage+"\" /></a>";	
	   						} else  {
   								var callback={
			      					success:function(oResponse){
   										files = (eval("(" + oResponse.responseText + ")")).ResultSet.Result; 
										if (files.length>0) {
   											file=files[0];
											var pdfImage=serverRoot+"/images/pdf.gif";
											//oResponse.argument.dest.innerHTML="<a style='font-size:9px' target='_blank' onclick=\"location.href=\"" +serverRoot + file.URI + "';\"><img src=\""+pdfImage+"\" /></a>";
											oResponse.argument.dest.innerHTML="<a href=\"" +serverRoot + file.URI + "\"><img src=\""+pdfImage+"\" /></a>";	
										} else {
											oResponse.argument.dest.innerHTML="No PDF";
										}
			      					},
			      					failure:function(oResponse){
			      					},
			      					argument:{dest:dest}
			    				};
			    				cat_uri=this.objp.uri + "/resources/" + assessors[aC].cats[acAC].xnat_abstractresource_id;
								YAHOO.util.Connect.asyncRequest('GET',cat_uri + '/files?format=json&timestamp=' + (new Date()).getTime(),callback,null);
							}
	   					}
	   				}
	   				if(pdfFound==false){
	   					dest.innerHTML="No PDF";
	   				}
   				}
   			}
   		}
	}
}
