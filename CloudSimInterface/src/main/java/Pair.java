import org.cloudbus.cloudsim.vms.Vm;

/**
 * Class used to maintain two thresholds for each location.
 */
public class Pair {
    Double first; //Threshold for location
    Double second; //Threshold for host

    Pair(){

    }

    public Pair(Double first, Double second) {
        this.first = first;
        this.second = second;
    }

    public Double getFirst() {
        return first;
    }

    public Double getSecond() {
        return second;
    }
}