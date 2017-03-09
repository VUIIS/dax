function FileViewerProcessing(_obja){
	//categories.object
	this.loading=0;
	this.requestRender=false;
	this.obja=_obja;
	if(this.obja.categories==undefined){
		this.obja.categories=new Object();
		this.obja.categories.ids=new Array();
	}
	
	if(this.obja.categories["misc"]==undefined || this.obja.categories["misc"]==null){
		this.obja.categories["misc"]=new Object();
		this.obja.categories["misc"].cats=new Array();
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
		
			YAHOO.util.Connect.asyncRequest('GET',this.obja.uri + '/resources?all=true&format=json&file_stats=true&sortBy=category,cat_id,label&timestamp=' + (new Date()).getTime(),catCallback,null,this);
		}else if(this.loading==1){
			//in process
		}
	}
	
	this.handleFailure=function(o){		
		closeModalPanel("refresh_file");
		alert("Error loading files");
	}
	
   this.getAssessor=function(ac, aid){
   		var gsAssessors=this.obja.categories[ac];
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
   		for(var catC=0;catC<this.obja.categories.ids.length;catC++)
   		{
   			scans=this.obja.categories[this.obja.categories.ids[catC]];
   			for(var sC=0;sC<scans.length;sC++){
   				scans[sC].cats =new Array();
   			}
   			
   			scans=null;
   		}
   		this.obja.categories["misc"].cats=new Array();
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
    			if(this.obja.categories["misc"].cats==null || this.obja.categories["misc"].cats==undefined){
    				this.obja.categories["misc"].cats=new Array();
    			}
    			this.obja.categories["misc"].cats.push(catalogs[catC]);
    		}
    	}
    	
    	this.showCounts();
    	
    	this.loading=3;
   }
   
   this.resetCounts=function(){
   		var assessors,aCount,aSize;
   		for(var catC=0;catC<this.obja.categories.ids.length;catC++)
   		{
   			var catName=this.obja.categories.ids[catC];
   			assessors=this.obja.categories[this.obja.categories.ids[catC]];
   			for(var aC=0;aC<assessors.length;aC++){
   				var dest=document.getElementById(catName + "_" + assessors[aC].id + "_stats");
   				if(dest!=null && dest !=undefined){
	   				dest.innerHTML="Loading...";
   				}
   			}
   			
   			assessors=null;
   		}
   }
   
   this.showCounts=function(){
   		var assessors,aCount,aSize;
   		
   		var assessor_counts=new Object();
   		var assessor_resources=new Array();
   		
   		for(var catC=0;catC<this.obja.categories.ids.length;catC++)
   		{
   			var catName=this.obja.categories.ids[catC];
   			assessors=this.obja.categories[catName];
   			for(var aC=0;aC<assessors.length;aC++){
   				var dest=document.getElementById(catName + "_" + assessors[aC].id + "_stats");
   				if(dest!=null && dest !=undefined){
	   				aCount=0;
	   				aSize=0;
	   				dest.innerHTML="";
	   				for(var acAC=0;acAC<assessors[aC].cats.length;acAC++){
	   				    zip_uri=this.obja.uri+"/resources/"+assessors[aC].cats[acAC].xnat_abstractresource_id;
   						dest.innerHTML+="<a href=\""+zip_uri+"/files\?format=zip\">"+assessors[aC].cats[acAC].label+"</a>";
	   					dest.innerHTML+=" (";
	   					dest.innerHTML+=assessors[aC].cats[acAC].file_count;
	   					dest.innerHTML+=" files, ";
   						dest.innerHTML+=size_format(assessors[aC].cats[acAC].file_size)
   					    dest.innerHTML+=") ";
	   					if(catName=="assessors"){
	   						if(assessor_counts[assessors[aC].cats[acAC].label]==undefined){
	   							assessor_counts[assessors[aC].cats[acAC].label]=new Object();
	   							assessor_counts[assessors[aC].cats[acAC].label].label=assessors[aC].cats[acAC].label;
	   							assessor_counts[assessors[aC].cats[acAC].label].count=0;
	   							assessor_counts[assessors[aC].cats[acAC].label].size=0;
	   							assessor_resources.push(assessors[aC].cats[acAC].label);
	   						}
   							assessor_counts[assessors[aC].cats[acAC].label].count+=parseInt(assessors[aC].cats[acAC].file_count);
   							assessor_counts[assessors[aC].cats[acAC].label].size+=parseInt(assessors[aC].cats[acAC].file_size);
	   					}
	   				}
   				}
   			}

   			assessors=null;
   		}
   }
   
   this.refreshCatalogs=function(msg_id){
		closeModalPanel(msg_id);
		openModalPanel("catalogs","Refreshing Catalog Information");
		var catCallback={
			success:this.processCatalogs,
			failure:this.handleFailure,
            cache:false, // Turn off caching for IE
			scope:this
		}
	
		this.requestRender=true;
		YAHOO.util.Connect.asyncRequest('GET',this.obja.uri + '/resources?all=true&format=json&file_stats=true&timestamp=' + (new Date()).getTime(),catCallback,null,this);
   }	
}
