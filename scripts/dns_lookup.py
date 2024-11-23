# ref: https://stackoverflow.com/questions/46836616/python-socket-getaddrinfo-taking-5-seconds-about-0-1-of-requests
import socket
import timeit

def single_dns_lookup():
    start = timeit.default_timer()
    try:
        print("Attempting DNS lookup...")
        result = socket.getaddrinfo('postgres', 5432)
        print("DNS lookup successful:", result)
    except socket.gaierror as e:
        print("DNS lookup failed:", e)
    end = timeit.default_timer()

    return int(end - start)

timings = {}

for _ in range(0, 100):
    time = single_dns_lookup()
    print(time)
    try:
        timings[time] += 1
    except KeyError:
        timings[time] = 1

print(timings)
