# How To Use
Within each folder *search* and *website*:

```
docker build -t <image name> .
docker run -p -d <host port>:<virtual port> <image name>
```

where *image name* is a custom name for the image generated in *docker build*

The host port is a custom port on the host machine. Any incoming packets to the host ports will be translated to the virtual ports for the virtual machine. The virtual ports are listed in the *Dockerfile* of each folder. Note that MongoDB has a default port number: 21017.

You can then access and utilize the search engine:
'''
http://<hostname>:<host port>
'''
where the *host port* refers to the host port number defined for the *website* folder
