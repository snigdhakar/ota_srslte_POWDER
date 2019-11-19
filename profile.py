#!/usr/bin/python

"""
This profile allows the allocation of resources for over-the-air
operation on the POWDER platform. Specifically, the profile has
options to request the allocation of SDR radios in rooftop 
base-stations and fixed-endpoints (i.e., nodes deployed at
human height).

Map of deployment is here:
https://www.powderwireless.net/map

The base-station SDRs are X310s and connected to an antenna
covering the cellular band (1695 - 2690 MHz), i.e., cellsdr,
or to an antenna covering the CBRS band (3400 - 3800 MHz), i.e.,
cbrssdr. Each X310 is paired with a compute node (by default
a Dell d740).

The fixed-endpoint SDRs are B210s each of which is paired with 
an Intel NUC small form factor compute node. Both B210s are connected
to broadband antennas: nuc1 is connected in an RX only configuration,
while nuc2 is connected in a TX/RX configuration.

By default the profile will install srsLTE software, as well as
GNU Radio and the UHD software tools.

Resources needed to realize a basic srsLTE setup consisting of a UE, an eNodeB and an EPC core network:

  * Frequency ranges (uplink and downlink) for LTE FDD operation. 
  * A "nuc2" fixed-end point compute/SDR pair. (This will run the UE side.)
  * A "cellsdr" SDR base station. (This will be the radio side of the eNodeB.)
  * A "d740" compute node. (This will run both the eNodeB software and the EPC software.)
  
**Specific resources that can be used:** 

  * Frequencies:
   * Uplink frequency: 2560 MHz to 2570 MHz
   * Downlink frequency: 2680 MHz to 2690 MHz

  * Hardware (at least one set of resources are needed):
   * Moran Eye Center, nuc2; Emulab, cellsdr1-ustar; Emulab, d740 
   * Humanities, nuc2; Emulab, cellsdr1-smt; Emulab, d740
   * Building 73, nuc2; Emulab, cellsdr1-browning; Emulab, d740
   * Bookstore, nuc2; Emulab, cellsdr1-bes; Emulab, d740

The instuctions below assume the first configuration.

Instructions:

#### To run the srsLTE software

**To run the EPC**

Open a terminal on the `cellsdr1-ustar-comp` node in your experiment. (Go to the "List View"
in your experiment. If you have ssh keys and an ssh client working in your
setup you should be able to click on the black "ssh -p ..." command to get a
terminal. If ssh is not working in your setup, you can open a browser shell
by clicking on the Actions icon corresponding to the node and selecting Shell
from the dropdown menu.)

Start up the EPC:

    sudo srsepc
    
**To run the eNodeB**

Open another terminal on the `cellsdr1-ustar-comp` node in your experiment.

Start up the eNodeB:

    sudo srsenb

**To run the UE**

Open a terminal on the `b210-moran-nuc2` node in your experiment.

Start up the UE:

    sudo srsue

**Verify functionality**

Open another terminal on the `b210-moran-nuc2` node in your experiment.

Verify that the virtual network interface tun_srsue" has been created:

    ifconfig tun_srsue

Run ping to the SGi IP address via your RF link:
    
    ping 172.16.0.1

Killing/restarting the UE process will result in connectivity being interrupted/restored.

If you are using an ssh client with X11 set up, you can run the UE with the GUI
enabled to see a real time view of the signals received by the UE:

    sudo srsue --gui.enable 1

"""

import geni.portal as portal
import geni.rspec.pg as rspec
import geni.rspec.emulab.pnext as pn
import geni.rspec.igext as ig
import geni.rspec.emulab.spectrum as spectrum

x310_node_disk_image = \
        "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU18-64-STD"
b210_node_disk_image = \
        "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU18-64-STD"

setup_command = "/local/repository/startup.sh"


def x310_node_pair(idx, x310_radio, node_type, installs):
    radio_link = request.Link("radio-link-%d"%(idx))
    radio_link.bandwidth = 10*1000*1000

    node = request.RawPC("%s-comp"%(x310_radio.radio_name))
    node.hardware_type = node_type
    node.disk_image = x310_node_disk_image
    node.component_manager_id = "urn:publicid:IDN+emulab.net+authority+cm"

    service_command = " ".join([setup_command] + installs)
    node.addService(rspec.Execute(shell="bash", command=service_command))

    node_radio_if = node.addInterface("usrp_if")
    node_radio_if.addAddress(rspec.IPv4Address("192.168.40.1",
                                               "255.255.255.0"))
    radio_link.addInterface(node_radio_if)

    radio = request.RawPC("%s-x310"%(x310_radio.radio_name))
    radio.component_id = x310_radio.radio_name
    radio_link.addNode(radio)


