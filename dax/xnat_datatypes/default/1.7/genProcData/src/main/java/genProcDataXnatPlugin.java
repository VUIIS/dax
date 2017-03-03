
import org.nrg.framework.annotations.XnatPlugin;
import org.nrg.framework.annotations.XnatDataModel;

@XnatPlugin(value = "genProcDataXnatPlugin", name = "DAX genProcData XNAT 1.7 Plugin", 
            description = "This is the DAX genProcData data type for XNAT 1.7 Plugin.",
            dataModels = {@XnatDataModel(value = "proc:genProcData", singular = "Processing", plural="Processings", code = "Proc")})
public class genProcDataXnatPlugin {
}
