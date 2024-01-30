#!/bin/bash 


tensorboard --logdir runs/ --port 9999 --reload_interval=10 --reload_multifile=true
