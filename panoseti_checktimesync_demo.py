#! /usr/bin/env python3

from panoseti_checktimesync import checktimesync
import qstart, config_file

def main():
    # set the quabo to image mode
    qstart.qstart(True)

    # get uart_port, wrs_ip from config file
    obs_config = config_file.get_obs_config()
    gps_port = obs_config['gps_port']
    wrs_ip = obs_config['wr_ip_addr']
    cts = checktimesync()
    state  = cts.check_all_time()
    print('PANOSETI Time Sync State: ', state)
    # set the quabo to idle mode
    qstart.qstart(False)
    
if __name__=='__main__':
    main()
 