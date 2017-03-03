
import org.nrg.framework.annotations.XnatPlugin;
import org.nrg.framework.annotations.XnatDataModel;

@XnatPlugin(value = "subjGenProcDataXnatPlugin", name = "DAX subjGenProcData XNAT 1.7 Plugin",
            description = "This is the DAX subjGenProcData data type for XNAT 1.7 Plugin.",
            dataModels = {@XnatDataModel(value = "proc:subjGenProcData", singular = "Longitudinal Processing", plural="Longitudinal Processings", code = "Subj Proc")})
public class subjGenProcDataXnatPlugin {
}