def b210_nuc_pair(idx, b210_node, installs):
    b210_nuc_pair_node = request.RawPC("b210-%s-%s"%(b210_node.aggregate_id,b210_node.component_id))
    agg_full_name = "urn:publicid:IDN+%s.powderwireless.net+authority+cm"%(b210_node.aggregate_id)
    b210_nuc_pair_node.component_manager_id = agg_full_name
    b210_nuc_pair_node.component_id = b210_node.component_id

    b210_nuc_pair_node.disk_image = b210_node_disk_image

    service_command = " ".join([setup_command] + installs)
    b210_nuc_pair_node.addService(
        rspec.Execute(shell="bash", command=service_command))



portal.context.defineParameter("x310_pair_nodetype",
                               "Type of compute node paired with the X310 Radios",
                               portal.ParameterType.STRING, "d740")

rooftop_names = [
    ("cbrssdr1-bes",
     "Behavioral: cbrssdr"),
    ("cbrssdr1-browning",
     "Browning: cbrssdr"),
    ("cbrssdr1-dentistry",
     "Dentistry: cbrssdr"),
    ("cbrssdr1-fm",
     "Friendship Manor: cbrssdr"),
    ("cbrssdr1-honors",
     "Honors: cbrssdr"),
    ("cbrssdr1-meb",
     "MEB: cbrssdr"),
    ("cbrssdr1-smt",
     "SMT: cbrssdr"),
    ("cbrssdr1-ustar",
     "USTAR: cbrssdr"),
    ("cellsdr1-bes",
     "Behavioral: cellsdr"),
    ("cellsdr1-browning",
     "Browning: cellsdr"),
    ("cellsdr1-dentistry",
     "Dentistry: cellsdr"),
    ("cellsdr1-fm",
     "Friendship Manor: cellsdr"),
    ("cellsdr1-honors",
     "Honors: cellsdr"),
    ("cellsdr1-meb",
     "MEB: cellsdr"),
    ("cellsdr1-smt",
     "SMT: cellsdr"),
    ("cellsdr1-ustar",
     "USTAR: cellsdr")
]

portal.context.defineStructParameter("x310_radios", "X310 Radios", [],
                                     multiValue=True,
                                     itemDefaultValue=
                                     {},
                                     min=0, max=None,
                                     members=[
                                        portal.Parameter(
                                             "radio_name",
                                             "Rooftop base-station X310",
                                             portal.ParameterType.STRING,
                                             rooftop_names[0],
                                             rooftop_names)
                                             
                                     ])


fixed_endpoint_aggregates = [
    ("web",
     "Warnock Engineering Building"),
    ("ebc",
     "Eccles Broadcast Center"),
    ("bookstore",
     "Bookstore"),
    ("humanities",
     "Humanities"),
    ("law73",
     "Law (building 73)"),
    ("madsen",
     "Madsen Clinic"),
    ("sagepoint",
     "Sage Point"),
    ("moran",
     "Moran Eye Center"),
]

portal.context.defineStructParameter("b210_nodes", "B210 Radios", [],
                                     multiValue=True,
                                     itemDefaultValue=
                                     {"component_id": "nuc2"},
                                     min=0, max=None,
                                     members=[
                                         portal.Parameter(
                                             "component_id",
                                             "Component ID (like nuc2)",
                                             portal.ParameterType.STRING, ""),
                                         portal.Parameter(
                                             "aggregate_id",
                                             "Fixed Endpoint B210",
                                             portal.ParameterType.STRING,
                                             fixed_endpoint_aggregates[0],
                                             fixed_endpoint_aggregates)
                                     ],
                                    )

portal.context.defineParameter("install_srslte",
                               "Should srsLTE Radio be installed?",
                               portal.ParameterType.BOOLEAN, True)
portal.context.defineParameter("install_gnuradio",
                               "Should GNU Radio (where uhd_fft, uhd_siggen, "
                               "etc come from be installed?",
                               portal.ParameterType.BOOLEAN, True)

params = portal.context.bindParameters()

request = portal.context.makeRequestRSpec()

request.requestSpectrum(2560, 2570, 0)
request.requestSpectrum(2680, 2690, 0)

installs = []
if params.install_srslte:
    installs.append("srslte")

if params.install_gnuradio:
    installs.append("gnuradio")

for i, x310_radio in enumerate(params.x310_radios):
    x310_node_pair(i, x310_radio, params.x310_pair_nodetype, installs)

for i, b210_node in enumerate(params.b210_nodes):
    b210_nuc_pair(i, b210_node, installs)


portal.context.printRequestRSpec()
