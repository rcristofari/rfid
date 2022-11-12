import logging

# ----------------------------------------------------------------------------------------------------------------------#
def broadcast_detections(client, nmea_queue):
    while True:
        # get the data from the queue
        sentence = nmea_queue.get()
        # publish on MQTT
        if sentence:
            try:
                client.publish(f"detections/all", nmea)
            except:
                logging.exception("Unable to post to MQTT")  # This doesn't work. Use on_publish callback instead.

# ----------------------------------------------------------------------------------------------------------------------#
def broadcast_frequency(client, stream_queue, n_antennas, antenna_name, base_freq, refresh_frequency=1):
    global penguin_is_sleeping  # refer to the global variable that is manipulated by the TIRIS thread
    n_pulses, times = 0, []
    while True:
        # get the data from the queue
        data = stream_queue.get()
        if data:
            n_pulses += 1
            times.append(data[2])
        if n_pulses >= n_antennas * base_freq * refresh_frequency:  # this should be roughly 1 second: we refresh TIRIS detection frequencies
            freq = n_pulses / (max(times) - min(times))
            client.publish("status/all", f"$HERTZ,{antenna_name},{freq}")
            if freq < basefreq * 0.75 and not penguin_is_sleeping:
                logging.warning(
                    f"Actual detection frequency is too low - {freq / n_antennas} instead of {base_freq / n_antennas}")
            n_pulses, times = 0, []

# ----------------------------------------------------------------------------------------------------------------------#
def broadcast_detections_and_frequencies(client, dbcon, stream_queue, passage_names, locations, port_dict, refresh_frequency = 2):

    n_pulses = 0
    n_antennas = len(passage_names)
    freq_list = []

    while True:

        # get the data from the queue
        data = stream_queue.get()
        freq_list.append(data)

        # If the line contains a detection, format as NMEA and publish
        if data[0]:
            nmea = dbcon.nmea_sentence(data[3], data[2], passage_names[port_dict[data[1]]] + " " + locations[port_dict[data[1]]])
            try:
                client.publish("detections/" + passage_names[port_dict[data[1]]], nmea)
                client.publish("detections/all", nmea)
            except:
                logging.exception("Unable to post to MQTT")  # This doesn't work. Use on_publish callback instead.

        # In any case, if something was retrieved from the queue:
        if data:
            n_pulses += 1
        # this should be roughly 2 seconds, we refresh TIRIS detection frequencies
        if n_pulses >= n_antennas * 7 * refresh_frequency:
            pulse_times_per_antenna, n_pulses_per_antenna = [[]]*n_antennas, [0]*n_antennas
            for x in freq_list:
                antenna_id = port_dict[x[1]]
                pulse_times_per_antenna[antenna_id].append(x[2])
                n_pulses_per_antenna[antenna_id] += 1
            freqs = [round(n_pulses_per_antenna[i] / (max(pulse_times_per_antenna[i]) - min(pulse_times_per_antenna[i])), 2) for i in range(n_antennas)]
            freq_nmea = "$HERTZ,"+",".join([str(f) for f in freqs])
            client.publish("status/all", freq_nmea)
            print(f"Detection frequencies: {freqs}")
            n_pulses, freq_list = 0, []

# ----------------------------------------------------------------------------------------------------------------------#
def mqtt_on_connect(client, user_data, flags, rc):
    if rc == 0:
        logging.info("MQTT connexion to broker successful")
    else:
        logging.error(f"MQTT connexion to broker failed with code {rc}")

# ----------------------------------------------------------------------------------------------------------------------#
def mqtt_on_publish(client, user_data, mid):
    broker_is_alive = True
