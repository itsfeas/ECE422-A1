#!/bin/bash 


tensorboard --logdir runs/ --port 8888 --reload_interval=30 --reload_multifile=true
