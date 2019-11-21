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
    ("cellsdr1-bes",
     "Behavioral: cellsdr1-bes"),
    ("cellsdr1-browning",
     "Browning: cellsdr1-browning"),
    ("cellsdr1-dentistry",
     "Dentistry: cellsdr1-dentistry"),
    ("cellsdr1-fm",
     "Friendship Manor: cellsdrsdr1-fm"),
    ("cellsdr1-honors",
     "Honors: cellsdrs1-honors"),
    ("cellsdr1-meb",
     "MEB: cellsdr1-meb"),
    ("cellsdr1-smt",
     "SMT: cellsdrsdr1-smt"),
    ("cellsdr1-ustar",
     "USTAR: cellsdr1-ustar")
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
     "WEB"),
    ("ebc",
     "EBC"),
    ("bookstore",
     "Bookstore"),
    ("humanities",
     "Humanities"),
    ("law73",
     "Law 73"),
    ("madsen",
     "Madsen"),
    ("sagepoint",
     "Sage Point"),
    ("moran",
     "Moran"),
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

channel_bandwidth_strings = [
    ('1.4', '1.4 MHz'),
    ('3', '3 MHz'),
    ('5', '5 MHz'),
    ('10', '10 MHz'),
]

# n PRB, width of frequency to allocate
channel_bandwidths = {
    '1.4': (6, 1.4, 0.5, 0.20),
    '3': (15, 3, 0.5, 0.20),
    '5': (25, 5, 0.5, 0.20),
    '10': (50, 10, 0.5, 0.20),
    '15': (75, 15, 0.5, 0.20),
    '20': (100, 20, 0.5, 0.20),
}

portal.context.defineParameter(
    "channel_bandwidth",
    "LTE Channel Bandwidth",
    portal.ParameterType.STRING, 
    channel_bandwidth_strings[2],
    channel_bandwidth_strings
)


params = portal.context.bindParameters()

request = portal.context.makeRequestRSpec()



installs = []

installs.append("srslte")
installs.append("gnuradio")


# fix the downlink frequency 

downlink_frequency = 2685.0

# calculate srsLTE configuration parameters

downlink_earfcn = downlink_frequency

centi_khz = downlink_frequency * 10
centi_khz = int(round(centi_khz))

if centi_khz < 26200:
	raise Exception("Too low of a downlink frequency for band 7")
if centi_khz > 26899:
	raise Exception("Too high of a downlink frequency for band 7")

earfcn = centi_khz - 26200 + 2750

channel_bandwidth_str = params.channel_bandwidth
n_prb, bandwidth, ul_amp, dl_gain = channel_bandwidths[channel_bandwidth_str]

low_downlink_frequency = downlink_frequency - bandwidth/2
high_downlink_frequency = downlink_frequency + bandwidth/2
low_uplink_frequency = downlink_frequency - bandwidth/2 - 120
high_uplink_frequency = downlink_frequency + bandwidth/2 - 120

request.requestSpectrum(low_downlink_frequency, high_downlink_frequency,0)
request.requestSpectrum(low_uplink_frequency, high_uplink_frequency, 0)

channel_setup_format_string = ("channel_setup-{n_prb}-{earfcn}-{ul_amp}-"
                                    "{dl_gain}")
installs.append(channel_setup_format_string.format(n_prb=n_prb,
                                                    earfcn=earfcn,
                                                    ul_amp=ul_amp,
                                                    dl_gain=dl_gain))

for i, x310_radio in enumerate(params.x310_radios):
    x310_node_pair(i, x310_radio, params.x310_pair_nodetype, installs)

for i, b210_node in enumerate(params.b210_nodes):
    b210_nuc_pair(i, b210_node, installs)


portal.context.printRequestRSpec()
