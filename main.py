from concurrent import futures

import logging

import socket
import os

import grpc
import csi_pb2
import csi_pb2_grpc

import subprocess

#csi_sock_full_path = "/Users/andre/Projects/opensource/gluster-dir-csi/csi.sock"
csi_sock_full_path = "/csi/csi.sock"
gluster_host = "10.0.114.218"
gluster_volume = "vol_main"


def unmount(path):
    print("Unmounting", path)
    return subprocess.run(["umount", path])

def mount(volume, path):
    print("Mounting", volume, "at", path)
    p = subprocess.run(["mount","-t", "glusterfs", "%s:/%s/%s" % (gluster_host, gluster_volume, volume), path])
    if p.returncode == 0:
        return True

    # Might be a stale mount, unmount and try again
    if p.returncode == 32:
        return True
    return p


class Identity(csi_pb2_grpc.Identity):

    def GetPluginInfo(self, request, context):
        return csi_pb2.GetPluginInfoResponse(name='gluster-dir-csi',vendor_version="1")

    def Probe(self, request, context):
        return csi_pb2.ProbeResponse()

    def GetPluginCapabilities(self, request, context):
        return csi_pb2.GetPluginCapabilitiesResponse(
            capabilities=[
                csi_pb2.PluginCapability(
                    service=csi_pb2.PluginCapability.Service(type=csi_pb2.PluginCapability.Service.Type.CONTROLLER_SERVICE)
                )
            ])

class Controller(csi_pb2_grpc.Controller):

    def ControllerGetCapabilities(self, request, context):
       return csi_pb2.ControllerGetCapabilitiesResponse(capabilities=[
           csi_pb2.ControllerServiceCapability(rpc = csi_pb2.ControllerServiceCapability.RPC(type=csi_pb2.ControllerServiceCapability.RPC.Type.CREATE_DELETE_VOLUME)),
       ])

    def CreateVolume(self, request, context):
      name = request.name
      print("CreateVolume", name)
      p = subprocess.run(["mkdir", "-p", "/mnt/main/%s" % name])
      volume = csi_pb2.Volume(volume_id=name)
      return csi_pb2.CreateVolumeResponse(volume=volume);

class Node(csi_pb2_grpc.Node):

    def NodeGetInfo(self, request, context):
        node_id = os.getenv("HOSTNAME")
        return csi_pb2.NodeGetInfoResponse(node_id=node_id)

    def NodeGetCapabilities(self, request, context):
        return csi_pb2.NodeGetCapabilitiesResponse(capabilities = [
           csi_pb2.NodeServiceCapability(rpc= csi_pb2.NodeServiceCapability.RPC(type = csi_pb2.NodeServiceCapability.RPC.Type.STAGE_UNSTAGE_VOLUME))
        ]);

    def NodePublishVolume(self,request,context):
        volume_id = request.volume_id
        path = request.target_path
        print("Node Publish Volume", path)
        p = subprocess.run(["mkdir", "-p", path], check=True)
        res = mount(volume_id, path)
        if res is True:
            return csi_pb2.NodePublishVolumeResponse();
        print(res)

    def NodeUnpublishVolume(self,request,context):
        path = request.target_path
        print("NodeUnpublishVolume", path)
        p = subprocess.run(["umount", path])
        return csi_pb2.NodeUnpublishVolumeResponse();

    def NodeStageVolume(self, request, context):
        volume_id = request.volume_id
        path = request.staging_target_path
        print("Node Stage Volume", path)
        res = mount(volume_id, path)
        if res is True:
            return csi_pb2.NodeStageVolumeResponse()
        print(res)

    def NodeUnstageVolume(self, request, context):
        path = request.staging_target_path
        print("NodeUnstageVolume", path)
        p = subprocess.run(["umount", path])
        return csi_pb2.NodeUnstageVolumeResponse()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    csi_pb2_grpc.add_IdentityServicer_to_server(Identity(), server)
    csi_pb2_grpc.add_ControllerServicer_to_server(Controller(), server)
    csi_pb2_grpc.add_NodeServicer_to_server(Node(), server)

    print("About to start listening on", csi_sock_full_path)
    server.add_insecure_port(f'unix://%s' % csi_sock_full_path )
    server.start()
    print("Waiting for termination")
    server.wait_for_termination()

if __name__ == '__main__':
    p = subprocess.run(["mkdir", "-p", "/mnt/main"])
    p = subprocess.run(["mount", "-t", "glusterfs", "%s:/%s" % (gluster_host, gluster_volume), "/mnt/main"],check=True)

    logging.basicConfig()
    serve()
