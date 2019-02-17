#!/usr/bin/python
# YRL028 - APIHAT - Python 3 API Version 0.1
#
# Main program utilities
#
# James Hilder, York Robotics Laboratory, Feb 2019

import subprocess, os, timeit, time, datetime, sensors, settings, logging

def get_program_filelist():
    filelist =  [f[:-10] for f in os.listdir(settings.PROGRAM_FILEPATH) if (os.path.isfile(os.path.join(settings.PROGRAM_FILEPATH, f)) and f.endswith('_apihat.py'))]
    logging.debug(filelist)
    return filelist

def write_prog_state_info(message):
    f= open(settings.program_info_filename,"w+")
    f.write(message)
    f.close()

def request_program(index):
    filename = get_program_filelist()[int(index)] + "_apihat"
    f= open(settings.program_request_filename,"w+")
    f.write(filename)
    f.close()
    logging.info("Wrote %s to %s" % (filename,settings.program_request_filename))

def get_audio_filelist():
    filelist =  [f for f in os.listdir(settings.AUDIO_FILEPATH) if (os.path.isfile(os.path.join(settings.AUDIO_FILEPATH, f)))]
    logging.debug(filelist)
    return filelist

def decode_time(epoch_seconds):
    return datetime.datetime.fromtimestamp(epoch_seconds).strftime('%Y-%m-%d %H:%M:%S.%f')

def dynamic_values_to_csv():
    update_cpu_load()
    mem = get_mem_usage()
    return "%2.1f,%2.1f,%2.1f,%2.1f,%2.1f,%d,%2.1f,%2.1f,%2.1f,%d,%d,%2.2f,%2.2f,%d,%d,%d,%d" % (cpu_percent_load_array[0][4]*100,cpu_percent_load_array[1][4]*100,cpu_percent_load_array[2][4]*100,cpu_percent_load_array[3][4]*100,cpu_percent_load_array[4][4]*100,get_arm_clockspeed(),get_pcb_temp(),get_cpu_temp(),get_gpu_temp(),mem[0],mem[1],mem[2],get_battery_voltage(),sensors.read_adc(0),sensors.read_adc(1),sensors.read_adc(2),sensors.read_adc(3))

def dynamic_values_to_csv_header():
    return "total-cpu-load,cpu-0-load,cpu-1-load,cpu-2-load,cpu-3-load,clock-speed,pcb-temp,cpu-temp,gpu-temp,memory-used,memory-total,memory-used-pct,battery-voltage,analog-1,analog-2,analog-3,analog-4"

def get_battery_voltage():
    return sensors.read_voltage()

def get_pcb_temp():
    return sensors.read_pcb_temp()

def get_ip():
    cmd = "hostname -I | cut -d\' \' -f1"
    IP = subprocess.check_output(cmd, shell = True ).strip()
    return IP.decode()

def get_cpu_load_using_top():
    cmd = "top -bn1 | grep load | awk '{printf \"%.2f\", $(NF-2)}'"
    CPU = subprocess.check_output(cmd, shell = True )
    return CPU

total_cpu_time = 0
cpu_load_array = [[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]]
cpu_percent_load_array = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]

def get_cpu_load():
    update_cpu_load()
    return round(cpu_percent_load_array[0][4] * 1000) / 10

def update_cpu_load():
    global total_cpu_time, cpu_load_array, cpu_percent_load_array
    cmd = "head -n 5 /proc/stat"
    load = subprocess.check_output(cmd, shell = True ).splitlines()
    current_cpu_load = []
    for index,line in enumerate(load):
        tokens = line.split(b" ")
        offset = 0
        if index == 0: offset = 1 #/proc/stat adds double space for overall cpu
        user = int(tokens[1+offset])
        nice = int(tokens[2+offset])
        system = int(tokens[3+offset])
        idle = int(tokens[4+offset])
        active = user+nice+system
        total = active+idle
        cpu_line = [user,nice,system,idle,active,total]
        current_cpu_load.append(cpu_line)
    if current_cpu_load[0][5] > total_cpu_time:
         total_cpu_time = current_cpu_load[0][5]
         cpu_percent_load_array = []
         amend_array = True
         for index,line in enumerate(current_cpu_load):
             #print(line)
             user_dif = line[0] - cpu_load_array[index][0]
             nice_dif = line[1] - cpu_load_array[index][1]
             system_dif = line[2] - cpu_load_array[index][2]
             idle_dif = line[3] - cpu_load_array[index][3]
             active_dif = line[4] - cpu_load_array[index][4]
             total_dif = line[5] - cpu_load_array[index][5]
             if(total_dif > 0):
                 user_pct = user_dif / total_dif
                 nice_pct = nice_dif / total_dif
                 system_pct = system_dif / total_dif
                 idle_pct = idle_dif / total_dif
                 active_pct = active_dif / total_dif
                 pct_line = [user_pct, nice_pct, system_pct, idle_pct, active_pct]
                 cpu_percent_load_array.append(pct_line)
             else: amend_array = False
         if amend_array: cpu_load_array = current_cpu_load
    return cpu_percent_load_array

def get_arm_clockspeed():
    cmd = "/opt/vc/bin/vcgencmd measure_clock arm"
    CSpeed = subprocess.check_output(cmd, shell = True )
    cspeed_str = (int(int(CSpeed.split(b"=")[1])/1000000))
    return cspeed_str

def get_gpu_temp():
    cmd = "/opt/vc/bin/vcgencmd measure_temp"
    GPUTemp = subprocess.check_output(cmd, shell = True )
    return (float(GPUTemp.split(b"=")[1].split(b"'")[0]))

def get_cpu_temp():
    cmd = "cat /sys/class/thermal/thermal_zone0/temp"
    CPUTemp = subprocess.check_output(cmd, shell = True )
    return (round(int(CPUTemp) / 1000,1))

def get_mem_usage():
    cmd = "free -m | awk 'NR==2{printf \"%s\\n%s\\n%.2f\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell = True ).splitlines()
    mem_used = int(MemUsage[0])
    mem_total = int(MemUsage[1])
    mem_used_pct = float(MemUsage[2])
    return [mem_used,mem_total,mem_used_pct]

def time_functions():
    print ("IP:      %s" % get_ip())
    print(timeit.timeit(stmt=get_ip, number=100) / .100)
    print ("LOAD:    %f " % get_cpu_load())
    print(timeit.timeit(stmt=get_cpu_load, number=100) / .10)
    #print ("TOP LOAD:%s %%" % get_cpu_load_using_top())
    #print(timeit.timeit(stmt=get_cpu_load_using_top, number=10) / .010)
    print ("CLOCK:   %d MHz" % get_arm_clockspeed())
    print(timeit.timeit(stmt=get_arm_clockspeed, number=100) / .100)
    print ("GPU:     %f C" % get_gpu_temp())
    print(timeit.timeit(stmt=get_gpu_temp, number=100) / .100)
    print ("CPU:     %f C" % get_cpu_temp())
    print(timeit.timeit(stmt=get_cpu_temp, number=100) / .100)
    print ("MEMORY:  %s " % get_mem_usage())
    print(timeit.timeit(stmt=get_mem_usage, number=100) / .100)
    print ("COMBINED:%s " % dynamic_values_to_csv())
    print(timeit.timeit(stmt=dynamic_values_to_csv, number = 20) / .02)


#Command line test [will run when display.py is run directly]
if __name__ == "__main__":
    time_functions()
    while True:
        print (dynamic_values_to_csv())
        time.sleep(0.5)
    os._exit(1)
