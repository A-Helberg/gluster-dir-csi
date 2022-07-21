job "gluster-dir-csi" {
  type        = "system"
  datacenters = ["dc1"]

  group "csi" {

    constraint {
      operator = "distinct_hosts"
      value    = "true"
    }

    # restart policy for failed portworx tasks
    restart {
      attempts = 3
      delay    = "30s"
      interval = "5m"
      mode     = "fail"
    }

    # how to handle upgrades of portworx instances
    update {
      max_parallel     = 1
      health_check     = "checks"
      min_healthy_time = "10s"
      healthy_deadline = "9m"
      auto_revert      = true
      canary           = 0
      stagger          = "30s"
    }

    task "node" {
      driver       = "docker"
      kill_timeout = "120s"    # allow portworx 2 min to gracefully shut down
      kill_signal  = "SIGTERM" # use SIGTERM to shut down the nodes

      csi_plugin {
        id        = "gluster-dir"
        type      = "monolith"
        mount_dir = "/csi"
      }

      # container config
      config {
        #image = "alpine"
        #command = "tail"
        #args = ["-f", "/dev/zero"]
        image        = "ahelberg/gluster-dir-csi"
        privileged = true
      }

      # resource config
      resources {
        cpu    = 1024
        memory = 500
      }
    }
  }
}
