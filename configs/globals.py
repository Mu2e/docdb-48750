# parameters for modifying original map data
# thermal noise
noise = 0.3 # Gauss
noise_str = '_noise'+str(noise).replace('.', 'p')
# phony curled field
phony_curl = 20.0 # Gauss / m
phony_curl_str = f'_curlZ'+str(phony_curl).replace('-', 'm').replace('.', 'p')
# z0 offest (center of DS)
z0 = 9.033
