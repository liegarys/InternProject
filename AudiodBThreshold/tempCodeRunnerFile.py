        crossings = np.where((audio_data[:-1] < threshold_value) & (audio_data[1:] >= threshold_value) | 
                             (audio_data[:-1] >= threshold_value) & (audio_data[1:] < threshold_value))[0]
        crossing_times = time_array[crossings]
        crossing_values = audio_data[crossings]