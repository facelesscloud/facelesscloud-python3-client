# Facelesscloud Client
# https://facelesscloud.com/

## Requirements
  Python3

### Description

  This is a client to interact easily with the Faceless Cloud server API.
  https://api.facelesscloud.com/


## Usage

  ### Installation

    * pip3 install facelesscloud

  ### Get functions

    get_region    Give you all Region informations and their IDs.
    get_os        Give you all Operating System informations and their IDs.
    get_flavor    Give you all Flavor Machine type informations and their IDs.
  
  ### Make configuration file

    Simply use the subcommand "makeconf" to easy start spawning instances.
    
    * facelesscloud makeconf

  ### Spawn a new instance with the config file

    Now Spawn the instance using the config file that you just created.
    
    * facelesscloud spawn -c instance-conf.json

  ### Spawn a new instance with args

    You can also directly use "spawn" subcommand send give the required params.
    
    * facelesscloud spawn --time 24 --flavor 201 --operating_system 167 --region 1 --sshkey /home/USER/.ssh/id_rsa.pub --kickstart ../path_to_your_bash_script/kick.sh

  ### Ful Documentation

    You can visit https://facelesscloud.com/documentation for full information.
    Or simply use the "--help" argument to know about other subcommands like, os, region, flavor, etc...
    
    * facelesscloud --help


### Platform

 - Tested against Ubuntu 16 and 18, but can run on Centos or any Linux Distro with python3.
 - Little QRCode diplaying bug under Windows, but should work fine. 


## Authors and maintainers

  Originally written by Faceless Cloud

## License

  This is a free software. Anyone is free to copy, modify, publish, use, compile, sell or distribute this software.
  Do what ever the fuck you want.
