import multiprocessing

bind = "0.0.0.0:443"
backlog = 1024

timeout = 30
keepalive = 3

worker_class = "gthread"
workers = multiprocessing.cpu_count() * 2 + 1
threads = multiprocessing.cpu_count() * 2

log_level = "critical"
proc_name = "gunalignbot"

keyfile = "server.key"
certificate = "server.crt"
