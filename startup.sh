#!/bin/bash

# Get the emulab repo 
while ! wget -qO - http://repos.emulab.net/emulab.key | sudo apt-key add -
do
    echo Failed to get emulab key, retrying
done

while ! sudo add-apt-repository -y http://repos.emulab.net/powder/ubuntu/
do
    echo Failed to get johnsond ppa, retrying
done

while ! sudo apt-get update
do
    echo Failed to update, retrying
done

do_channel_setup=0

for thing in $*
do
    cmd=(`echo $thing | tr '-' '\n'`)
    case ${cmd[0]} in
        gnuradio)
            while ! sudo DEBIAN_FRONTEND=noninteractive apt-get install -y gnuradio
            do
                echo Failed to get gnuradio, retrying
            done
            ;;

        gnuradio-companion)
            while ! sudo DEBIAN_FRONTEND=noninteractive apt-get install -y gnuradio libgtk-3-dev gir1.2-gtk-3.0 python3-gi gobject-introspection python3-gi-cairo
            do
                echo Failed to get gnuradio, retrying
            done
            ;;

        srslte)
            while ! sudo DEBIAN_FRONTEND=noninteractive apt-get install -y srslte uhd-host
            do
                echo Failed to get srsLTE, retrying
            done
            ;;
        channel_setup)
            n_prb=${cmd[1]}
            earfcn=${cmd[2]}
            ul_amp=${cmd[3]}
            dl_gain=${cmd[4]}
            do_channel_setup=1
            ;;
    esac
done

while ! sudo "/usr/lib/uhd/utils/uhd_images_downloader.py"
do
    echo Failed to download uhd images, retrying
done

if [[ $do_channel_setup == 1 ]]
then
    sudo patch /etc/srslte/ue.conf <<END
--- ue.conf.orig	2019-11-18 18:46:59.583996306 -0700
+++ ue.conf	2019-11-18 18:49:11.543994481 -0700
@@ -31,9 +31,9 @@
 #                     Default is auto (yes for UHD, no for rest)
 #####################################################################
 [rf]
-dl_earfcn = 3400
+dl_earfcn = ${earfcn}
 freq_offset = 0
-tx_gain = 80
+tx_gain = 89
 #rx_gain = 40

 #nof_radios = 1
@@ -289,7 +289,7 @@
 #pregenerate_signals = false
 #pdsch_csi_enabled  = true
 #pdsch_8bit_decoder = false
-#force_ul_amplitude = 0
+force_ul_amplitude = ${ul_amp}

 #####################################################################
 # General configuration options
END

    sudo patch /etc/srslte/enb.conf <<END
--- enb.conf.orig	2019-11-18 18:47:04.995996231 -0700
+++ enb.conf	2019-11-18 18:53:58.875990508 -0700
@@ -28,7 +28,8 @@
 mme_addr = 127.0.1.100
 gtp_bind_addr = 127.0.1.1
 s1c_bind_addr = 127.0.1.1
-n_prb = 50
+n_prb = ${n_prb}
+dgain = ${dl_gain}
 #tm = 4
 #nof_ports = 2
 
@@ -66,9 +67,9 @@
 #                     Default "auto". B210 USRP: 400 us, bladeRF: 0 us. 
 #####################################################################
 [rf]
-dl_earfcn = 3400
-tx_gain = 80
-rx_gain = 40
+dl_earfcn = ${earfcn}
+tx_gain = 31.5
+rx_gain = 31.5
 
 #device_name = auto
 
END

    if [[ ${n_prb} == 6 ]]
    then
        sudo patch /etc/srslte/sib.conf <<END
--- sib.conf.orig	2019-11-18 19:04:40.274132729 -0700
+++ sib.conf	2019-11-18 19:05:05.674949801 -0700
@@ -46,7 +46,7 @@
             {
                 high_speed_flag = false;
                 prach_config_index = 3;
-                prach_freq_offset = 2;
+                prach_freq_offset = 0;
                 zero_correlation_zone_config = 5;
             };
         };
END
    fi
fi
