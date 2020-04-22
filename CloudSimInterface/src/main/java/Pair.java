import org.cloudbus.cloudsim.vms.Vm;

/**
 * Class used to maintain VM IDs even after removal of some VMs.
 */
public class Pair {
    Vm vm;
    boolean isRemoved;

    Pair(){

    }

    Pair(Vm vm, boolean isRemoved){
        this.vm = vm;
        this.isRemoved = isRemoved;
    }

    public Vm getVm() {
        return vm;
    }

    public boolean isRemoved() {
        return isRemoved;
    }
}